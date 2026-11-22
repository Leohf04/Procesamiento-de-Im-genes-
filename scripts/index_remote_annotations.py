#!/usr/bin/env python3
"""Build per-image annotation statistics from remote A2D2 and UrbanSyn manifests."""
from __future__ import annotations
import argparse, json, io
from collections import Counter
from pathlib import Path
import numpy as np
from PIL import Image
from src.data_adapters import (decode_a2d2_instances, decode_a2d2_semantic,
    decode_urbansyn_panoptic, decode_urbansyn_semantic, load_a2d2_class_list,
    normalize_class_name)
from src.urban_ontology import (load_urban_ontology, source_instance_map,
    source_semantic_map, semantic_name_to_id, instance_name_to_id)

A2D2_BUCKET="audi-autonomous-driving-dataset"
A2D2_REGION="eu-central-1"
URBANSYN_REPO="UrbanSyn/UrbanSyn"
SPLITS=("train","val","test")

def read_jsonl(path):
    rows=[]
    with path.open(encoding="utf-8") as f:
        for n,line in enumerate(f,1):
            if line.strip():
                try: rows.append(json.loads(line))
                except json.JSONDecodeError as e: raise ValueError(f"{path}:{n}: invalid JSON") from e
    ids=[str(x.get("sample_id","")) for x in rows]
    if any(not x for x in ids) or len(ids)!=len(set(ids)): raise ValueError(f"{path}: missing/duplicate sample_id")
    return rows

def class_pixel_counts(mask,id_to_name,ignore_index=255):
    ids,counts=np.unique(mask,return_counts=True); out={}
    for cid,count in zip(ids,counts):
        name=id_to_name.get(int(cid))
        if name is not None and int(cid)!=ignore_index and int(count)>0: out[name]=int(count)
    return dict(sorted(out.items()))

def instance_counts(decoded,id_to_name):
    counts=Counter()
    for label in decoded["labels"]:
        if int(label) in id_to_name: counts[id_to_name[int(label)]]+=1
    return dict(sorted(counts.items()))

def summarize_a2d2_mask(mask,color_to_name,semantic_map,instance_map):
    rgb=np.asarray(mask.convert("RGB") if isinstance(mask,Image.Image) else mask)
    sem=decode_a2d2_semantic(rgb,color_to_name,semantic_map)
    inst=decode_a2d2_instances(rgb,color_to_name,instance_map,min_component_area=8)
    return {"semantic_pixels":class_pixel_counts(sem,{int(v):k for k,v in semantic_map.items()}),
            "instance_counts":instance_counts(inst,{int(v):k for k,v in instance_map.items()})}

def summarize_urbansyn_masks(semantic_mask,panoptic_mask,semantic_map,instance_map):
    sem=decode_urbansyn_semantic(semantic_mask,semantic_map)
    inst=decode_urbansyn_panoptic(panoptic_mask,instance_map,min_instance_area=1)
    return {"semantic_pixels":class_pixel_counts(sem,{int(v):k for k,v in semantic_name_to_id().items()}),
            "instance_counts":instance_counts(inst,{int(v):k for k,v in instance_name_to_id().items()})}

def open_array(path):
    with Image.open(path) as im: return np.asarray(im).copy()

def write_jsonl(path,rows):
    tmp=path.with_suffix(path.suffix+".tmp")
    with tmp.open("w",encoding="utf-8") as f:
        for row in rows: f.write(json.dumps(row,sort_keys=True,ensure_ascii=False)+"\n")
    tmp.replace(path)

def split_summary(rows,filename):
    sem_frames=Counter(); inst_totals=Counter()
    for row in rows:
        sem_frames.update(row["semantic_pixels"].keys())
        inst_totals.update(row["instance_counts"])
    return {"samples":len(rows),"annotation_index":filename,
            "semantic_class_frame_coverage":dict(sorted(sem_frames.items())),
            "instance_object_counts":dict(sorted(inst_totals.items()))}

def index_a2d2(manifest_dir,output_dir,s3=None):
    import boto3
    from botocore import UNSIGNED
    from botocore.config import Config
    if s3 is None:
        s3=boto3.client("s3",region_name=A2D2_REGION,config=Config(signature_version=UNSIGNED,retries={"max_attempts":5}))
    response=s3.get_object(Bucket=A2D2_BUCKET,Key="camera_lidar_semantic/class_list.json")
    color_map=load_a2d2_class_list(json.loads(response["Body"].read()))
    ontology=load_urban_ontology()
    semantic_map={normalize_class_name(k):int(v) for k,v in ontology["semantic"]["sources"]["a2d2_normalized_name_to_semantic_id"].items()}
    instance_map={normalize_class_name(k):int(v) for k,v in ontology["instances"]["sources"]["a2d2_normalized_name_to_instance_id"].items()}
    output_dir.mkdir(parents=True,exist_ok=True)
    summary={"dataset":"a2d2","splits":{},"class_list_entries":len(color_map)}
    prefix=f"s3://{A2D2_BUCKET}/"
    for split in SPLITS:
        manifest=read_jsonl(manifest_dir/f"a2d2_{split}.jsonl"); rows=[]
        for i,record in enumerate(manifest,1):
            uri=record["assets"]["semantic"]
            if not uri.startswith(prefix): raise ValueError(f"Unexpected A2D2 URI: {uri}")
            try:
                payload=s3.get_object(Bucket=A2D2_BUCKET,Key=uri[len(prefix):])["Body"].read()
                with Image.open(io.BytesIO(payload)) as im: stats=summarize_a2d2_mask(im,color_map,semantic_map,instance_map)
            except Exception as exc: raise RuntimeError(f"A2D2 {split} {record['sample_id']}: {exc}") from exc
            rows.append({"sample_id":str(record["sample_id"]),"annotation_status":"ok",
                         "semantic_pixels":stats["semantic_pixels"],"instance_counts":stats["instance_counts"]})
            if i%100==0: print(f"A2D2 {split}: {i}/{len(manifest)}",flush=True)
        filename=f"a2d2_{split}.annotations.jsonl"; write_jsonl(output_dir/filename,rows)
        summary["splits"][split]=split_summary(rows,filename)
    (output_dir/"a2d2_annotation_index_summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    return summary

def index_urbansyn(manifest_dir,output_dir,downloader=None):
    from huggingface_hub import hf_hub_download
    downloader=downloader or hf_hub_download
    ontology=load_urban_ontology(); sem_map=source_semantic_map("urbansyn",ontology); inst_map=source_instance_map("urbansyn",ontology)
    output_dir.mkdir(parents=True,exist_ok=True)
    summary={"dataset":"urbansyn","splits":{},"repository":URBANSYN_REPO}
    for split in SPLITS:
        manifest=read_jsonl(manifest_dir/f"urbansyn_{split}.jsonl"); rows=[]
        for i,record in enumerate(manifest,1):
            try:
                common={"repo_id":URBANSYN_REPO,"repo_type":"dataset","revision":record["revision"]}
                sem_path=downloader(**common,filename=record["assets"]["semantic"])
                pan_path=downloader(**common,filename=record["assets"]["panoptic"])
                sem,pan=open_array(sem_path),open_array(pan_path)
                if sem.shape[:2]!=pan.shape[:2]: raise ValueError(f"sem/pan shape mismatch {sem.shape} vs {pan.shape}")
                stats=summarize_urbansyn_masks(sem,pan,sem_map,inst_map)
            except Exception as exc: raise RuntimeError(f"UrbanSyn {split} {record['sample_id']}: {exc}") from exc
            rows.append({"sample_id":str(record["sample_id"]),"annotation_status":"ok",
                         "semantic_pixels":stats["semantic_pixels"],"instance_counts":stats["instance_counts"]})
            if i%100==0: print(f"UrbanSyn {split}: {i}/{len(manifest)}",flush=True)
        filename=f"urbansyn_{split}.annotations.jsonl"; write_jsonl(output_dir/filename,rows)
        summary["splits"][split]=split_summary(rows,filename)
    (output_dir/"urbansyn_annotation_index_summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    return summary

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest-dir",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,default=Path("artifacts/annotation_index"))
    p.add_argument("--dataset",choices=("a2d2","urbansyn","both"),default="both")
    a=p.parse_args(); results=[]
    if a.dataset in ("a2d2","both"): results.append(index_a2d2(a.manifest_dir,a.output_dir))
    if a.dataset in ("urbansyn","both"): results.append(index_urbansyn(a.manifest_dir,a.output_dir))
    print(json.dumps(results,indent=2,ensure_ascii=False))
if __name__=="__main__": main()
