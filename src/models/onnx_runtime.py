"""Real ONNX Runtime semantic-segmentation inference adapter."""
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
        labels = cv2.resize(labels, (w, h), interpolation=cv2.INTER_NEAREST)
        return labels
