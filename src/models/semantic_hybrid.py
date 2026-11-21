import cv2
import numpy as np

from src.utils.config_utils import resolve_backend

VOC_TO_SEMANTIC = {15: 1, 2: 2, 7: 3, 14: 4, 6: 5}


class SemanticHybridModel:
    def __init__(self, backend="auto", device="auto", confidence_threshold=0.50, urban_voc_ids=None, allowed_labels=None, lane_params=None):
        self.backend = resolve_backend(backend)
        self.confidence_threshold = confidence_threshold
        self.urban_voc_ids = urban_voc_ids if urban_voc_ids is not None else list(VOC_TO_SEMANTIC)
        self.allowed_labels, self.lane_params = allowed_labels, lane_params or {}
        if self.backend == "torch":
            import torch
            import torchvision
            from torchvision import transforms
            from torchvision.models.detection import FasterRCNN_ResNet50_FPN_V2_Weights
            from torchvision.models.segmentation import DeepLabV3_ResNet50_Weights
            self.device = torch.device(("cuda" if torch.cuda.is_available() else "cpu") if device == "auto" else device)
            seg_weights = DeepLabV3_ResNet50_Weights.DEFAULT
            self.seg_model = torchvision.models.segmentation.deeplabv3_resnet50(weights=seg_weights).to(self.device).eval()
            self.seg_normalize = transforms.Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])
            det_weights = FasterRCNN_ResNet50_FPN_V2_Weights.DEFAULT
            self.det_model = torchvision.models.detection.fasterrcnn_resnet50_fpn_v2(weights=det_weights).to(self.device).eval()
            self.det_categories = det_weights.meta["categories"]
        else:
            self.hog_people = cv2.HOGDescriptor()
            self.hog_people.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    def _extract_lane_mask(self, image):
        h,w=image.shape[:2]; roi=np.zeros((h,w),np.uint8); roi[int(h*.55):,:]=255
        wl=np.array(self.lane_params.get("lane_hsv_white_lower",[0,0,185]),np.uint8); wu=np.array(self.lane_params.get("lane_hsv_white_upper",[180,45,255]),np.uint8)
        yl=np.array(self.lane_params.get("lane_hsv_yellow_lower",[15,80,120]),np.uint8); yu=np.array(self.lane_params.get("lane_hsv_yellow_upper",[35,255,255]),np.uint8)
        hsv=cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
        lanes=cv2.bitwise_and(cv2.bitwise_or(cv2.inRange(hsv,wl,wu),cv2.inRange(hsv,yl,yu)),roi)
        return (cv2.morphologyEx(lanes,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_RECT,(5,5)))>0).astype(np.uint8)

    def _predict_torch(self, image):
        import torch
        rgb=cv2.cvtColor(image,cv2.COLOR_BGR2RGB); tensor=torch.from_numpy(rgb).permute(2,0,1).float()/255
        with torch.no_grad():
            logits=self.seg_model(self.seg_normalize(tensor).unsqueeze(0).to(self.device))["out"][0]
            raw=logits.argmax(0).cpu().numpy().astype(np.uint8)
            det=self.det_model([tensor.to(self.device)])[0]
        semantic=np.zeros(raw.shape,np.uint8)
        for voc_id,class_id in VOC_TO_SEMANTIC.items(): semantic[raw==voc_id]=class_id
        scores=det["scores"].cpu().numpy(); labels=det["labels"].cpu().numpy(); boxes=det["boxes"].cpu().numpy()
        keep=[]; names=[]
        for i,(score,label) in enumerate(zip(scores,labels)):
            name=self.det_categories[int(label)]
            if score>=self.confidence_threshold and (self.allowed_labels is None or name in self.allowed_labels):
                keep.append(i); names.append(name)
        return {"boxes":boxes[keep] if keep else np.zeros((0,4),np.float32),
                "labels":labels[keep] if keep else np.zeros((0,),np.int64),"class_names":names,
                "scores":scores[keep] if keep else np.zeros((0,),np.float32),
                "instance_masks":None,"raw_semantic_map":raw,"urban_semantic_mask":semantic,
                "lane_mask":self._extract_lane_mask(image)}

    def _predict_onnx_cv2(self,image):
        h,w=image.shape[:2]; rects,weights=self.hog_people.detectMultiScale(image,winStride=(8,8),padding=(8,8),scale=1.05)
        boxes=[];scores=[];semantic=np.zeros((h,w),np.uint8)
        for (x,y,bw,bh),weight in zip(rects,weights):
            score=float(1/(1+np.exp(-float(weight))))
            if score<self.confidence_threshold or (self.allowed_labels is not None and "person" not in self.allowed_labels): continue
            x1,y1,x2,y2=max(0,x),max(0,y),min(w,x+bw),min(h,y+bh); boxes.append([x1,y1,x2,y2]);scores.append(score);semantic[y1:y2,x1:x2]=1
        return {"boxes":np.asarray(boxes,np.float32).reshape(-1,4),"labels":np.ones(len(boxes),np.int64),
                "class_names":["person"]*len(boxes),"scores":np.asarray(scores,np.float32),
                "instance_masks":None,"raw_semantic_map":semantic,"urban_semantic_mask":semantic,
                "lane_mask":self._extract_lane_mask(image)}

    def predict(self,image_bgr):
        return self._predict_torch(image_bgr) if self.backend=="torch" else self._predict_onnx_cv2(image_bgr)
