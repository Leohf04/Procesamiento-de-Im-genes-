import os
import time
import cv2
from src.features.fine_classifier import FineGrainedClassifier
from src.models.instance_seg import InstanceSegmentationModel
from src.models.semantic_hybrid import SemanticHybridModel
from src.utils.config_utils import load_config, resolve_backend
from src.utils.visualization import render_predictions


class UrbanPerceptionPipeline:
    def __init__(self, approach="instance", config_path="configs/config.yaml", backend="auto", model_override=None):
        self.config = load_config(config_path)
        self.evaluation_cfg = self.config.get("evaluation", {})
        self.approach = approach
        self.backend = resolve_backend(backend)
        target_cfg = self.config.get("target_classes", {})
        self.allowed_labels = set(target_cfg.get("urban_labels", []))
        shared5 = self.config.get("models", {}).get("semantic_hybrid", {}).get("shared_mask_labels")
        self.shared5 = shared5 or ["person", "bicycle", "car", "motorcycle", "bus"]
        fine_cfg = self.config.get("fine_classification", {})
        self.subclasses_map = fine_cfg.get("subclasses_map", {})
        self.fine_classifier = FineGrainedClassifier(model_path=fine_cfg.get("model_path", "data/processed/fine_svm_classifier.joblib"))
        if model_override is not None:
            self.model = model_override
        elif self.backend == "torch" and self.approach == "instance":
            cfg = self.config["models"]["instance"]
            self.model = InstanceSegmentationModel(backend="torch",
                device=self.config.get("system", {}).get("device", "auto"),
                confidence_threshold=cfg.get("confidence_threshold", 0.5),
                mask_threshold=cfg.get("mask_threshold", 0.5),
                allowed_labels=self.allowed_labels, shared_labels=set(self.shared5),
                checkpoint_path=cfg.get("urban_checkpoint"))
        elif self.approach == "hybrid" and self.backend in {"torch", "onnx"}:
            cfg = self.config["models"]["semantic_hybrid"]
            self.model = SemanticHybridModel(backend=self.backend,
                device=self.config.get("system", {}).get("device", "auto"),
                confidence_threshold=cfg.get("detector_confidence_threshold", 0.5),
                allowed_labels=self.allowed_labels, lane_params=cfg,
                segmentation_checkpoint=cfg.get("checkpoint_path"),
                lane_checkpoint=cfg.get("lane_checkpoint"),
                num_semantic_classes=cfg.get("num_classes", 11),
                input_size=tuple(cfg.get("input_size", [512, 1024])))
        elif self.backend == "onnx":
            raise ValueError("ONNX semántico solo admite --approach hybrid; no equivale a Mask R-CNN.")
        elif self.backend == "torch":
            raise ValueError(f"Enfoque no soportado: {self.approach}")
        else:
            self.model = InstanceSegmentationModel(backend="onnx_cv2",
                confidence_threshold=self.config.get("models", {}).get("instance", {}).get("confidence_threshold", 0.5),
                allowed_labels=self.allowed_labels, shared_labels=set(self.shared5))

    def run_frame(self, frame_bgr):
        prediction = self.model.predict(frame_bgr)
        fine_labels = []
        for box, cname, score in zip(prediction.get("boxes", []), prediction.get("class_names", []), prediction.get("scores", [])):
            fine_name, _ = self.fine_classifier.predict_roi(frame_bgr, tuple(map(int, box)), cname, float(score), subclasses_map=self.subclasses_map)
            fine_labels.append(fine_name)
        prediction["fine_labels"] = fine_labels
        return prediction

    def process_video_stream(self, source=0, output_video_path=None, max_frames=None):
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            raise RuntimeError(f"No se pudo abrir la fuente de video: {source}")
        writer = None
        frames_written = 0
        start_time = time.perf_counter()
        output_size = None
        try:
            while True:
                ret, frame = cap.read()
                if not ret or (max_frames is not None and frames_written >= max_frames):
                    break
                process_start = time.perf_counter()
                prediction = self.run_frame(frame)
                elapsed = time.perf_counter() - process_start
                output = render_predictions(frame, prediction, 1.0 / elapsed if elapsed > 0 else 0.0)
                output_size = (frame.shape[1], frame.shape[0])
                if output_video_path:
                    if writer is None:
                        out_dir = os.path.dirname(output_video_path)
                        if out_dir: os.makedirs(out_dir, exist_ok=True)
                        writer = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*"mp4v"), 20.0, output_size)
                        if not writer.isOpened():
                            writer.release()
                            raise RuntimeError(f"VideoWriter no pudo crear '{output_video_path}'.")
                    writer.write(output)
                frames_written += 1
        finally:
            cap.release()
            if writer is not None: writer.release()
        elapsed = time.perf_counter() - start_time
        return {"frames_written": frames_written, "elapsed_seconds": elapsed,
                "fps": frames_written / elapsed if elapsed > 0 else 0.0, "output_size": output_size}
