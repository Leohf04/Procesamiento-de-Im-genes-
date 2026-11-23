"""Reproducible per-domain urban training engine; test data is never consumed."""
from __future__ import annotations
import hashlib, json, os, random, tempfile, time
from pathlib import Path
from typing import Callable, Mapping
import numpy as np
import torch


def seed_everything(seed: int) -> None:
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    if torch.cuda.is_available(): torch.cuda.manual_seed_all(seed)


def semantic_confusion_matrix(prediction, target, num_classes: int, ignore_index: int = 255):
    if prediction.shape != target.shape: raise ValueError("prediction/target shape mismatch")
    p, t = prediction.reshape(-1).long(), target.reshape(-1).long()
    valid = (t != ignore_index) & (t >= 0) & (t < num_classes)
    if bool(((p[valid] < 0) | (p[valid] >= num_classes)).any()):
        raise ValueError("Predicted semantic IDs outside configured range")
    return torch.bincount(t[valid] * num_classes + p[valid],
                          minlength=num_classes * num_classes).reshape(num_classes, num_classes)


def semantic_metrics(confusion) -> dict:
    m = confusion.to(torch.float64); support=m.sum(1); tp=m.diag()
    denom=support+m.sum(0)-tp
    iou=torch.where(denom>0,tp/denom,torch.nan)
    acc=torch.where(support>0,tp/support,torch.nan)
    total=support.sum()
    return {"miou": float(torch.nanmean(iou)) if bool(torch.isfinite(iou).any()) else None,
            "pixel_accuracy": float(tp.sum()/total) if total>0 else None,
            "mean_accuracy": float(torch.nanmean(acc)) if bool(torch.isfinite(acc).any()) else None,
            "iou_per_class":[None if not torch.isfinite(x) else float(x) for x in iou],
            "accuracy_per_class":[None if not torch.isfinite(x) else float(x) for x in acc],
            "support_per_class":[int(x) for x in support],
            "confusion_matrix":confusion.long().cpu().tolist()}


def _move_targets(targets, device):
    return [{k:(v.to(device) if torch.is_tensor(v) else v) for k,v in t.items()} for t in targets]


def _atomic_save(payload, path: Path):
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix=path.name+".",suffix=".tmp",dir=path.parent); os.close(fd)
    try: torch.save(payload,tmp); os.replace(tmp,path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)


def _rng_state():
    s={"python":random.getstate(),"numpy":np.random.get_state(),"torch":torch.get_rng_state()}
    if torch.cuda.is_available(): s["cuda"]=torch.cuda.get_rng_state_all()
    return s


def _restore_rng(s):
    random.setstate(s["python"]); np.random.set_state(s["numpy"]); torch.set_rng_state(s["torch"])
    if torch.cuda.is_available() and "cuda" in s: torch.cuda.set_rng_state_all(s["cuda"])


def load_checkpoint(path, model, optimizer, scheduler=None, scaler=None,
                    expected_config_hash=None, map_location="cpu"):
    try: state=torch.load(path,map_location=map_location,weights_only=False)
    except TypeError: state=torch.load(path,map_location=map_location)
    if state.get("format_version")!=1: raise ValueError("Unsupported checkpoint format")
    if expected_config_hash and state.get("config_hash")!=expected_config_hash:
        raise ValueError("Checkpoint config hash differs; refusing unsafe resume")
    model.load_state_dict(state["model"]); optimizer.load_state_dict(state["optimizer"])
    if scheduler is not None and state.get("scheduler") is not None: scheduler.load_state_dict(state["scheduler"])
    if scaler is not None and state.get("scaler") is not None: scaler.load_state_dict(state["scaler"])
    _restore_rng(state["rng"]); return state


def _train_epoch(model, loader, optimizer, task, device, class_weights, ignore_index,
                 scaler, amp, max_grad_norm):
    model.train(); total=0.; batches=0
    for batch in loader:
        optimizer.zero_grad(set_to_none=True)
        if task=="semantic":
            images,masks=batch; images=images.to(device); masks=masks.to(device,dtype=torch.long)
            with torch.autocast(device_type=device.type,enabled=amp):
                logits=model(images)["out"]
                loss=torch.nn.functional.cross_entropy(logits,masks,
                    weight=class_weights.to(device) if class_weights is not None else None,
                    ignore_index=ignore_index)
        else:
            images,targets=batch; images=[x.to(device) for x in images]; targets=_move_targets(targets,device)
            with torch.autocast(device_type=device.type,enabled=amp):
                losses=model(images,targets)
                if not isinstance(losses,Mapping) or not losses: raise RuntimeError("Detection model returned no losses")
                if any(x.ndim!=0 or not bool(torch.isfinite(x)) for x in losses.values()):
                    raise FloatingPointError("Non-finite detection loss")
                loss=sum(losses.values())
        if loss.ndim!=0 or not bool(torch.isfinite(loss)): raise FloatingPointError("Non-finite training loss")
        if scaler is not None and scaler.is_enabled():
            scaler.scale(loss).backward(); scaler.unscale_(optimizer)
            if max_grad_norm: torch.nn.utils.clip_grad_norm_(model.parameters(),max_grad_norm)
            scaler.step(optimizer); scaler.update()
        else:
            loss.backward()
            if max_grad_norm: torch.nn.utils.clip_grad_norm_(model.parameters(),max_grad_norm)
            optimizer.step()
        total+=float(loss.detach().cpu()); batches+=1
    if not batches: raise RuntimeError("Training loader yielded zero batches")
    return total/batches,batches


@torch.no_grad()
def evaluate_semantic(model, loader, num_classes, device, ignore_index=255):
    model.eval(); cm=torch.zeros((num_classes,num_classes),dtype=torch.int64); batches=0
    for images,masks in loader:
        logits=model(images.to(device))["out"]
        if logits.ndim!=4 or logits.shape[1]!=num_classes: raise ValueError("Unexpected semantic logits shape")
        cm+=semantic_confusion_matrix(logits.argmax(1).cpu(),masks.cpu(),num_classes,ignore_index)
        batches+=1
    if not batches: raise RuntimeError("Validation loader yielded zero batches")
    result=semantic_metrics(cm); result["validation_batches"]=batches; return result


def run_experiment(*, model, train_loader, validation_loader, task: str, optimizer,
                   output_dir, config: Mapping, class_weights=None, scheduler=None,
                   detection_evaluator: Callable|None=None, resume_from=None, device=None):
    """Run one domain only. Instance mode requires a validated evaluator returning mask_ap."""
    if task not in {"semantic","instances"}: raise ValueError("task must be semantic or instances")
    if task=="instances" and detection_evaluator is None:
        raise ValueError("Instance training requires a validated COCO evaluator; Mask AP will not be guessed")
    if train_loader is validation_loader: raise ValueError("Train and validation loaders must be distinct")
    if not config.get("experiment_id") or not config.get("dataset"): raise ValueError("experiment_id and dataset are required")
    max_epochs=int(config.get("max_epochs",5)); patience=int(config.get("patience",2))
    max_seconds=float(config.get("max_seconds",5400)); delta=float(config.get("min_delta",0))
    if max_epochs<1 or patience<1 or max_seconds<=0: raise ValueError("Invalid run limits")
    seed=int(config.get("seed",2026)); seed_everything(seed)
    device=torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu")); model.to(device)
    amp=bool(config.get("amp",False) and device.type=="cuda")
    scaler=torch.cuda.amp.GradScaler(enabled=amp) if device.type=="cuda" else None
    cfg_hash=hashlib.sha256(json.dumps(dict(config),sort_keys=True,separators=(",",":")).encode()).hexdigest()
    out=Path(output_dir); out.mkdir(parents=True,exist_ok=True)
    metrics_file=out/"metrics.jsonl"; last=out/"last.pt"; best=out/"best.pt"
    start=steps=bad=0; best_metric=None
    if resume_from:
        state=load_checkpoint(resume_from,model,optimizer,scheduler,scaler,cfg_hash,device)
        start=int(state["epoch"]); steps=int(state["global_step"]); bad=int(state["bad_epochs"]); best_metric=state["best_metric"]
    meta={"experiment_id":config["experiment_id"],"dataset":config["dataset"],"task":task,
          "seed":seed,"config_hash":cfg_hash,"device":str(device),"torch":torch.__version__}
    started=time.monotonic(); history=[]
    for epoch in range(start,max_epochs):
        if time.monotonic()-started>=max_seconds: break
        train_loss,n=_train_epoch(model,train_loader,optimizer,task,device,class_weights,
            int(config.get("ignore_index",255)),scaler,amp,config.get("max_grad_norm"))
        steps+=n
        if task=="semantic":
            val=evaluate_semantic(model,validation_loader,int(config["num_classes"]),device,int(config.get("ignore_index",255)))
            metric=val["miou"]
        else:
            model.eval(); val=dict(detection_evaluator(model,validation_loader,device)); metric=val.get("mask_ap")
            if not isinstance(metric,(int,float)) or not np.isfinite(metric):
                raise ValueError("Evaluator must return finite numeric mask_ap from validated COCOeval")
        if metric is None or not np.isfinite(metric): raise ValueError("Undefined primary validation metric")
        if scheduler:
            if isinstance(scheduler,torch.optim.lr_scheduler.ReduceLROnPlateau): scheduler.step(float(metric))
            else: scheduler.step()
        improved=best_metric is None or float(metric)>float(best_metric)+delta
        if improved: best_metric=float(metric); bad=0
        else: bad+=1
        row={"epoch":epoch+1,"global_step":steps,"train_loss":train_loss,"train_batches":n,
             "validation":val,"primary_metric":float(metric),"best_metric":best_metric,
             "learning_rates":[g["lr"] for g in optimizer.param_groups],
             "elapsed_seconds":round(time.monotonic()-started,3)}
        with metrics_file.open("a",encoding="utf-8") as f:
            f.write(json.dumps(row,ensure_ascii=False,allow_nan=False)+"\n")
        history.append(row)
        payload={"format_version":1,"model":model.state_dict(),"optimizer":optimizer.state_dict(),
            "scheduler":scheduler.state_dict() if scheduler else None,
            "scaler":scaler.state_dict() if scaler else None,"epoch":epoch+1,
            "global_step":steps,"best_metric":best_metric,"bad_epochs":bad,
            "rng":_rng_state(),"config_hash":cfg_hash,"metadata":meta}
        _atomic_save(payload,last)
        if improved: _atomic_save(payload,best)
        if bad>=patience or time.monotonic()-started>=max_seconds: break
    return {"status":"completed" if history else "no_epoch_completed",
        "experiment_id":config["experiment_id"],"dataset":config["dataset"],"task":task,
        "config_hash":cfg_hash,"epochs_completed":len(history),"global_step":steps,
        "best_metric":best_metric,"last_checkpoint":str(last) if last.exists() else None,
        "best_checkpoint":str(best) if best.exists() else None,"metrics_file":str(metrics_file),
        "history":history,"test_evaluated":False}
