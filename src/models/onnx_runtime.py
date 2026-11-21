"""Real ONNX Runtime semantic and lane segmentation inference."""
import cv2
import numpy as np


class ONNXSemanticSegmenter:
    def __init__(self, model_path, num_classes, input_size=(512, 1024), providers=None):
        try:
            import onnxruntime as ort
        except ImportError as exc:
            raise RuntimeError("Backend ONNX requiere onnxruntime u onnxruntime-gpu.") from exc
        self.session = ort.InferenceSession(str(model_path), providers=providers or ["CPUExecutionProvider"])
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
        self.num_classes = int(num_classes)
        self.input_size = tuple(input_size)

    def predict(self, image_bgr):
        h, w = image_bgr.shape[:2]
        resized = cv2.resize(cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB),
                             (self.input_size[1], self.input_size[0])).astype(np.float32) / 255.0
        mean = np.array([0.485, 0.456, 0.406], np.float32)
        std = np.array([0.229, 0.224, 0.225], np.float32)
        tensor = ((resized - mean) / std).transpose(2, 0, 1)[None].astype(np.float32)
        output = self.session.run([self.output_name], {self.input_name: tensor})[0]
        if output.ndim != 4 or output.shape[1] != self.num_classes:
            raise ValueError(f"Salida ONNX esperada [1,{self.num_classes},H,W], recibida {output.shape}")
        labels = output.argmax(axis=1)[0].astype(np.uint8)
        return cv2.resize(labels, (w, h), interpolation=cv2.INTER_NEAREST)


class ONNXUrbanHybridModel:
    def __init__(self, semantic_path, lane_path=None, num_semantic_classes=11, input_size=(512, 1024)):
        if not semantic_path:
            raise ValueError("Configura models.semantic_hybrid.onnx_semantic_model")
        self.semantic = ONNXSemanticSegmenter(semantic_path, num_semantic_classes, input_size)
        self.lane = ONNXSemanticSegmenter(lane_path, 2, input_size) if lane_path else None

    def predict(self, image_bgr):
        raw = self.semantic.predict(image_bgr)
        lane = self.lane.predict(image_bgr) if self.lane else np.zeros(raw.shape, np.uint8)
        mapping = {2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 7, 9: 8, 10: 9, 1: 10}
        semantic = np.zeros(raw.shape, np.uint8)
        for source_id, target_id in mapping.items():
            semantic[raw == source_id] = target_id
        return {"boxes": np.zeros((0, 4), np.float32), "labels": np.zeros((0,), np.int64),
                "class_names": [], "scores": np.zeros((0,), np.float32), "instance_masks": None,
                "raw_semantic_map": raw, "urban_semantic_mask": semantic,
                "lane_mask": lane, "lane_model_loaded": self.lane is not None,
                "detection_note": "Este export ONNX solo realiza segmentación semántica; no genera cajas ni instancias."}
