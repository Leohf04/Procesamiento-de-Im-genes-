#!/usr/bin/env python3
"""Guarded CLI. A project factory builds local train/validation loaders; test is never passed."""
import argparse, importlib, json
from pathlib import Path
from src.urban_experiment_runner import run_experiment

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config",type=Path,required=True)
    p.add_argument("--factory",required=True,help="module:function returning model, train_loader, validation_loader, optimizer, task")
    p.add_argument("--output-dir",type=Path,required=True); p.add_argument("--resume",type=Path)
    p.add_argument("--execute",action="store_true")
    a=p.parse_args(); cfg=json.loads(a.config.read_text(encoding="utf-8"))
    if cfg.get("run_training") is not True or not a.execute:
        raise SystemExit("BLOCKED: config run_training must be true AND --execute must be supplied.")
    module,name=a.factory.split(":",1); bundle=getattr(importlib.import_module(module),name)(cfg)
    required={"model","train_loader","validation_loader","optimizer","task"}
    if required-set(bundle): raise ValueError(f"Factory missing: {sorted(required-set(bundle))}")
    result=run_experiment(model=bundle["model"],train_loader=bundle["train_loader"],
        validation_loader=bundle["validation_loader"],optimizer=bundle["optimizer"],
        task=bundle["task"],output_dir=a.output_dir,config=cfg,
        class_weights=bundle.get("class_weights"),scheduler=bundle.get("scheduler"),
        detection_evaluator=bundle.get("detection_evaluator"),resume_from=a.resume,
        device=bundle.get("device"))
    print(json.dumps(result,indent=2,ensure_ascii=False))
if __name__=="__main__": main()
