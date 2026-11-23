"""COCOeval-based Box AP and Mask AP for Torchvision Mask R-CNN."""
from __future__ import annotations
from contextlib import redirect_stdout
from io import StringIO
import numpy as np
import torch

def evaluate_coco_instance_segmentation(model, loader, device, categories):
    try:
        from pycocotools.coco import COCO
        from pycocotools.cocoeval import COCOeval
        from pycocotools import mask as mask_utils
    except ImportError as exc:
        raise RuntimeError("Install pycocotools to compute validated COCO Box/Mask AP") from exc
    category_ids=sorted(int(k) for k in categories)
    images=[]; annotations=[]; bbox_results=[]; segm_results=[]; support={k:0 for k in category_ids}
    ann_id=1; model.eval()
    with torch.inference_mode():
      for images_batch, targets in loader:
        predictions=model([im.to(device) for im in images_batch])
        for target,pred in zip(targets,predictions):
          image_id=int(target["image_id"].reshape(-1)[0].item())
          gt_masks=target["masks"].cpu().numpy().astype(np.uint8)
          gt_boxes=target["boxes"].cpu().numpy()
          gt_labels=target["labels"].cpu().numpy()
          h,w=gt_masks.shape[-2:] if gt_masks.ndim==3 else images_batch[0].shape[-2:]
          images.append({"id":image_id,"width":int(w),"height":int(h)})
          for mask,box,label in zip(gt_masks,gt_boxes,gt_labels):
            label=int(label)
            if label not in categories: raise ValueError(f"Unknown GT category id {label}")
            rle=mask_utils.encode(np.asfortranarray(mask))
            rle["counts"]=rle["counts"].decode("ascii")
            x1,y1,x2,y2=[float(v) for v in box]
            annotations.append({"id":ann_id,"image_id":image_id,"category_id":label,
                "segmentation":rle,"bbox":[x1,y1,max(0.,x2-x1),max(0.,y2-y1)],
                "area":float(mask.sum()),"iscrowd":0})
            support[label]+=1; ann_id+=1
          boxes=pred["boxes"].detach().cpu().numpy()
          labels=pred["labels"].detach().cpu().numpy()
          scores=pred["scores"].detach().cpu().numpy()
          masks=pred["masks"].detach().cpu().numpy()
          for box,label,score,mask in zip(boxes,labels,scores,masks):
            label=int(label)
            if label not in categories: continue
            x1,y1,x2,y2=[float(v) for v in box]
            bbox_results.append({"image_id":image_id,"category_id":label,"score":float(score),
                "bbox":[x1,y1,max(0.,x2-x1),max(0.,y2-y1)]})
            binary=(mask[0]>=0.5).astype(np.uint8)
            rle=mask_utils.encode(np.asfortranarray(binary))
            rle["counts"]=rle["counts"].decode("ascii")
            segm_results.append({"image_id":image_id,"category_id":label,"score":float(score),"segmentation":rle})
    if not images: raise RuntimeError("COCO validation loader produced no images")\n    if not annotations: raise RuntimeError("COCO Mask AP undefined: validation split has zero ground-truth instances")
    base={"images":images,"categories":[{"id":k,"name":str(categories[k])} for k in category_ids]}
    coco_gt=COCO(); coco_gt.dataset={**base,"annotations":annotations}
    with redirect_stdout(StringIO()): coco_gt.createIndex()
    def evaluate(results,iou_type):
        coco_dt=COCO()
        if results:
            with redirect_stdout(StringIO()): coco_dt=coco_gt.loadRes(results)
        else:
            coco_dt.dataset={**base,"annotations":[]}
            with redirect_stdout(StringIO()): coco_dt.createIndex()
        ev=COCOeval(coco_gt,coco_dt,iou_type)
        ev.params.imgIds=[int(x["id"]) for x in images]
        ev.params.catIds=category_ids
        with redirect_stdout(StringIO()):
            ev.evaluate(); ev.accumulate(); ev.summarize()
        return ev
    box_ev=evaluate(bbox_results,"bbox"); mask_ev=evaluate(segm_results,"segm")
    def per_class(ev):
        precision=ev.eval["precision"] # [IoU, recall, category, area, maxDets]
        result={}
        for i,cid in enumerate(ev.params.catIds):
            values=precision[:,: ,i,0,-1]; values=values[values>-1]
            result[str(cid)]={"name":str(categories[cid]),
                "ap":float(values.mean()) if values.size else None,"ground_truth_instances":support[cid]}
        return result
    return {"box_ap":float(box_ev.stats[0]),"box_ap50":float(box_ev.stats[1]),
        "box_ap75":float(box_ev.stats[2]),"mask_ap":float(mask_ev.stats[0]),
        "mask_ap50":float(mask_ev.stats[1]),"mask_ap75":float(mask_ev.stats[2]),
        "mask_ap_per_class":per_class(mask_ev),"box_ap_per_class":per_class(box_ev),
        "images":len(images),"ground_truth_instances":int(sum(support.values())),
        "evaluator":"pycocotools.COCOeval","iou_thresholds":"0.50:0.05:0.95"}
