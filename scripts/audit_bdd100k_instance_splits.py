"""Audit official BDD100K instance splits before any real Mask R-CNN training.

This checks split separation, exact image/bitmask pairing, raw RGBA encoding,
annotation IDs/flags and class coverage. It never downloads data or trains.
"""
import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image

CLASSES = (
    "pedestrian", "rider", "car", "truck", "bus", "train",
    "motorcycle", "bicycle",
)
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png"}


def indexed_files(directory, suffixes):
    directory = Path(directory)
    if not directory.is_dir():
        raise FileNotFoundError(f"Missing directory: {directory}")
    files = [p for p in directory.iterdir()
             if p.is_file() and p.suffix.lower() in suffixes]
    indexed = {}
    duplicates = []
    for path in files:
        if path.stem in indexed:
            duplicates.append(path.stem)
        indexed[path.stem] = path
    if duplicates:
        raise ValueError(f"Duplicate file stems in {directory}: {duplicates[:5]}")
    return indexed


def audit_split(name, images_dir, masks_dir, sample_limit=4):
    images = indexed_files(images_dir, IMAGE_SUFFIXES)
    masks = indexed_files(masks_dir, {".png"})
    missing_masks = sorted(set(images) - set(masks))
    orphan_masks = sorted(set(masks) - set(images))
    if missing_masks or orphan_masks:
        raise ValueError(
            f"{name}: image/mask mismatch; missing_masks={len(missing_masks)}, "
            f"orphan_masks={len(orphan_masks)}"
        )

    counts = Counter()
    total_instances = 0
    sampled = []
    for stem in sorted(images):
        image_path, mask_path = images[stem], masks[stem]
        with Image.open(image_path) as image:
            image_size = image.size
        with Image.open(mask_path) as mask:
            if mask.mode != "RGBA":
                raise ValueError(f"{mask_path} must be original RGBA, got {mask.mode}")
            if mask.size != image_size:
                raise ValueError(
                    f"Dimension mismatch for {stem}: image={image_size}, mask={mask.size}"
                )
            encoded = np.asarray(mask, dtype=np.uint8)

        category = encoded[..., 0]
        flags = encoded[..., 1]
        instance_ids = ((encoded[..., 2].astype(np.uint16) << 8)
                        | encoded[..., 3].astype(np.uint16))
        for instance_id in np.unique(instance_ids):
            if instance_id == 0:
                continue
            pixels = instance_ids == instance_id
            category_ids = np.unique(category[pixels])
            category_ids = category_ids[category_ids > 0]
            if category_ids.size != 1:
                raise ValueError(f"Invalid category encoding in {mask_path}, ann_id={instance_id}")
            class_id = int(category_ids[0])
            if class_id > len(CLASSES):
                raise ValueError(f"Unknown BDD100K instance class ID {class_id} in {mask_path}")
            if np.any((flags[pixels] & 0b11) != 0):
                continue
            counts[CLASSES[class_id - 1]] += 1
            total_instances += 1

        if len(sampled) < sample_limit:
            sampled.append(stem)

    return {
        "split": name,
        "images": len(images),
        "bitmasks": len(masks),
        "instances": total_instances,
        "instances_per_class": {class_name: counts[class_name] for class_name in CLASSES},
        "classes_present": [class_name for class_name in CLASSES if counts[class_name] > 0],
        "sample_stems": sampled,
    }, set(images)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-images", required=True)
    parser.add_argument("--train-bitmasks", required=True)
    parser.add_argument("--val-images", required=True)
    parser.add_argument("--val-bitmasks", required=True)
    parser.add_argument("--output", default="bdd100k_instance_preflight.json")
    parser.add_argument("--sample-limit", type=int, default=4)
    parser.add_argument("--allow-missing-train-classes", action="store_true",
                        help="Report but do not fail if one of the eight classes is absent in train.")
    args = parser.parse_args()

    train, train_stems = audit_split(
        "train", args.train_images, args.train_bitmasks, args.sample_limit
    )
    val, val_stems = audit_split(
        "val", args.val_images, args.val_bitmasks, args.sample_limit
    )
    overlap = sorted(train_stems & val_stems)
    if overlap:
        raise ValueError(
            f"Train/validation overlap detected ({len(overlap)} stems), examples: {overlap[:5]}"
        )
    missing_train = [name for name in CLASSES if train["instances_per_class"][name] == 0]
    report = {
        "dataset": "BDD100K official instance segmentation",
        "format": "RGBA bitmasks (R=category, G=flags, B:A=annotation ID)",
        "train": train,
        "val": val,
        "split_overlap": 0,
        "missing_train_classes": missing_train,
        "ready_for_training": bool(train["images"] and val["images"] and not missing_train),
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not train["images"] or not val["images"]:
        raise ValueError("Both official train and val splits must be non-empty.")
    if missing_train and not args.allow_missing_train_classes:
        raise ValueError(
            "Training preflight blocked: missing classes in train: "
            + ", ".join(missing_train)
        )
    print("RESULT: BDD100K OFFICIAL INSTANCE PREFLIGHT PASSED")


if __name__ == "__main__":
    main()
