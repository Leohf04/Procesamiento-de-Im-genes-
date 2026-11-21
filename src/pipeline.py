import os
import time

import cv2

from src.features.fine_classifier import FineGrainedClassifier
from src.models.instance_seg import InstanceSegmentationModel
from src.models.semantic_hybrid import SemanticHybridModel
from src.utils.config_utils import load_config, resolve_backend
from src.utils.visualization import render_predictions


class UrbanPerceptionPipeline:
    def __init__(
        self,
        approach: str = "instance",
        config_path: str = "configs/config.yaml",
        backend: str = "auto",
        model_override=None,
    ):
        self.config = load_config(config_path)
        self.evaluation_cfg = self.config.get("evaluation", {})
        self.approach = approach
        self.backend = resolve_backend(backend)

        target_cfg = self.config.get("target_classes", {})
        self.allowed_labels = set(target_cfg.get("urban_labels", []))
        self.coco_category_ids = set(target_cfg.get("coco_category_ids", []))

        shared5 = self.config.get("models", {}).get("semantic_hybrid", {}).get(
            "shared_mask_labels"
        )
        self.shared5 = shared5 or [
            "person",
            "bicycle",
            "car",
            "motorcycle",
            "bus",
        ]

        fine_cfg = self.config.get("fine_classification", {})
        self.subclasses_map = fine_cfg.get("subclasses_map", {})
        self.fine_classifier = FineGrainedClassifier(
            model_path=fine_cfg.get(
                "model_path", "data/processed/fine_svm_classifier.joblib"
            )
        )

        if model_override is not None:
            self.model = model_override
        elif self.backend == "torch":
            if self.approach == "instance":
                instance_cfg = self.config["models"]["instance"]
                self.model = InstanceSegmentationModel(
                    backend=self.backend,
                    device=self.config.get("system", {}).get("device", "auto"),
                    confidence_threshold=instance_cfg.get(
                        "confidence_threshold", 0.50
                    ),
                    mask_threshold=instance_cfg.get("mask_threshold", 0.50),
                    allowed_labels=self.allowed_labels,
                    shared_labels=set(self.shared5),
                )
            else:
                hybrid_cfg = self.config["models"]["semantic_hybrid"]
                self.model = SemanticHybridModel(
                    backend=self.backend,
                    device=self.config.get("system", {}).get("device", "auto"),
                    confidence_threshold=hybrid_cfg.get(
                        "detector_confidence_threshold", 0.50
                    ),
                    urban_voc_ids=hybrid_cfg.get(
                        "deeplab_urban_voc_ids", [2, 6, 7, 14, 15]
                    ),
                    allowed_labels=self.allowed_labels,
                    lane_params=hybrid_cfg,
                )
        else:
            # Backend ligero para Termux/Android (sin PyTorch): modo demo.
            self.model = InstanceSegmentationModel(
                backend="onnx_cv2",
                confidence_threshold=self.config.get("models", {})
                .get("instance", {})
                .get("confidence_threshold", 0.50),
                allowed_labels=self.allowed_labels,
                shared_labels=set(self.shared5),
            )

    def run_frame(self, frame_bgr) -> dict:
        prediction = self.model.predict(frame_bgr)
        boxes = prediction.get("boxes", [])
        class_names = prediction.get("class_names", [])
        scores = prediction.get("scores", [])

        fine_labels = []
        for box, cname, score in zip(boxes, class_names, scores):
            fine_name, _fine_score = self.fine_classifier.predict_roi(
                frame_bgr,
                tuple(map(int, box)),
                cname,
                float(score),
                subclasses_map=self.subclasses_map,
            )
            fine_labels.append(fine_name)

        prediction["fine_labels"] = fine_labels
        return prediction

    def process_video_stream(
        self,
        source=0,
        output_video_path: str | None = None,
        max_frames: int | None = None,
    ) -> dict:
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
                if not ret:
                    break
                if max_frames is not None and frames_written >= max_frames:
                    break

                process_start = time.perf_counter()
                prediction = self.run_frame(frame)
                elapsed = time.perf_counter() - process_start
                current_fps = 1.0 / elapsed if elapsed > 0 else 0.0

                output = render_predictions(frame, prediction, current_fps)
                output_size = (frame.shape[1], frame.shape[0])

                if output_video_path:
                    if writer is None:
                        out_dir = os.path.dirname(output_video_path)
                        if out_dir:
                            os.makedirs(out_dir, exist_ok=True)
                        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                        writer = cv2.VideoWriter(
                            output_video_path, fourcc, 20.0, output_size
                        )
                        if not writer.isOpened():
                            writer.release()
                            writer = None
                            raise RuntimeError(
                                f"VideoWriter no pudo crear '{output_video_path}'. "
                                "Verifica el códec mp4v."
                            )
                    writer.write(output)
                    frames_written += 1
                else:
                    frames_written += 1
        finally:
            cap.release()
            if writer is not None:
                writer.release()

        total_elapsed = time.perf_counter() - start_time
        return {
            "frames_written": frames_written,
            "elapsed_seconds": total_elapsed,
            "fps": (frames_written / total_elapsed if total_elapsed > 0 else 0.0),
            "output_size": output_size,
        }
