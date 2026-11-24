import numpy as np
import torch
from PIL import Image

from src.urban_geometry import letterbox_geometry, letterbox_image, letterbox_mask
from src.urban_optimizer import build_optimizer_and_scheduler


def test_protocol_optimizer_and_scheduler_are_created_without_step():
    model = torch.nn.Linear(3, 2)
    semantic, semantic_scheduler = build_optimizer_and_scheduler(
        model, "semantic", {"learning_rate": 1e-3}
    )
    instances, instance_scheduler = build_optimizer_and_scheduler(
        model, "instances", {"learning_rate": 1e-3}
    )
    assert isinstance(semantic, torch.optim.AdamW)
    assert isinstance(instances, torch.optim.SGD)
    for scheduler in (semantic_scheduler, instance_scheduler):
        assert isinstance(scheduler, torch.optim.lr_scheduler.ReduceLROnPlateau)
        assert scheduler.mode == "max"
        assert scheduler.patience == 2
    assert all(parameter.grad is None for parameter in model.parameters())


def test_letterbox_geometry_preserves_aspect_and_maps_boxes():
    geometry = letterbox_geometry((100, 200), (512, 512))
    assert (geometry.resized_height, geometry.resized_width) == (256, 512)
    assert (geometry.top, geometry.left) == (128, 0)
    boxes = geometry.boxes_xyxy(np.array([[40, 20, 100, 60]], dtype=np.float32))
    np.testing.assert_allclose(boxes, [[102.4, 179.2, 256.0, 281.6]], atol=1e-4)


def test_letterbox_image_and_semantic_mask_use_consistent_padding():
    image = Image.fromarray(np.full((100, 200, 3), 127, dtype=np.uint8), "RGB")
    image_out, image_geometry = letterbox_image(image, (512, 512))
    mask_out, mask_geometry = letterbox_mask(
        np.full((100, 200), 7, dtype=np.uint8), (512, 512), fill_value=255
    )
    assert image_out.size == (512, 512)
    assert image_geometry == mask_geometry
    image_array = np.asarray(image_out)
    assert image_array[0, 0].tolist() == [0, 0, 0]
    assert image_array[128, 20].tolist() == [127, 127, 127]
    assert mask_out.shape == (512, 512)
    assert int(mask_out[0, 0]) == 255
    assert int(mask_out[128, 20]) == 7


def test_letterbox_instance_mask_background_padding():
    source = np.zeros((100, 200), dtype=np.uint8)
    source[20:60, 40:100] = 3
    transformed, _ = letterbox_mask(source, (512, 512), fill_value=0)
    assert transformed.shape == (512, 512)
    assert set(np.unique(transformed)).issubset({0, 3})
    assert int(transformed[0, 0]) == 0
    assert int((transformed == 3).sum()) > 0
