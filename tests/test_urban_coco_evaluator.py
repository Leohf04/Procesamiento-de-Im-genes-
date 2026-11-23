import pytest
import torch
from torch import nn
from src.urban_coco_evaluator import evaluate_coco_instance_segmentation

pycoco = pytest.importorskip("pycocotools")

class PerfectDetector(nn.Module):
    def forward(self, images):
        outputs=[]
        for image in images:
            mask=torch.zeros((1,1,*image.shape[-2:]),device=image.device)
            mask[:,:,0:2,0:2]=1
            outputs.append({"boxes":torch.tensor([[0.,0.,2.,2.]],device=image.device),
                "labels":torch.tensor([1],device=image.device),
                "scores":torch.tensor([0.99],device=image.device),"masks":mask})
        return outputs

def test_coco_evaluator_reports_real_box_and_mask_ap():
    image=torch.zeros((3,4,4))
    mask=torch.zeros((1,4,4),dtype=torch.uint8); mask[:,0:2,0:2]=1
    target={"image_id":torch.tensor([7]),"boxes":torch.tensor([[0.,0.,2.,2.]]),
        "labels":torch.tensor([1]),"masks":mask,"area":torch.tensor([4.]),
        "iscrowd":torch.tensor([0])}
    loader=[([image],[target])]
    report=evaluate_coco_instance_segmentation(PerfectDetector(),loader,torch.device("cpu"),{1:"car"})
    assert report["evaluator"]=="pycocotools.COCOeval"
    assert report["mask_ap"]>0.99 and report["box_ap"]>0.99
    assert report["ground_truth_instances"]==1
