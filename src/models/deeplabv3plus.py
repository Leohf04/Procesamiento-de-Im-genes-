"""DeepLabV3+ implementation with a ResNet-50 encoder (output stride 16)."""
import torch
from torch import nn
from torch.nn import functional as F
from torchvision.models import ResNet50_Weights, resnet50


class ASPP(nn.Module):
    def __init__(self, in_channels: int, out_channels: int = 256, rates=(6, 12, 18)):
        super().__init__()
        branches = [nn.Sequential(nn.Conv2d(in_channels, out_channels, 1, bias=False),
                                  nn.BatchNorm2d(out_channels), nn.ReLU(inplace=True))]
        for rate in rates:
            branches.append(nn.Sequential(
                nn.Conv2d(in_channels, out_channels, 3, padding=rate, dilation=rate, bias=False),
                nn.BatchNorm2d(out_channels), nn.ReLU(inplace=True)))
        self.global_pool = nn.Sequential(nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(in_channels, out_channels, 1, bias=False),
            nn.ReLU(inplace=True))
        self.branches = nn.ModuleList(branches)
        self.project = nn.Sequential(nn.Conv2d(out_channels * (len(branches) + 1), out_channels, 1, bias=False),
                                     nn.BatchNorm2d(out_channels), nn.ReLU(inplace=True), nn.Dropout(0.1))

    def forward(self, x):
        size = x.shape[-2:]
        pooled = F.interpolate(self.global_pool(x), size=size, mode="bilinear", align_corners=False)
        return self.project(torch.cat([*(branch(x) for branch in self.branches), pooled], dim=1))


class DeepLabV3Plus(nn.Module):
    """DeepLabV3+ decoder; returns logits resized to the input image resolution."""
    def __init__(self, num_classes: int, pretrained_backbone: bool = True):
        super().__init__()
        weights = ResNet50_Weights.DEFAULT if pretrained_backbone else None
        encoder = resnet50(weights=weights, replace_stride_with_dilation=[False, False, True])
        self.stem = nn.Sequential(encoder.conv1, encoder.bn1, encoder.relu, encoder.maxpool)
        self.layer1, self.layer2, self.layer3, self.layer4 = encoder.layer1, encoder.layer2, encoder.layer3, encoder.layer4
        self.aspp = ASPP(2048, 256)
        self.low_projection = nn.Sequential(nn.Conv2d(256, 48, 1, bias=False),
                                             nn.BatchNorm2d(48), nn.ReLU(inplace=True))
        self.decoder = nn.Sequential(
            nn.Conv2d(304, 256, 3, padding=1, bias=False), nn.BatchNorm2d(256), nn.ReLU(inplace=True),
            nn.Conv2d(256, 256, 3, padding=1, bias=False), nn.BatchNorm2d(256), nn.ReLU(inplace=True),
            nn.Dropout(0.1), nn.Conv2d(256, num_classes, 1))

    def forward(self, x):
        input_size = x.shape[-2:]
        x = self.stem(x)
        low = self.layer1(x)
        x = self.layer4(self.layer3(self.layer2(low)))
        x = self.aspp(x)
        x = F.interpolate(x, size=low.shape[-2:], mode="bilinear", align_corners=False)
        logits = self.decoder(torch.cat([x, self.low_projection(low)], dim=1))
        return {"out": F.interpolate(logits, size=input_size, mode="bilinear", align_corners=False)}
