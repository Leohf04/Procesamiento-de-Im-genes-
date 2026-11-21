"""Export a trained DeepLabV3+ checkpoint to ONNX logits."""
import argparse
from pathlib import Path
import torch
from src.models.deeplabv3plus import DeepLabV3Plus


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--classes", type=int, default=11)
    parser.add_argument("--height", type=int, default=512)
    parser.add_argument("--width", type=int, default=1024)
    args = parser.parse_args()
    checkpoint = torch.load(args.checkpoint, map_location="cpu")
    model = DeepLabV3Plus(args.classes, pretrained_backbone=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    dummy = torch.randn(1, 3, args.height, args.width)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    torch.onnx.export(model, dummy, str(output), input_names=["image"], output_names=["logits"],
                      opset_version=17, dynamic_axes={"image": {0: "batch"}, "logits": {0: "batch"}})
    print(f"ONNX exportado: {output}")


if __name__ == "__main__":
    main()
