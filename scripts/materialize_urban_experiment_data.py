#!/usr/bin/env python3
"""Materialize only train/val RGB and labels on the remote runtime (never test)."""
import argparse, hashlib, json
from pathlib import Path
from urllib.parse import urlparse
import boto3
from botocore import UNSIGNED
from botocore.config import Config
from huggingface_hub import hf_hub_download

A2D2_BUCKET="audi-autonomous-driving-dataset"
HF_REPO="UrbanSyn/UrbanSyn"

def read_jsonl(path):
    with Path(path).open(encoding="utf-8") as f: return [json.loads(x) for x in f if x.strip()]

def write_jsonl(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8") as f:
        for row in rows: f.write(json.dumps(row,ensure_ascii=False,sort_keys=True)+"\n")

def download_s3(client,uri,dest):
    u=urlparse(uri)
    if u.scheme!="s3" or u.netloc!=A2D2_BUCKET: raise ValueError(f"Unexpected A2D2 URI: {uri}")
    dest.parent.mkdir(parents=True,exist_ok=True)
    if not dest.is_file(): client.download_file(u.netloc,u.path.lstrip("/"),str(dest))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest-dir",type=Path,required=True)
    p.add_argument("--annotation-index-dir",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args()
    s3=boto3.client("s3",region_name="eu-central-1",
        config=Config(signature_version=UNSIGNED,retries={"max_attempts":5}))
    class_path=a.output_dir/"a2d2"/"class_list.json"; class_path.parent.mkdir(parents=True,exist_ok=True)
    if not class_path.exists():
        obj=s3.get_object(Bucket=A2D2_BUCKET,Key="camera_lidar_semantic/class_list.json")
        class_path.write_bytes(obj["Body"].read())
    summary=[]
    for ds in ("a2d2","urbansyn"):
      for split in ("train","val"):
        manifests=read_jsonl(a.manifest_dir/f"{ds}_{split}.jsonl")
        annotations=read_jsonl(a.annotation_index_dir/f"{ds}_{split}.annotations.jsonl")
        ann_ids=[str(x.get("sample_id","")) for x in annotations]
        ids=[str(x.get("sample_id","")) for x in manifests]
        if not ids or len(ids)!=len(set(ids)) or set(ids)!=set(ann_ids) or len(ann_ids)!=len(set(ann_ids)):
            raise RuntimeError(f"{ds}/{split}: manifest/index IDs missing, duplicate or mismatched")
        ann_map={str(x["sample_id"]):x for x in annotations}
        if any(ann_map[x].get("annotation_status","ok")!="ok" for x in ids):
            raise RuntimeError(f"{ds}/{split}: annotations contain non-ok rows")
        local=[]
        for row in manifests:
            sid=str(row["sample_id"]); key=hashlib.sha256(sid.encode()).hexdigest()[:20]
            folder=a.output_dir/ds/split/key
            assets=row.get("assets",{})
            if ds=="a2d2":
                image=folder/"rgb.png"; semantic=folder/"semantic.png"
                download_s3(s3,assets["rgb"],image); download_s3(s3,assets["semantic"],semantic)
                record={"sample_id":sid,"dataset":ds,"image":str(image),"semantic":str(semantic),"instance":str(semantic)}
            else:
                rev=row.get("revision")
                if not rev: raise ValueError(f"UrbanSyn {sid}: pinned revision missing")
                paths={}
                for name in ("rgb","semantic","panoptic"):
                    paths[name]=Path(hf_hub_download(repo_id=HF_REPO,repo_type="dataset",
                        revision=rev,filename=assets[name],local_dir=str(folder/"hf")))
                record={"sample_id":sid,"dataset":ds,**{k:str(v) for k,v in paths.items()}}
            local.append(record)
        write_jsonl(a.output_dir/"local_manifests"/f"{ds}_{split}.jsonl",local)
        summary.append({"dataset":ds,"split":split,"samples":len(local),"materialized_assets":True})
    report={"status":"PASS","splits_materialized":["train","val"],"test_touched":False,
            "datasets":summary,"output_dir":str(a.output_dir)}
    (a.output_dir/"materialization_report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))
if __name__=="__main__": main()
