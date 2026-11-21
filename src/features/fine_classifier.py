import os

import joblib
import numpy as np
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import GroupShuffleSplit
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

    def _features_from_roi(self, image_bgr: np.ndarray, roi_box: tuple[int, int, int, int]) -> np.ndarray:
        return np.concatenate([extract_hog_features(image_bgr, roi_box), extract_color_histogram(image_bgr, roi_box)]).astype(np.float32)

    def is_trained(self) -> bool:
        return self.model is not None

    def predict_roi(self, image_bgr, roi_box, base_class_name, base_score, subclasses_map=None):
        suffix = (subclasses_map or {}).get(base_class_name, base_class_name)
        if self.model is None:
            return f"{suffix}svm_untrained", 0.0
        features = self._features_from_roi(image_bgr, roi_box).reshape(1, -1)
        pred = str(self.model.predict(features)[0])
        decision = self.model.decision_function(features)
        margin = float(np.max(decision)) if np.ndim(decision) else float(decision)
        return pred, margin

    def train(self, samples: list[dict], max_rois_per_class: int = 120, random_seed: int = 42):
        rng = np.random.default_rng(random_seed)
        features, labels, groups = [], [], []
        for sample_idx, sample in enumerate(samples):
            for box, label in zip(sample["gt_boxes"], sample["gt_labels"]):
                features.append(self._features_from_roi(sample["image"], tuple(map(int, box))))
                labels.append(label)
                groups.append(sample.get("image_id", sample_idx))
        if not features:
            raise RuntimeError("No se encontraron ROIs para entrenar el clasificador.")
        x, y, groups = np.asarray(features, dtype=np.float32), np.asarray(labels), np.asarray(groups)
        if len(np.unique(groups)) < 2:
            raise ValueError("Se necesitan ROIs de al menos dos imágenes distintas para separar entrenamiento y validación sin fuga.")
        selected = []
        for cls in np.unique(y):
            indices = np.where(y == cls)[0]
            rng.shuffle(indices)
            selected.extend(indices[:max_rois_per_class].tolist())
        selected = np.asarray(selected, dtype=int)
        x, y, groups = x[selected], y[selected], groups[selected]
        splitter = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=random_seed)
        train_idx, val_idx = next(splitter.split(x, y, groups))
        train_classes = np.unique(y[train_idx])
        val_mask = np.isin(y[val_idx], train_classes)
        val_idx = val_idx[val_mask]
        if len(train_classes) < 2 or not len(val_idx):
            raise ValueError("La partición por imagen no dejó al menos dos clases de entrenamiento y muestras de validación evaluables; añade más imágenes.")
        self.model = make_pipeline(StandardScaler(), LinearSVC(C=1.0, max_iter=4000, dual=True))
        self.model.fit(x[train_idx], y[train_idx])
        self.known_prefixes = list(self.model.classes_)
        predictions = self.model.predict(x[val_idx])
        confusion = confusion_matrix(y[val_idx], predictions, labels=self.model.classes_)
        self.validation_accuracy = float(np.mean(predictions == y[val_idx]))
        self.validation_image_ids = sorted(set(groups[val_idx].tolist()))
        return sorted(self.known_prefixes), confusion

    def save(self):
        if self.model is None: return
        out_dir = os.path.dirname(self.model_path)
        if out_dir: os.makedirs(out_dir, exist_ok=True)
        joblib.dump(self.model, self.model_path)
