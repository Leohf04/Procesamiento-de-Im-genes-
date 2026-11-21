import cv2
import numpy as np

from src.utils.config_utils import resolve_backend


class InstanceSegmentationModel:
    def __init__(
        self,
        backend: str = "auto",
        device: str = "auto",
        confidence_threshold: float = 0.50,
        mask_threshold: float = 0.50,
        allowed_labels: set[str] | None = None,
        shared_labels: set[str] | None = None,
    ):
        self.backend = resolve_backend(backend)
        self.confidence_threshold = confidence_threshold
        self.mask_threshold = mask_threshold
        self.allowed_labels = allowed_labels
        self.shared_labels = shared_labels or {
            "person",
            "bicycle",
            "car",
            "motorcycle",
            "bus",
        }

        if self.backend == "torch":
            import torch
            import torchvision
            from torchvision.models.detection.mask_rcnn import (
                MaskRCNN_ResNet50_FPN_V2_Weights,
            )

            self.device = torch.device(
                ("cuda" if torch.cuda.is_available() else "cpu")
                if device == "auto"
                else device
            )
            weights = MaskRCNN_ResNet50_FPN_V2_Weights.DEFAULT
            self.model = torchvision.models.detection.maskrcnn_resnet50_fpn_v2(
                weights=weights
            )
            self.model.to(self.device)
            self.model.eval()
            self.category_names = weights.meta["categories"]
        else:
            # Modo demo ligero en Termux/Android: detector clásico HOG de peatones
            # + máscara elíptica.
            self.hog_people = cv2.HOGDescriptor()
            self.hog_people.setSVMDetector(
                cv2.HOGDescriptor_getDefaultPeopleDetector()
            )

    def _predict_torch(self, image_bgr: np.ndarray) -> dict:
        import torch

        h, w = image_bgr.shape[:2]
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        tensor_img = (
            torch.from_numpy(image_rgb).permute(2, 0, 1).float() / 255.0
        )
        tensor_img = tensor_img.to(self.device)

        with torch.no_grad():
            outputs = self.model([tensor_img])[0]

        scores = outputs["scores"].cpu().numpy()
        labels = outputs["labels"].cpu().numpy()
        boxes = outputs["boxes"].cpu().numpy()
        raw_masks = outputs["masks"][:, 0].cpu().numpy()

        keep_indices = []
        class_names = []
        for idx, (sc, lbl) in enumerate(zip(scores, labels)):
            if sc < self.confidence_threshold:
                continue
            cname = self.category_names[int(lbl)]
            if self.allowed_labels is not None and cname not in self.allowed_labels:
                continue
            keep_indices.append(idx)
            class_names.append(cname)

        if keep_indices:
            f_boxes = boxes[keep_indices]
            f_labels = labels[keep_indices]
            f_scores = scores[keep_indices]
            f_masks = (
                raw_masks[keep_indices] >= self.mask_threshold
            ).astype(np.uint8)
            urban_sem_all8 = np.max(f_masks, axis=0).astype(np.uint8)
            shared_idx = [
                i for i, cn in enumerate(class_names) if cn in self.shared_labels
            ]
            urban_sem_shared5 = (
                np.max(f_masks[shared_idx], axis=0).astype(np.uint8)
                if shared_idx
                else np.zeros((h, w), dtype=np.uint8)
            )
        else:
            f_boxes = np.zeros((0, 4), dtype=np.float32)
            f_labels = np.zeros((0,), dtype=np.int64)
            f_scores = np.zeros((0,), dtype=np.float32)
            f_masks = np.zeros((0, h, w), dtype=np.uint8)
            urban_sem_all8 = np.zeros((h, w), dtype=np.uint8)
            urban_sem_shared5 = np.zeros((h, w), dtype=np.uint8)

        return {
            "boxes": f_boxes,
            "labels": f_labels,
            "class_names": class_names,
            "scores": f_scores,
            "instance_masks": f_masks,
            "urban_semantic_mask": urban_sem_shared5,
            "urban_semantic_mask_all8": urban_sem_all8,
        }

    def _predict_onnx_cv2(self, image_bgr: np.ndarray) -> dict:
        h, w = image_bgr.shape[:2]
        rects, weights = self.hog_people.detectMultiScale(
            image_bgr, winStride=(8, 8), padding=(8, 8), scale=1.05
        )

        boxes, labels, class_names, scores, masks = [], [], [], [], []
        for (x, y, bw, bh), weight in zip(rects, weights):
            sc = float(1.0 / (1.0 + np.exp(-float(weight))))
            if sc < self.confidence_threshold:
                continue
            if self.allowed_labels is not None and "person" not in self.allowed_labels:
                continue
            x1, y1, x2, y2 = max(0, x), max(0, y), min(w, x + bw), min(h, y + bh)
            boxes.append([x1, y1, x2, y2])
            labels.append(1)
            class_names.append("person")
            scores.append(sc)
            m = np.zeros((h, w), dtype=np.uint8)
            cv2.ellipse(
                m,
                ((x1 + x2) // 2, (y1 + y2) // 2),
                (max(1, (x2 - x1) // 2), max(1, (y2 - y1) // 2)),
                0,
                0,
                360,
                1,
                -1,
            )
            masks.append(m)

        if boxes:
            f_boxes = np.array(boxes, dtype=np.float32)
            f_labels = np.array(labels, dtype=np.int64)
            f_scores = np.array(scores, dtype=np.float32)
            f_masks = np.array(masks, dtype=np.uint8)
            urban_sem = np.max(f_masks, axis=0).astype(np.uint8)
        else:
            f_boxes = np.zeros((0, 4), dtype=np.float32)
            f_labels = np.zeros((0,), dtype=np.int64)
            f_scores = np.zeros((0,), dtype=np.float32)
            f_masks = np.zeros((0, h, w), dtype=np.uint8)
            urban_sem = np.zeros((h, w), dtype=np.uint8)

        return {
            "boxes": f_boxes,
            "labels": f_labels,
            "class_names": class_names,
            "scores": f_scores,
            "instance_masks": f_masks,
            "urban_semantic_mask": urban_sem,
            "urban_semantic_mask_all8": urban_sem,
        }

    def predict(self, image_bgr: np.ndarray) -> dict:
        if self.backend == "torch":
            return self._predict_torch(image_bgr)
        return self._predict_onnx_cv2(image_bgr)
