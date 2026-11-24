import numpy as np
import pytest

from src.data_adapters import (
    A2D2InstanceDataset, A2D2SemanticDataset, UrbanSynInstanceDataset,
    UrbanSynSemanticDataset, decode_a2d2_instances, decode_a2d2_semantic,
    decode_urbansyn_panoptic, decode_urbansyn_semantic, load_a2d2_class_list,
    detection_collate_fn, to_torchvision_target,
)


def test_a2d2_color_map_semantic_and_ignore():
    colors = load_a2d2_class_list({"#ff0000": "Car 1", "#00ff00": "Solid line"})
    mask = np.zeros((8, 10, 3), dtype=np.uint8)
    mask[1:5, 2:7] = (255, 0, 0)
    mask[6, 1:9] = (0, 255, 0)
    decoded = decode_a2d2_semantic(mask, colors)
    assert decoded[2, 3] == 6
    assert decoded[6, 3] == 12
    assert decoded[0, 0] == 255


def test_a2d2_subclass_components_become_separate_instances():
    colors = load_a2d2_class_list({"#ff0000": "Pedestrian 1"})
    mask = np.zeros((20, 30, 3), dtype=np.uint8)
    mask[2:7, 2:6] = (255, 0, 0)
    mask[12:18, 20:26] = (255, 0, 0)
    decoded = decode_a2d2_instances(mask, colors, min_component_area=4)
    assert decoded["masks"].shape == (2, 20, 30)
    assert decoded["labels"].tolist() == [3, 3]
    assert decoded["boxes"].tolist() == [[2, 2, 6, 7], [20, 12, 26, 18]]


def test_urbansyn_semantic_rgb_and_mapping():
    ids = np.zeros((5, 6), dtype=np.uint8)
    ids[1:3, 2:4] = 11
    rgb = np.repeat(ids[..., None], 3, axis=2)
    decoded = decode_urbansyn_semantic(rgb, {0: 0, 11: 6})
    assert decoded[1, 2] == 6
    assert decoded[0, 0] == 0
    with pytest.raises(ValueError):
        decode_urbansyn_semantic(np.dstack([ids, ids, ids + 1]))


def test_urbansyn_panoptic_rg_instance_blue_class():
    pan = np.zeros((12, 16, 3), dtype=np.uint8)
    pan[1:5, 2:7, 0] = 0
    pan[1:5, 2:7, 1] = 1
    pan[1:5, 2:7, 2] = 11
    pan[7:10, 10:14, 0] = 0
    pan[7:10, 10:14, 1] = 2
    pan[7:10, 10:14, 2] = 12
    decoded = decode_urbansyn_panoptic(pan, {11: 6, 12: 3})
    assert decoded["masks"].shape == (2, 12, 16)
    assert decoded["labels"].tolist() == [6, 3]
    assert decoded["boxes"].tolist() == [[2, 1, 7, 5], [10, 7, 14, 10]]


def test_maskrcnn_target_has_expected_tensor_contract():
    decoded = {"masks": np.ones((1, 4, 5), np.uint8), "boxes": np.array([[0, 0, 5, 4]], np.float32),
               "labels": np.array([1]), "area": np.array([20], np.float32), "iscrowd": np.array([0])}
    target = to_torchvision_target(decoded, image_id=7)
    assert target["boxes"].shape == (1, 4)
    assert target["masks"].dtype.name == "uint8" if hasattr(target["masks"].dtype, "name") else str(target["masks"].dtype) == "torch.uint8"
    assert target["image_id"].item() == 7


def test_deeplab_and_maskrcnn_forward_backward_smoke():
    torch = pytest.importorskip("torch")
    torchvision = pytest.importorskip("torchvision")
    from src.models.deeplabv3plus import DeepLabV3Plus
    from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
    from torchvision.models.detection.mask_rcnn import MaskRCNNPredictor

    # Semantic segmentation: real architecture, synthetic batch/labels, one optimizer step.
    semantic = DeepLabV3Plus(num_classes=4, pretrained_backbone=False).train()
    image = torch.randn(1, 3, 64, 64)
    source_semantic = np.zeros((64, 64), dtype=np.uint8)
    source_semantic[16:48, 16:48] = 1
    labels = torch.from_numpy(decode_urbansyn_semantic(source_semantic, {0: 0, 1: 1}).astype(np.int64))[None]
    loss = torch.nn.functional.cross_entropy(semantic(image)["out"], labels)
    loss.backward()
    assert torch.isfinite(loss)

    # Instance segmentation: torchvision Mask R-CNN with project-style targets.
    model = torchvision.models.detection.maskrcnn_resnet50_fpn(
        weights=None, weights_backbone=None, min_size=64, max_size=64
    )
    box_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(box_features, 3)
    mask_features = model.roi_heads.mask_predictor.conv5_mask.in_channels
    model.roi_heads.mask_predictor = MaskRCNNPredictor(mask_features, 256, 3)
    model.train()
    img = torch.rand(3, 64, 64)
    panoptic = np.zeros((64, 64, 3), dtype=np.uint8)
    panoptic[8:48, 8:35, 1] = 1  # instance ID = R*256 + G
    panoptic[8:48, 8:35, 2] = 11  # source class ID in blue channel
    decoded_instances = decode_urbansyn_panoptic(panoptic, {11: 1})
    target = to_torchvision_target(decoded_instances, image_id=0)
    losses = model([img], [target])
    total = sum(losses.values())
    total.backward()
    assert all(torch.isfinite(value) for value in losses.values())


def test_empty_instance_masks_return_valid_empty_targets():
    colors = load_a2d2_class_list({"#ff0000": "Car 1"})
    decoded = decode_a2d2_instances(np.zeros((5, 7, 3), dtype=np.uint8), colors)
    assert decoded["masks"].shape == (0, 5, 7)
    assert decoded["boxes"].shape == (0, 4)
    assert decoded["area"].shape == (0,)


def test_manifest_datasets_load_a2d2_and_urbansyn(tmp_path):
    from PIL import Image

    rgb = np.zeros((12, 16, 3), dtype=np.uint8)
    rgb[..., 0] = 120
    a2_mask = np.zeros_like(rgb)
    a2_mask[2:7, 3:8] = (255, 0, 0)
    pan = np.zeros_like(rgb)
    pan[2:7, 3:8, 1] = 1
    pan[2:7, 3:8, 2] = 11
    sem = np.zeros((12, 16), dtype=np.uint8)
    sem[2:7, 3:8] = 11

    for name, array in [("rgb.png", rgb), ("a2.png", a2_mask),
                        ("pan.png", pan), ("sem.png", np.repeat(sem[..., None], 3, axis=2))]:
        Image.fromarray(array).save(tmp_path / name)

    colors = load_a2d2_class_list({"#ff0000": "Car 1"})
    a2_sem = A2D2SemanticDataset(
        [{"image": str(tmp_path / "rgb.png"), "semantic": str(tmp_path / "a2.png")}],
        colors, size=(8, 10))
    image, semantic = a2_sem[0]
    assert image.shape == (3, 8, 10) and semantic.shape == (8, 10)

    a2_inst = A2D2InstanceDataset(
        [{"image": str(tmp_path / "rgb.png"), "instance": str(tmp_path / "a2.png")}],
        colors, min_component_area=1)
    image, target = a2_inst[0]
    assert image.shape == (3, 12, 16) and target["masks"].shape == (1, 12, 16)

    us_sem = UrbanSynSemanticDataset(
        [{"image": str(tmp_path / "rgb.png"), "semantic": str(tmp_path / "sem.png")}],
        {0: 0, 11: 1})
    image, semantic = us_sem[0]
    assert semantic.shape == (12, 16) and semantic[3, 4].item() == 1

    us_inst = UrbanSynInstanceDataset(
        [{"image": str(tmp_path / "rgb.png"), "panoptic": str(tmp_path / "pan.png")}],
        {11: 1})
    image, target = us_inst[0]
    assert target["boxes"].tolist() == [[3, 2, 8, 7]]


def test_detection_collate_keeps_variable_targets_as_lists():
    import torch
    image_a, image_b = torch.zeros(3, 8, 8), torch.zeros(3, 8, 8)
    target_a, target_b = {"boxes": torch.zeros(0, 4)}, {"boxes": torch.ones(1, 4)}
    images, targets = detection_collate_fn([(image_a, target_a), (image_b, target_b)])
    assert len(images) == 2 and len(targets) == 2
    assert targets[0]["boxes"].shape == (0, 4)
    assert targets[1]["boxes"].shape == (1, 4)
