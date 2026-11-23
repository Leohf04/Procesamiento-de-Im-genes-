import json
import pytest
import torch
from torch import nn
from torch.utils.data import DataLoader,TensorDataset
from src.urban_experiment_runner import evaluate_semantic,load_checkpoint,run_experiment,semantic_confusion_matrix

class Tiny(nn.Module):
    def __init__(self): super().__init__(); self.conv=nn.Conv2d(1,2,1)
    def forward(self,x): return {"out":self.conv(x)}

def make_loaders():
    ds=TensorDataset(torch.randn(4,1,4,4),torch.randint(0,2,(4,4,4)))
    return DataLoader(ds,batch_size=2),DataLoader(ds,batch_size=2)

def test_confusion_ignore_and_absent_class():
    cm=semantic_confusion_matrix(torch.tensor([[[0,1,1,0]]]),torch.tensor([[[0,1,0,255]]]),2)
    assert cm.tolist()==[[1,1],[0,1]]
    ds=DataLoader(TensorDataset(torch.randn(1,1,4,4),torch.zeros(1,4,4,dtype=torch.long)))
    report=evaluate_semantic(Tiny(),ds,2,torch.device("cpu"))
    assert report["support_per_class"]==[16,0] and report["iou_per_class"][1] is None

def test_runner_saves_metrics_and_checkpoints(tmp_path):
    tr,va=make_loaders(); model=Tiny(); opt=torch.optim.SGD(model.parameters(),lr=.01)
    cfg={"experiment_id":"unit-sem","dataset":"synthetic","max_epochs":2,"patience":2,"seed":7,"num_classes":2}
    r=run_experiment(model=model,train_loader=tr,validation_loader=va,task="semantic",optimizer=opt,
                     output_dir=tmp_path,config=cfg,device="cpu")
    assert r["status"]=="completed" and r["epochs_completed"]==2
    assert (tmp_path/"last.pt").is_file() and (tmp_path/"best.pt").is_file()
    assert len([json.loads(x) for x in (tmp_path/"metrics.jsonl").read_text().splitlines()])==2

def test_resume_rejects_config_hash_mismatch(tmp_path):
    tr,va=make_loaders(); model=Tiny(); opt=torch.optim.SGD(model.parameters(),lr=.01)
    cfg={"experiment_id":"resume","dataset":"synthetic","max_epochs":1,"num_classes":2}
    run_experiment(model=model,train_loader=tr,validation_loader=va,task="semantic",optimizer=opt,
                   output_dir=tmp_path,config=cfg,device="cpu")
    with pytest.raises(ValueError,match="config hash"):
        load_checkpoint(tmp_path/"last.pt",model,opt,expected_config_hash="wrong")

def test_instances_require_mask_ap_evaluator(tmp_path):
    tr,va=make_loaders(); model=Tiny(); opt=torch.optim.SGD(model.parameters(),lr=.01)
    with pytest.raises(ValueError,match="COCO evaluator"):
        run_experiment(model=model,train_loader=tr,validation_loader=va,task="instances",
            optimizer=opt,output_dir=tmp_path,config={"experiment_id":"det","dataset":"synthetic"},device="cpu")
