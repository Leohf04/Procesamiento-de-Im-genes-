import cv2
import numpy as np
from pathlib import Path
from src.utils.config_utils import resolve_backend

SEMANTIC_CLASS_IDS = {"person": 1, "bicycle": 2, "car": 3, "motorcycle": 4, "bus": 5,
                      "truck": 6, "rider": 7}
CITYSCAPES_INSTANCE_NAMES = ["__background__", "person", "rider", "car", "truck", "bus", "motorcycle", "bicycle"]


class InstanceSegmentationModel:
    def __init__(self, backend="auto", device="auto", confidence_threshold=0.50,
                 mask_threshold=0.50, allowed_labels=None, shared_labels=None,
                 checkpoint_path=None):
        self.backend = resolve_backend(backend)
        self.confidence_threshold, self.mask_threshold = confidence_threshold, mask_threshold
        self.allowed_labels = allowed_labels
        self.shared_labels = shared_labels or set(SEMANTIC_CLASS_IDS)
        self.urban_finetuned = False
        if self.backend == "torch":
            import torch
            import torchvision
            from torchvision.models.detection.mask_rcnn import MaskRCNN_ResNet50_FPN_V2_Weights, MaskRCNNPredictor
            from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
            self.device = torch.device(("cuda" if torch.cuda.is_available() else "cpu") if device == "auto" else device)
            if checkpoint_path and Path(checkpoint_path).is_file():
                checkpoint = torch.load(checkpoint_path, map_location=self.device, weights_only=False)
                class_names = checkpoint.get("class_names", CITYSCAPES_INSTANCE_NAMES)
                num_classes = int(checkpoint.get("num_classes", len(class_names)))
                if len(class_names) != num_classes:
                    raise ValueError("Los metadatos del checkpoint Mask R-CNN no coinciden con num_classes.")
                self.model = torchvision.models.detection.maskrcnn_resnet50_fpn_v2(weights=None, weights_backbone=None)
                box_features = self.model.roi_heads.box_predictor.cls_score.in_features
                self.model.roi_heads.box_predictor = FastRCNNPredictor(box_features, num_classes)
                mask_features = self.model.roi_heads.mask_predictor.conv5_mask.in_channels
                self.model.roi_heads.mask_predictor = MaskRCNNPredictor(mask_features, 256, num_classes)
                self.model.load_state_dict(checkpoint["model_state_dict"])
                self.category_names = class_names
                self.semantic_label_space = (
                    "bdd100k_instance" if "pedestrian" in class_names else "cityscapes"
                )
                self.urban_finetuned = True
            else:
                weights = MaskRCNN_ResNet50_FPN_V2_Weights.DEFAULT
                self.model = torchvision.models.detection.maskrcnn_resnet50_fpn_v2(weights=weights)
                self.category_names = weights.meta["categories"]
            self.model.to(self.device).eval()
            self.input_size = (512, 1024)
        else:
            self.hog_people = cv2.HOGDescriptor()
            self.hog_people.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    def _predict_torch(self, image_bgr):
        import torch
        h, w = image_bgr.shape[:2]
        rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        original_h, original_w = h, w
        if self.urban_finetuned:
            rgb = cv2.resize(rgb, (self.input_size[1], self.input_size[0]), interpolation=cv2.INTER_LINEAR)
        tensor = torch.from_numpy(rgb).permute(2, 0, 1).float().div(255).to(self.device)
        with torch.inference_mode():
            output = self.model([tensor])[0]
        scores, labels = output["scores"].cpu().numpy(), output["labels"].cpu().numpy()
        boxes, raw_masks = output["boxes"].cpu().numpy(), output["masks"][:, 0].cpu().numpy()
        if self.urban_finetuned:
            sx, sy = original_w / self.input_size[1], original_h / self.input_size[0]
            boxes[:, [0, 2]] *= sx
            boxes[:, [1, 3]] *= sy
            raw_masks = np.stack([cv2.resize(mask, (original_w, original_h), interpolation=cv2.INTER_LINEAR) for mask in raw_masks]) if len(raw_masks) else np.zeros((0, original_h, original_w), np.float32)
        keep, names = [], []
        for idx, (score, label) in enumerate(zip(scores, labels)):
            if int(label) >= len(self.category_names):
                continue
            name = self.category_names[int(label)]
            if score >= self.confidence_threshold and (self.allowed_labels is None or name in self.allowed_labels):
                keep.append(idx); names.append(name)
        fboxes = boxes[keep] if keep else np.zeros((0, 4), np.float32)
        flabels = labels[keep] if keep else np.zeros((0,), np.int64)
        fscores = scores[keep] if keep else np.zeros((0,), np.float32)
        masks = (raw_masks[keep] >= self.mask_threshold).astype(np.uint8) if keep else np.zeros((0, h, w), np.uint8)
        semantic = np.zeros((h, w), dtype=np.uint8)
        for mask, name in zip(masks, names):
            class_id = SEMANTIC_CLASS_IDS.get("person" if name == "pedestrian" else name)
            if class_id is not None:
                semantic[mask > 0] = class_id
        semantic_all = np.zeros((h, w), dtype=np.uint8)
        for mask, label in zip(masks, flabels):
            semantic_all[mask > 0] = int(label)
        return {"boxes": fboxes, "labels": flabels, "class_names": names, "scores": fscores,
                "instance_masks": masks, "urban_semantic_mask": semantic,
                "urban_semantic_mask_all8": semantic_all, "urban_finetuned": self.urban_finetuned,
                "semantic_label_space": getattr(self, "semantic_label_space", "coco") if self.urban_finetuned else "coco"}

    def _predict_onnx_cv2(self, image_bgr):
        h, w = image_bgr.shape[:2]
        rects, weights = self.hog_people.detectMultiScale(image_bgr, winStride=(8, 8), padding=(8, 8), scale=1.05)
        boxes, scores, masks = [], [], []
        for (x, y, bw, bh), weight in zip(rects, weights):
            score = float(1.0 / (1.0 + np.exp(-float(weight))))
            if score < self.confidence_threshold or (self.allowed_labels is not None and "person" not in self.allowed_labels):
                continue
            x1, y1, x2, y2 = max(0, x), max(0, y), min(w, x + bw), min(h, y + bh)
            boxes.append([x1, y1, x2, y2]); scores.append(score)
            mask = np.zeros((h, w), np.uint8)
            cv2.ellipse(mask, ((x1+x2)//2, (y1+y2)//2), (max(1,(x2-x1)//2),max(1,(y2-y1)//2)), 0, 0, 360, 1, -1)
            masks.append(mask)
        fboxes = np.asarray(boxes, np.float32).reshape(-1, 4)
        fmasks = np.asarray(masks, np.uint8).reshape(-1, h, w) if masks else np.zeros((0,h,w), np.uint8)
        semantic = np.zeros((h,w), np.uint8)
        for mask in fmasks: semantic[mask > 0] = 1
        return {"boxes": fboxes, "labels": np.ones(len(boxes), np.int64), "class_names": ["person"]*len(boxes),
                "scores": np.asarray(scores, np.float32), "instance_masks": fmasks,
                "urban_semantic_mask": semantic, "urban_semantic_mask_all8": semantic.copy(),
                "urban_finetuned": False}

    def predict(self, image_bgr):
        return self._predict_torch(image_bgr) if self.backend == "torch" else self._predict_onnx_cv2(image_bgr)
