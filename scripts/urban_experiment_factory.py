"""Factory for one local A2D2/UrbanSyn experiment (train + validation only)."""
import json
from pathlib import Path
import torch
from torch.utils.data import DataLoader
from src.data_adapters import (A2D2SemanticDataset,A2D2InstanceDataset,
    UrbanSynSemanticDataset,UrbanSynInstanceDataset,detection_collate_fn,load_a2d2_class_list)
from src.urban_ontology import load_urban_ontology,semantic_name_to_id,instance_name_to_id,source_semantic_map,source_instance_map
from src.urban_training import build_urban_train_loader
from src.urban_optimizer import build_optimizer_and_scheduler
from src.urban_coco_evaluator import evaluate_coco_instance_segmentation
from src.urban_experiment_runner import seed_everything

def _jsonl(path):
    with Path(path).open(encoding="utf-8") as f: return [json.loads(x) for x in f if x.strip()]

def create_experiment(config):
    ds=config["dataset"]; task=config["task"]
    if ds not in {"a2d2","urbansyn"} or task not in {"semantic","instances"}:
        raise ValueError("dataset/task must be a2d2|urbansyn and semantic|instances")
    seed_everything(int(config.get("seed",2026)))
    root=Path(config["data_dir"]); manifest=root/"local_manifests"; index=Path(config["annotation_index_dir"])
    ontology=load_urban_ontology(); semantic_ids=semantic_name_to_id(ontology); instance_ids=instance_name_to_id(ontology)
    mapping=semantic_ids if task=="semantic" else instance_ids
    size=int(config.get("image_size",512)); batch=int(config.get("batch_size",1)); workers=int(config.get("num_workers",0))
    rows={s:_jsonl(manifest/f"{ds}_{s}.jsonl") for s in ("train","val")}
    annotations={s:_jsonl(index/f"{ds}_{s}.annotations.jsonl") for s in ("train","val")}
    for split in ("train","val"):
        ids=[str(x["sample_id"]) for x in rows[split]]
        ann_ids=[str(x["sample_id"]) for x in annotations[split]]
        if len(ann_ids)!=len(set(ann_ids)) or set(ids)!=set(ann_ids):
            raise ValueError(f"{ds}/{split}: local manifest and annotation index IDs differ")
        ann_by_id={str(x["sample_id"]):x for x in annotations[split]}
        annotations[split]=[ann_by_id[sid] for sid in ids]
        if any(x.get("annotation_status","ok")!="ok" for x in annotations[split]):
            raise ValueError(f"{ds}/{split}: annotation_status not ok")
    train_ids={x["sample_id"] for x in rows["train"]}
    val_ids={x["sample_id"] for x in rows["val"]}
    if train_ids & val_ids: raise ValueError("Train/validation sample_id leakage")
    if ds=="a2d2":
        cmap=load_a2d2_class_list(root/"a2d2"/"class_list.json")
        if task=="semantic":
            train_ds=A2D2SemanticDataset(rows["train"],cmap,semantic_ids,(size,size))
            val_ds=A2D2SemanticDataset(rows["val"],cmap,semantic_ids,(size,size))
        else:
            train_ds=A2D2InstanceDataset(rows["train"],cmap,instance_ids,(size,size))
            val_ds=A2D2InstanceDataset(rows["val"],cmap,instance_ids,(size,size))
    else:
        local_rows={split:[{**row,"image":row["rgb"]} for row in rows[split]] for split in ("train","val")}
        if task=="semantic":
            source=source_semantic_map("urbansyn",ontology)
            train_ds=UrbanSynSemanticDataset(local_rows["train"],source,(size,size))
            val_ds=UrbanSynSemanticDataset(local_rows["val"],source,(size,size))
        else:
            source=source_instance_map("urbansyn",ontology)
            train_ds=UrbanSynInstanceDataset(local_rows["train"],source,(size,size))
            val_ds=UrbanSynInstanceDataset(local_rows["val"],source,(size,size))
    train_rows=[dict(x,dataset=ds,split="train") for x in annotations["train"]]
    train_loader,weights=build_urban_train_loader(train_ds,train_rows,task=task,class_to_id=mapping,
        batch_size=batch,num_workers=workers,seed=int(config.get("seed",2026)),
        pin_memory=torch.cuda.is_available())
    val_batch=int(config.get("validation_batch_size",1))
    val_loader=DataLoader(val_ds,batch_size=val_batch,shuffle=False,num_workers=workers,
        pin_memory=torch.cuda.is_available(),collate_fn=detection_collate_fn if task=="instances" else None)
    if task=="semantic":
        from src.models.deeplabv3plus import DeepLabV3Plus
        model=DeepLabV3Plus(num_classes=len(semantic_ids),pretrained_backbone=False)
        num_classes=len(semantic_ids)
        if int(config.get("num_classes",num_classes)) != num_classes:
            raise ValueError("num_classes does not match urban-v1 semantic ontology")
    else:
        import torchvision
        from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
        from torchvision.models.detection.mask_rcnn import MaskRCNNPredictor
        model=torchvision.models.detection.maskrcnn_resnet50_fpn(weights=None,weights_backbone=None,
            min_size=size,max_size=size)
        bf=model.roi_heads.box_predictor.cls_score.in_features
        model.roi_heads.box_predictor=FastRCNNPredictor(bf,len(instance_ids)+1)
        mf=model.roi_heads.mask_predictor.conv5_mask.in_channels
        model.roi_heads.mask_predictor=MaskRCNNPredictor(mf,256,len(instance_ids)+1)
        num_classes=len(instance_ids)+1
    optimizer, scheduler = build_optimizer_and_scheduler(model, task, config)
    evaluator=None
    if task=="instances":
        evaluator=lambda m,l,d:evaluate_coco_instance_segmentation(m,l,d,{v:k for k,v in instance_ids.items()})
    return {"model":model,"train_loader":train_loader,"validation_loader":val_loader,
        "optimizer":optimizer,"scheduler":scheduler,"class_weights":weights,"task":task,
        "detection_evaluator":evaluator}
