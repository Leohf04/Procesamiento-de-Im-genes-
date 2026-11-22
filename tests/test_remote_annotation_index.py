import numpy as np
from scripts.index_remote_annotations import (
    class_pixel_counts, instance_counts, summarize_a2d2_mask, summarize_urbansyn_masks
)
from src.urban_ontology import load_urban_ontology, source_instance_map, source_semantic_map

def test_pixel_counts_skip_ignore_and_unknown():
    assert class_pixel_counts(np.array([[0,0,255],[3,3,9]],dtype=np.uint8),{0:"road",3:"car"}) == {"car":2,"road":2}

def test_instance_counts_by_class():
    assert instance_counts({"labels":np.array([3,3,1,8])},{1:"person",3:"car",8:"bicycle"}) == {"bicycle":1,"car":2,"person":1}

def test_urbansyn_synthetic_semantic_and_panoptic_masks():
    sem=np.array([[0,13,19],[11,18,255]],dtype=np.uint8)
    pan=np.zeros((2,3,3),dtype=np.uint8)
    pan[0,1]=[0,1,13]; pan[1,1]=[0,2,18]
    ontology=load_urban_ontology()
    result=summarize_urbansyn_masks(sem,pan,source_semantic_map("urbansyn",ontology),source_instance_map("urbansyn",ontology))
    assert result["semantic_pixels"] == {"bicycle":1,"car":1,"person":1,"road":1}
    assert result["instance_counts"] == {"bicycle":1,"car":1}

def test_a2d2_synthetic_rgb_mask():
    colors={(0,0,0):"road",(1,2,3):"Car 1",(4,5,6):"Pedestrian 1",(7,8,9):"Bicycle 1"}
    rgb=np.zeros((8,8,3),dtype=np.uint8)
    rgb[0:4,0:4]=(1,2,3); rgb[4:6,0:2]=(4,5,6); rgb[4:6,4:6]=(7,8,9)
    result=summarize_a2d2_mask(rgb,colors,{"road":0,"car":13,"person":11,"bicycle":18},{"car":3,"person":1,"bicycle":8})
    assert result["semantic_pixels"] == {"bicycle":4,"car":16,"person":4,"road":40}
    assert result["instance_counts"] == {"bicycle":1,"car":1,"person":1}

def test_a2d2_static_classes_are_preserved_by_shared_normalizer():
    from src.data_adapters import normalize_class_name
    assert normalize_class_name("Building") == "building"
    assert normalize_class_name("Vegetation") == "vegetation"
    assert normalize_class_name("Traffic sign") == "traffic sign"
    assert normalize_class_name("Solid line") == "lane marking"

def test_a2d2_bus_instances_are_not_dropped():
    colors = {(1, 2, 3): "Bus 1"}
    rgb = np.zeros((6, 6, 3), dtype=np.uint8)
    rgb[1:5, 1:5] = (1, 2, 3)
    result = summarize_a2d2_mask(rgb, colors, {"bus": 15}, {"bus": 5})
    assert result["instance_counts"] == {"bus": 1}
