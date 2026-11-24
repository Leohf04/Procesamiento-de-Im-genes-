import json
import pytest
import torch
from torch import nn
from torch.utils.data import DataLoader,TensorDataset
from src.urban_experiment_runner import evaluate_semantic,load_checkpoint,run_experiment,semantic_confusion_matrix,semantic_metrics

class Tiny(nn.Module):
    def __init__(self): super().__init__(); self.conv=nn.Conv2d(1,2,1)
    def forward(self,x): return {"out":self.conv(x)}

def make_loaders():
    ds=TensorDataset(torch.randn(4,1,4,4),torch.randint(0,2,(4,4,4)))
    return DataLoader(ds,batch_size=2,generator=torch.Generator().manual_seed(17)),DataLoader(ds,batch_size=2)

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
    saved=torch.load(tmp_path/"last.pt",map_location="cpu",weights_only=False)
    assert "loader_generator" in saved["loader_rng"]
    tr.generator.manual_seed(999)
    load_checkpoint(tmp_path/"last.pt",model,opt,expected_config_hash=r["config_hash"],train_loader=tr)
    assert torch.equal(tr.generator.get_state(),saved["loader_rng"]["loader_generator"])

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


class TinyDetector(nn.Module):
    def __init__(self):
        super().__init__()
        self.weight=nn.Parameter(torch.tensor(1.0))
    def forward(self,images,targets=None):
        if self.training:
            return {"loss_classifier":self.weight.square(),
                    "loss_mask":(self.weight*2).square()}
        return [{"boxes":torch.zeros((0,4)),"labels":torch.zeros((0,),dtype=torch.long),
                 "scores":torch.zeros((0,)),"masks":torch.zeros((0,1,4,4))} for _ in images]

def test_instance_loop_logs_individual_loss_components(tmp_path):
    model=TinyDetector()
    optimizer=torch.optim.SGD(model.parameters(),lr=.01)
    batch=([torch.zeros((3,4,4))],[{"boxes":torch.tensor([[0.,0.,2.,2.]]),
        "labels":torch.tensor([1]),"masks":torch.ones((1,4,4),dtype=torch.uint8),
        "image_id":torch.tensor([1]),"area":torch.tensor([4.]),"iscrowd":torch.tensor([0])}])
    train=[batch]; validation=[batch]
    result=run_experiment(model=model,train_loader=train,validation_loader=validation,
        task="instances",optimizer=optimizer,output_dir=tmp_path,
        config={"experiment_id":"unit-det","dataset":"synthetic","max_epochs":1,"patience":1},
        detection_evaluator=lambda m,l,d:{"mask_ap":0.5,"box_ap":0.6},device="cpu")
    losses=result["history"][0]["train_loss"]
    assert set(losses["components"])=={"loss_classifier","loss_mask"}


def test_iou_absent_ground_truth_class_is_undefined_even_with_false_positives():
    # Filas = clase GT y columnas = clase predicha. Clase 1 no aparece en GT,
    # pero hay 3 falsos positivos de clase 1 sobre píxeles GT de clase 0.
    cm=torch.tensor([[4,3],[0,0]],dtype=torch.int64)
    report=semantic_metrics(cm)
    assert report["support_per_class"]==[7,0]
    assert report["iou_per_class"][1] is None
    assert report["miou"]==pytest.approx(4/7)
    assert report["accuracy_per_class"][1] is None


def test_runner_gradient_accumulation_steps_optimizer_at_group_boundaries(tmp_path):
    class CountingSGD(torch.optim.SGD):
        def __init__(self, params, **kwargs):
            super().__init__(params, **kwargs)
            self.step_calls = 0
        def step(self, closure=None):
            self.step_calls += 1
            return super().step(closure)

    ds = TensorDataset(torch.randn(4,1,4,4), torch.randint(0,2,(4,4,4)))
    tr = DataLoader(ds, batch_size=1)
    va = DataLoader(ds, batch_size=2)
    model = Tiny()
    optimizer = CountingSGD(model.parameters(), lr=.01)
    result = run_experiment(
        model=model, train_loader=tr, validation_loader=va, task="semantic",
        optimizer=optimizer, output_dir=tmp_path,
        config={"experiment_id":"accum","dataset":"synthetic","max_epochs":1,
                "patience":1,"num_classes":2,"gradient_accumulation_steps":2},
        device="cpu",
    )
    assert result["status"] == "completed"
    # Four training batches grouped in pairs -> two optimizer updates.
    assert optimizer.step_calls == 2
