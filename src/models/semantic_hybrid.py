import cv2
import numpy as np

from src.utils.config_utils import resolve_backend


class SemanticHybridModel:
    def __init__(
        self,
        backend: str = "auto",
        device: str = "auto",
        confidence_threshold: float = 0.50,
        urban_voc_ids: list[int] | None = None,
        allowed_labels: set[str] | None = None,
        lane_params: dict | None = None,
    ):
        self.backend = resolve_backend(backend)
        self.confidence_threshold = confidence_threshold
        self.urban_voc_ids = (
            urban_voc_ids if urban_voc_ids is not None else [2, 6, 7, 14, 15]
        )
        self.allowed_labels = allowed_labels
        self.lane_params = lane_params or {}

        if self.backend == "torch":
            import torch
            import torchvision
            from torchvision import transforms
            from torchvision.models.detection import (
                FasterRCNN_ResNet50_FPN_V2_Weights,
            )
            from torchvision.models.segmentation import (
                DeepLabV3_ResNet50_Weights,
            )

            self.device = torch.device(
                ("cuda" if torch.cuda.is_available() else "cpu")
                if device == "auto"
                else device
            )

            seg_weights = DeepLabV3_ResNet50_Weights.DEFAULT
            self.seg_model = torchvision.models.segmentation.deeplabv3_resnet50(
                weights=seg_weights
            )
            self.seg_model.to(self.device)
            self.seg_model.eval()
            self.seg_normalize = transforms.Normalize(
                mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
            )

            det_weights = FasterRCNN_ResNet50_FPN_V2_Weights.DEFAULT
            self.det_model = torchvision.models.detection.fasterrcnn_resnet50_fpn_v2(
                weights=det_weights
            )
            self.det_model.to(self.device)
            self.det_model.eval()
            self.det_categories = det_weights.meta["categories"]
        else:
            # Modo demo ligero en Termux/Android: detección HOG de peatones + carriles HSV
            self.hog_people = cv2.HOGDescriptor()
            self.hog_people.setSVMDetector(
                cv2.HOGDescriptor_getDefaultPeopleDetector()
            )

    def _extract_lane_mask(self, image_bgr: np.ndarray) -> np.ndarray:
        h, w = image_bgr.shape[:2]
        roi = np.zeros((h, w), dtype=np.uint8)
        roi[int(h * 0.55) :, :] = 255

        w_low = np.array(
            self.lane_params.get("lane_hsv_white_lower", [0, 0, 185]), dtype=np.uint8
        )
        w_high = np.array(
            self.lane_params.get("lane_hsv_white_upper", [180, 45, 255]),
            dtype=np.uint8,
        )
        y_low = np.array(
            self.lane_params.get("lane_hsv_yellow_lower", [15, 80, 120]),
            dtype=np.uint8,
        )
        y_high = np.array(
            self.lane_params.get("lane_hsv_yellow_upper", [35, 255, 255]),
            dtype=np.uint8,
        )

        hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
        white_mask = cv2.inRange(hsv, w_low, w_high)
        yellow_mask = cv2.inRange(hsv, y_low, y_high)
        lanes = cv2.bitwise_and(cv2.bitwise_or(white_mask, yellow_mask), roi)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        lanes = cv2.morphologyEx(lanes, cv2.MORPH_CLOSE, kernel)
        return (lanes > 0).astype(np.uint8)

    def _predict_torch(self, image_bgr: np.ndarray) -> dict:
        import torch

        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        base_tensor = torch.from_numpy(image_rgb).permute(2, 0, 1).float() / 255.0

        seg_input = self.seg_normalize(base_tensor).unsqueeze(0).to(self.device)
        with torch.no_grad():
            seg_logits = self.seg_model(seg_input)["out"][0]
        raw_semantic_map = (
            seg_logits.argmax(0).cpu().numpy().astype(np.uint8)
        )
        # Mapear exclusivamente las clases urbanas VOC
        # (person, bicycle, car, motorbike, bus)
        urban_semantic_mask = np.isin(
            raw_semantic_map, self.urban_voc_ids
        ).astype(np.uint8)

        det_input = base_tensor.to(self.device)
        with torch.no_grad():
            det_out = self.det_model([det_input])[0]

        scores = det_out["scores"].cpu().numpy()
        labels = det_out["labels"].cpu().numpy()
        boxes = det_out["boxes"].cpu().numpy()

        keep_indices = []
        class_names = []
        for idx, (sc, lbl) in enumerate(zip(scores, labels)):
            if sc < self.confidence_threshold:
                continue
            cname = self.det_categories[int(lbl)]
            if self.allowed_labels is not None and cname not in self.allowed_labels:
                continue
            keep_indices.append(idx)
            class_names.append(cname)

        if keep_indices:
            f_boxes = boxes[keep_indices]
            f_labels = labels[keep_indices]
            f_scores = scores[keep_indices]
        else:
            f_boxes = np.zeros((0, 4), dtype=np.float32)
            f_labels = np.zeros((0,), dtype=np.int64)
            f_scores = np.zeros((0,), dtype=np.float32)

        return {
            "boxes": f_boxes,
            "labels": f_labels,
            "class_names": class_names,
            "scores": f_scores,
            "instance_masks": None,
            "raw_semantic_map": raw_semantic_map,
            "urban_semantic_mask": urban_semantic_mask,
            "lane_mask": self._extract_lane_mask(image_bgr),
        }

    def _predict_onnx_cv2(self, image_bgr: np.ndarray) -> dict:
        h, w = image_bgr.shape[:2]
        rects, weights = self.hog_people.detectMultiScale(
            image_bgr, winStride=(8, 8), padding=(8, 8), scale=1.05
        )

        boxes, labels, class_names, scores = [], [], [], []
        urban_semantic_mask = np.zeros((h, w), dtype=np.uint8)
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
            urban_semantic_mask[y1:y2, x1:x2] = 1

        return {
            "boxes": (
                np.array(boxes, dtype=np.float32)
                if boxes
                else np.zeros((0, 4), dtype=np.float32)
            ),
            "labels": (
                np.array(labels, dtype=np.int64)
                if labels
                else np.zeros((0,), dtype=np.int64)
            ),
            "class_names": class_names,
            "scores": (
                np.array(scores, dtype=np.float32)
                if scores
                else np.zeros((0,), dtype=np.float32)
            ),
            "instance_masks": None,
            "raw_semantic_map": urban_semantic_mask,
            "urban_semantic_mask": urban_semantic_mask,
            "lane_mask": self._extract_lane_mask(image_bgr),
        }

    def predict(self, image_bgr: np.ndarray) -> dict:
        if self.backend == "torch":
            return self._predict_torch(image_bgr)
        return self._predict_onnx_cv2(image_bgr)
