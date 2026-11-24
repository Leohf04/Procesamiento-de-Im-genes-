#!/usr/bin/env python3
"""Run real-data smoke tests for all four manifest-backed urban loaders.

Only one deterministic record per split and dataset is downloaded to temporary
runner storage. No source data is written to the repository or uploaded.
"""
from __future__ import annotations
import argparse, hashlib, json, tempfile, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from urllib.parse import urlparse

import boto3
from botocore import UNSIGNED
from botocore.config import Config
from huggingface_hub import hf_hub_download
import numpy as np
from PIL import Image
import torch
from torch.utils.data import DataLoader

from src.data_adapters import (
    A2D2InstanceDataset, A2D2SemanticDataset, UrbanSynInstanceDataset,
    UrbanSynSemanticDataset, DEFAULT_CANONICAL_CLASSES, load_a2d2_class_list,
    detection_collate_fn,
)
from src.urban_ontology import (
    instance_name_to_id, load_urban_ontology, semantic_name_to_id,
    source_instance_map, source_semantic_map,
)

SPLITS=("train","val","test")


def rows(path):
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]


def choose(records, split):
    return min(records, key=lambda r: hashlib.sha256(
        f"real-loader-smoke-2026:{r['sample_id']}".encode()).hexdigest())


def download_a2d2(s3, uri, dest):
    parsed=urlparse(uri)
    if parsed.scheme!="s3":
        raise ValueError(f"Expected S3 URI: {uri}")
    s3.download_file(parsed.netloc, parsed.path.lstrip("/"), str(dest))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--manifest-dir",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--size",type=int,default=512)
    args=ap.parse_args()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    s3=boto3.client("s3",region_name="eu-central-1",
        config=Config(signature_version=UNSIGNED,retries={"max_attempts":5}))
    class_raw=json.loads(s3.get_object(Bucket="audi-autonomous-driving-dataset",
        Key="camera_lidar_semantic/class_list.json")["Body"].read())
    color_map=load_a2d2_class_list(class_raw)
    ontology=load_urban_ontology()
    semantic_ids=semantic_name_to_id(ontology)
    instance_ids=instance_name_to_id(ontology)
    urban_semantic_map=source_semantic_map("urbansyn",ontology)
    urban_instance_map=source_instance_map("urbansyn",ontology)
    report={"sampled_per_split":1,"datasets":{},"status":"running"}
    with tempfile.TemporaryDirectory(prefix="urban-real-loader-") as tmp:
        root=Path(tmp)
        for dataset in ("a2d2","urbansyn"):
            details={}
            for split in SPLITS:
                manifest=rows(args.manifest_dir/f"{dataset}_{split}.jsonl")
                row=choose(manifest,split)
                local=root/dataset/split
                local.mkdir(parents=True)
                paths={}
                if dataset=="a2d2":
                    for key in ("rgb","semantic"):
                        p=local/f"{key}.png"
                        download_a2d2(s3,row["assets"][key],p)
                        paths[key]=p
                    sem_records=[{"sample_id":row["sample_id"],"dataset":dataset,"image":str(paths["rgb"]),"semantic":str(paths["semantic"])}]
                    inst_records=[{"sample_id":row["sample_id"],"dataset":dataset,"image":str(paths["rgb"]),"instance":str(paths["semantic"])}]
                    sem_ds=A2D2SemanticDataset(sem_records,color_map,semantic_ids,size=(args.size,args.size))
                    inst_ds=A2D2InstanceDataset(inst_records,color_map,instance_ids,size=(args.size,args.size),min_component_area=4)
                else:
                    for key in ("rgb","semantic","panoptic","bbox"):
                        p=hf_hub_download(repo_id="UrbanSyn/UrbanSyn",repo_type="dataset",
                            revision=row["revision"],filename=row["assets"][key],
                            local_dir=str(local/"hf"))
                        paths[key]=Path(p)
                    sem_records=[{"sample_id":row["sample_id"],"dataset":dataset,"image":str(paths["rgb"]),"semantic":str(paths["semantic"])}]
                    inst_records=[{"sample_id":row["sample_id"],"dataset":dataset,"image":str(paths["rgb"]),"panoptic":str(paths["panoptic"])}]
                    sem_ds=UrbanSynSemanticDataset(sem_records,urban_semantic_map,size=(args.size,args.size))
                    inst_ds=UrbanSynInstanceDataset(inst_records,urban_instance_map,size=(args.size,args.size),min_instance_area=4)
                    bbox=json.loads(paths["bbox"].read_text())
                    if isinstance(bbox,list): bbox_count=len(bbox)
                    elif isinstance(bbox,dict):
                        bbox_count=next((len(bbox[k]) for k in ("objects","annotations","bboxes","boxes","labels","instances") if isinstance(bbox.get(k),list)),None)
                    else: bbox_count=None
                image,semantic=sem_ds[0]
                images,targets=next(iter(DataLoader(inst_ds,batch_size=1,collate_fn=detection_collate_fn)))
                target=targets[0]
                assert image.shape==(3,args.size,args.size)
                assert semantic.shape==(args.size,args.size)
                assert torch.isfinite(image).all()
                assert set(target)=={"boxes","labels","masks","image_id","area","iscrowd"}
                assert target["boxes"].ndim==2 and target["boxes"].shape[1]==4
                assert target["masks"].ndim==3 and target["masks"].shape[1:]==(args.size,args.size)
                assert len(target["labels"])==len(target["boxes"])==len(target["masks"])
                assert torch.isfinite(target["boxes"]).all()
                if len(target["boxes"]):
                    assert (target["boxes"][:,2:]>=target["boxes"][:,:2]).all()
                    assert (target["boxes"][:,2:]<=args.size).all()
                item={"sample_id":row["sample_id"],"semantic_shape":list(semantic.shape),
                    "semantic_ids":sorted(int(x) for x in torch.unique(semantic).tolist()),
                    "instance_count":int(len(target["labels"])),
                    "instance_labels":sorted(int(x) for x in torch.unique(target["labels"]).tolist()),
                    "boxes_shape":list(target["boxes"].shape),"masks_shape":list(target["masks"].shape)}
                if dataset=="urbansyn": item["bbox_json_records"]=bbox_count
                details[split]=item
            report["datasets"][dataset]=details
    report["status"]="PASS"
    args.output.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
    print("RESULT: REAL MANIFEST LOADER SMOKE TEST PASSED")

if __name__=="__main__": main()
