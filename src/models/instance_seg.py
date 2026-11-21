import cv2
import numpy as np

from src.utils.config_utils import resolve_backend

SEMANTIC_CLASS_IDS = {"person": 1, "bicycle": 2, "car": 3, "motorcycle": 4, "bus": 5}


class InstanceSegmentationModel:
    def __init__(self, backend="auto", device="auto", confidence_threshold=0.50, mask_threshold=0.50, allowed_labels=None, shared_labels=None):
        self.backend = resolve_backend(backend)
        self.confidence_threshold, self.mask_threshold = confidence_threshold, mask_threshold
        self.allowed_labels = allowed_labels
        self.shared_labels = shared_labels or set(SEMANTIC_CLASS_IDS)
        if self.backend == "torch":
            import torch
            import torchvision
            from torchvision.models.detection.mask_rcnn import MaskRCNN_ResNet50_FPN_V2_Weights
            self.device = torch.device(("cuda" if torch.cuda.is_available() else "cpu") if device == "auto" else device)
            weights = MaskRCNN_ResNet50_FPN_V2_Weights.DEFAULT
            self.model = torchvision.models.detection.maskrcnn_resnet50_fpn_v2(weights=weights).to(self.device)
            self.model.eval()
            self.category_names = weights.meta["categories"]
        else:
            self.hog_people = cv2.HOGDescriptor()
            self.hog_people.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    def _predict_torch(self, image_bgr):
        import torch
        h, w = image_bgr.shape[:2]
        rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        tensor = torch.from_numpy(rgb).permute(2, 0, 1).float().div(255).to(self.device)
        with torch.no_grad():
            output = self.model([tensor])[0]
        scores, labels = output["scores"].cpu().numpy(), output["labels"].cpu().numpy()
        boxes, raw_masks = output["boxes"].cpu().numpy(), output["masks"][:, 0].cpu().numpy()
        keep, names = [], []
        for idx, (score, label) in enumerate(zip(scores, labels)):
            name = self.category_names[int(label)]
            if score >= self.confidence_threshold and (self.allowed_labels is None or name in self.allowed_labels):
                keep.append(idx); names.append(name)
        fboxes = boxes[keep] if keep else np.zeros((0, 4), np.float32)
        flabels = labels[keep] if keep else np.zeros((0,), np.int64)
        fscores = scores[keep] if keep else np.zeros((0,), np.float32)
        masks = (raw_masks[keep] >= self.mask_threshold).astype(np.uint8) if keep else np.zeros((0, h, w), np.uint8)
        semantic = np.zeros((h, w), dtype=np.uint8)
        for mask, name in zip(masks, names):
            class_id = SEMANTIC_CLASS_IDS.get(name)
            if class_id is not None:
                semantic[mask > 0] = class_id
        semantic_all = np.zeros((h, w), dtype=np.uint8)
        for mask, label in zip(masks, flabels):
            semantic_all[mask > 0] = int(label)
        return {"boxes": fboxes, "labels": flabels, "class_names": names, "scores": fscores,
                "instance_masks": masks, "urban_semantic_mask": semantic,
                "urban_semantic_mask_all8": semantic_all}

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
                "urban_semantic_mask": semantic, "urban_semantic_mask_all8": semantic.copy()}

    def predict(self, image_bgr):
        return self._predict_torch(image_bgr) if self.backend == "torch" else self._predict_onnx_cv2(image_bgr)
