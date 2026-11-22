import numpy as np
import pytest

from src.data_adapters import (
    decode_a2d2_instances, decode_a2d2_semantic, decode_urbansyn_panoptic,
    decode_urbansyn_semantic, load_a2d2_class_list, to_torchvision_target,
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
