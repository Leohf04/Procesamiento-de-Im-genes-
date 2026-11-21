import cv2
import numpy as np
from pathlib import Path
from src.utils.config_utils import resolve_backend

CITYSCAPES_TO_PROJECT = {2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 7, 9: 8, 10: 9, 1: 10}


class SemanticHybridModel:
    def __init__(self, backend="auto", device="auto", confidence_threshold=0.50,
                 urban_voc_ids=None, allowed_labels=None, lane_params=None,
                 segmentation_checkpoint=None, lane_checkpoint=None,
                 num_semantic_classes=11, input_size=(512, 1024)):
        self.backend = resolve_backend(backend)
        self.confidence_threshold = confidence_threshold
        self.allowed_labels, self.lane_params = allowed_labels, lane_params or {}
        self.input_size = tuple(input_size)
        if self.backend == "torch":
            import torch
            import torchvision
            from torchvision import transforms
            from torchvision.models.detection import FasterRCNN_ResNet50_FPN_V2_Weights
            from src.models.deeplabv3plus import DeepLabV3Plus
            self.device = torch.device(("cuda" if torch.cuda.is_available() else "cpu") if device == "auto" else device)
            if not segmentation_checkpoint or not Path(segmentation_checkpoint).is_file():
                raise FileNotFoundError(
                    "No existe el checkpoint urbano DeepLabV3+. Entrena primero con "
                    "python scripts/train_urban_segmentation.py --task cityscapes --data-root data/cityscapes"
                )
            checkpoint = torch.load(segmentation_checkpoint, map_location=self.device)
            self.seg_model = DeepLabV3Plus(num_semantic_classes, pretrained_backbone=False)
            self.seg_model.load_state_dict(checkpoint["model_state_dict"])
            self.seg_model.to(self.device).eval()
            self.seg_normalize = transforms.Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])
            det_weights = FasterRCNN_ResNet50_FPN_V2_Weights.DEFAULT
            self.det_model = torchvision.models.detection.fasterrcnn_resnet50_fpn_v2(weights=det_weights).to(self.device).eval()
            self.det_categories = det_weights.meta["categories"]
            self.lane_model = None
            if lane_checkpoint and Path(lane_checkpoint).is_file():
                lane_ckpt = torch.load(lane_checkpoint, map_location=self.device)
                self.lane_model = DeepLabV3Plus(2, pretrained_backbone=False)
                self.lane_model.load_state_dict(lane_ckpt["model_state_dict"])
                self.lane_model.to(self.device).eval()
        elif self.backend == "onnx":
            from src.models.onnx_runtime import ONNXUrbanHybridModel
            self.onnx_model = ONNXUrbanHybridModel(
                self.lane_params["onnx_semantic_model"], self.lane_params.get("onnx_lane_model"),
                num_semantic_classes, self.input_size)
        else:
            raise ValueError("El backend clásico OpenCV/HOG no implementa segmentación semántica urbana.")

    def _predict_torch(self, image):
        import torch
        rgb=cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
        resized=cv2.resize(rgb,(self.input_size[1],self.input_size[0]),interpolation=cv2.INTER_LINEAR)
        tensor=torch.from_numpy(resized).permute(2,0,1).float()/255
        detector_tensor=torch.from_numpy(rgb).permute(2,0,1).float()/255
        with torch.inference_mode():
            logits=self.seg_model(self.seg_normalize(tensor).unsqueeze(0).to(self.device))["out"][0]
            raw=logits.argmax(0).cpu().numpy().astype(np.uint8)
            det=self.det_model([detector_tensor.to(self.device)])[0]
            lane = None
            if self.lane_model is not None:
                lane_logits=self.lane_model(self.seg_normalize(tensor).unsqueeze(0).to(self.device))["out"][0]
                lane=lane_logits.argmax(0).cpu().numpy().astype(np.uint8)
        raw=cv2.resize(raw,(image.shape[1],image.shape[0]),interpolation=cv2.INTER_NEAREST)
        semantic=np.zeros(raw.shape,np.uint8)
        for source_id,target_id in CITYSCAPES_TO_PROJECT.items():
            semantic[raw==source_id]=target_id
        scores=det["scores"].cpu().numpy(); labels=det["labels"].cpu().numpy(); boxes=det["boxes"].cpu().numpy()
        keep=[]; names=[]
        for i,(score,label) in enumerate(zip(scores,labels)):
            name=self.det_categories[int(label)]
            if score>=self.confidence_threshold and (self.allowed_labels is None or name in self.allowed_labels):
                keep.append(i); names.append(name)
        lane_mask=np.zeros(raw.shape,np.uint8) if lane is None else cv2.resize(lane,(image.shape[1],image.shape[0]),interpolation=cv2.INTER_NEAREST)
        return {"boxes":boxes[keep] if keep else np.zeros((0,4),np.float32),
                "labels":labels[keep] if keep else np.zeros((0,),np.int64),"class_names":names,
                "scores":scores[keep] if keep else np.zeros((0,),np.float32),
                "instance_masks":None,"raw_semantic_map":raw,"urban_semantic_mask":semantic,
                "lane_mask":lane_mask,"lane_model_loaded":self.lane_model is not None}

    def predict(self,image_bgr):
        if self.backend == "torch":
            return self._predict_torch(image_bgr)
        return self.onnx_model.predict(image_bgr)
