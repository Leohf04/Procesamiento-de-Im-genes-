import os

import joblib
import numpy as np
from sklearn.metrics import confusion_matrix
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC

from src.features.descriptors import extract_color_histogram, extract_hog_features


class FineGrainedClassifier:
    def __init__(self, model_path: str = "data/processed/fine_svm_classifier.joblib"):
        self.model_path = model_path
        self.model = None
        self.known_prefixes = []
        if os.path.isfile(self.model_path):
            self.model = joblib.load(self.model_path)
            self.known_prefixes = list(self.model.classes_)

    def _features_from_roi(
        self,
        image_bgr: np.ndarray,
        roi_box: tuple[int, int, int, int],
    ) -> np.ndarray:
        hog_feat = extract_hog_features(image_bgr, roi_box)
        color_feat = extract_color_histogram(image_bgr, roi_box)
        return np.concatenate([hog_feat, color_feat]).astype(np.float32)

    def is_trained(self) -> bool:
        return self.model is not None

    def predict_roi(
        self,
        image_bgr: np.ndarray,
        roi_box: tuple[int, int, int, int],
        base_class_name: str,
        base_score: float,
        subclasses_map: dict[str, str] | None = None,
    ) -> tuple[str, float]:
        subclasses_map = subclasses_map or {}
        default_suffix = subclasses_map.get(base_class_name, base_class_name)

        if self.model is None:
            return f"{default_suffix}svm_untrained", 0.0

        features = self._features_from_roi(image_bgr, roi_box).reshape(1, -1)
        pred = str(self.model.predict(features)[0])
        margin = float(self.model.decision_function(features)[0].max())
        return pred, margin

    def train(
        self,
        samples: list[dict],
        max_rois_per_class: int = 120,
        random_seed: int = 42,
    ) -> tuple[list[str], "np.ndarray"]:
        rng = np.random.default_rng(random_seed)
        features_list = []
        labels_list: list[str] = []

        for sample in samples:
            image = sample["image"]
            for roi_box, cn in zip(sample["gt_boxes"], sample["gt_labels"]):
                features_list.append(
                    self._features_from_roi(image, tuple(map(int, roi_box)))
                )
                labels_list.append(cn)

        if not features_list:
            raise RuntimeError(
                "No se encontraron ROIs de entrenamiento en las muestras cargadas."
            )

        feats_np = np.array(features_list, dtype=np.float32)
        labels_np = np.array(labels_list)

        selected_idx = []
        for cname in np.unique(labels_np):
            class_indices = np.where(labels_np == cname)[0]
            rng.shuffle(class_indices)
            selected_idx.extend(class_indices[:max_rois_per_class].tolist())

        x_train = feats_np[selected_idx]
        y_train = labels_np[selected_idx]

        self.model = make_pipeline(
            StandardScaler(), LinearSVC(C=1.0, max_iter=4000, dual=True)
        )
        self.model.fit(x_train, y_train)
        self.known_prefixes = list(self.model.classes_)

        confusion = confusion_matrix(y_train, self.model.predict(x_train))
        return sorted(self.known_prefixes), confusion

    def save(self) -> None:
        if self.model is None:
            return
        out_dir = os.path.dirname(self.model_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        joblib.dump(self.model, self.model_path)
