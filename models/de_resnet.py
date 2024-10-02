# https://github.com/hq-deng/RD4AD/blob/main/de_resnet.py
from torch import Tensor
import torch.nn as nn
try:
    from torch.hub import load_state_dict_from_url
except ImportError:
    from torch.utils.model_zoo import load_url as load_state_dict_from_url
from typing import Type, Any, Callable, Union, List, Optional

__all__ = ['ResNet', 'de_resnet18', 'de_resnet34', 'de_resnet50', 'resnet101', 'resnet152', 'resnext50_32x4d', 'resnext101_32x8d', 'de_wide_resnet50_2', 'de_wide_resnet101_2']
model_urls = {'resnet18': 'https://download.pytorch.org/models/resnet18-f37072fd.pth', 'resnet34': 'https://download.pytorch.org/models/resnet34-b627a593.pth',
              'resnet50': 'https://download.pytorch.org/models/resnet50-0676ba61.pth', 'resnet101': 'https://download.pytorch.org/models/resnet101-63fe2227.pth',
              'resnet152': 'https://download.pytorch.org/models/resnet152-394f9c45.pth', 'resnext50_32x4d': 'https://download.pytorch.org/models/resnext50_32x4d-7cdf4587.pth',
              'resnext101_32x8d': 'https://download.pytorch.org/models/resnext101_32x8d-8ba56ff5.pth', 'wide_resnet50_2': 'https://download.pytorch.org/models/wide_resnet50_2-95faca4d.pth',
              'wide_resnet101_2': 'https://download.pytorch.org/models/wide_resnet101_2-32ee1156.pth'}

def conv3x3(in_planes: int, out_planes: int, stride: int = 1, groups: int = 1, dilation: int = 1) -> nn.Conv2d:
    return nn.Conv2d(in_planes, out_planes, kernel_size=3, stride=stride, padding=dilation, groups=groups, bias=False, dilation=dilation)

def conv1x1(in_planes: int, out_planes: int, stride: int = 1) -> nn.Conv2d:
    return nn.Conv2d(in_planes, out_planes, kernel_size=1, stride=stride, bias=False)

def deconv2x2(in_planes: int, out_planes: int, stride: int = 1, groups: int = 1, dilation: int = 1) -> nn.Conv2d:
    return nn.ConvTranspose2d(in_planes, out_planes, kernel_size=2, stride=stride, groups=groups, bias=False, dilation=dilation)

class BasicBlock(nn.Module):
    expansion: int = 1

    def __init__(self, inplanes: int, planes: int, stride: int = 1, upsample: Optional[nn.Module] = None, groups: int = 1, base_width: int = 64, dilation: int = 1, norm_layer: Optional[Callable[..., nn.Module]] = None) -> None:
        super(BasicBlock, self).__init__()
        if norm_layer is None:
            norm_layer = nn.BatchNorm2d
        if groups != 1 or base_width != 64:
            raise ValueError('BasicBlock only supports groups=1 and base_width=64')
        if dilation > 1:
            raise NotImplementedError("Dilation > 1 not supported in BasicBlock")
        if stride == 2:
            self.conv1 = deconv2x2(inplanes, planes, stride)
        else:
            self.conv1 = conv3x3(inplanes, planes, stride)
        self.bn1 = norm_layer(planes)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = conv3x3(planes, planes)
        self.bn2 = norm_layer(planes)
        self.upsample = upsample
        self.stride = stride

    def forward(self, x: Tensor) -> Tensor:
        identity = x
        # block 1
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        # block 2
        out = self.conv2(out)
        out = self.bn2(out)
        if self.upsample is not None:
            identity = self.upsample(x)
        # skip connection
        out += identity
        out = self.relu(out)
        return out

class Bottleneck(nn.Module):
    expansion: int = 4

    def __init__(self, inplanes: int, planes: int, stride: int = 1, upsample: Optional[nn.Module] = None, groups: int = 1, base_width: int = 64, dilation: int = 1, norm_layer: Optional[Callable[..., nn.Module]] = None) -> None:
        super(Bottleneck, self).__init__()
        if norm_layer is None:
            norm_layer = nn.BatchNorm2d
        width = int(planes * (base_width / 64.)) * groups
        self.conv1 = conv1x1(inplanes, width)
        self.bn1 = norm_layer(width)
        if stride == 2:
            self.conv2 = deconv2x2(width, width, stride, groups, dilation)
        else:
            self.conv2 = conv3x3(width, width, stride, groups, dilation)
        self.bn2 = norm_layer(width)
        self.conv3 = conv1x1(width, planes * self.expansion)
        self.bn3 = norm_layer(planes * self.expansion)
        self.relu = nn.ReLU(inplace=True)
        self.upsample = upsample
        self.stride = stride

    def forward(self, x: Tensor) -> Tensor:
        identity = x
        # block 1
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        # block 2
        out = self.conv2(out)
        out = self.bn2(out)
        out = self.relu(out)
        # block 3
        out = self.conv3(out)
        out = self.bn3(out)
        if self.upsample is not None:
            identity = self.upsample(x)
        # skip connection
        out += identity
        out = self.relu(out)
        return out

class ResNet(nn.Module):
    def __init__(self, block: Type[Union[BasicBlock, Bottleneck]], layers: List[int], num_classes: int = 1000, zero_init_residual: bool = False, groups: int = 1, width_per_group: int = 64, replace_stride_with_dilation: Optional[List[bool]] = None, norm_layer: Optional[Callable[..., nn.Module]] = None) -> None:
        super(ResNet, self).__init__()
        if norm_layer is None:
            norm_layer = nn.BatchNorm2d
        self._norm_layer = norm_layer
        self.inplanes = 512 * block.expansion
        self.dilation = 1
        if replace_stride_with_dilation is None:
            replace_stride_with_dilation = [False, False, False]
        if len(replace_stride_with_dilation) != 3:
            raise ValueError("replace_stride_with_dilation should be None or a 3-element tuple, got {}".format(replace_stride_with_dilation))
        self.groups = groups
        self.base_width = width_per_group
        self.layer1 = self._make_layer(block, 256, layers[0], stride=2)
        self.layer2 = self._make_layer(block, 128, layers[1], stride=2, dilate=replace_stride_with_dilation[0])
        self.layer3 = self._make_layer(block, 64, layers[2], stride=2, dilate=replace_stride_with_dilation[1])
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
            elif isinstance(m, (nn.BatchNorm2d, nn.GroupNorm)):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
        if zero_init_residual:
            for m in self.modules():
                if isinstance(m, Bottleneck):
                    nn.init.constant_(m.bn3.weight, 0)
                elif isinstance(m, BasicBlock):
                    nn.init.constant_(m.bn2.weight, 0)

    def _make_layer(self, block: Type[Union[BasicBlock, Bottleneck]], planes: int, blocks: int, stride: int = 1, dilate: bool = False) -> nn.Sequential:
        norm_layer = self._norm_layer
        upsample = None
        previous_dilation = self.dilation
        if dilate:
            self.dilation *= stride
            stride = 1
        if stride != 1 or self.inplanes != planes * block.expansion:
            upsample = nn.Sequential(deconv2x2(self.inplanes, planes * block.expansion, stride), norm_layer(planes * block.expansion))
        layers = []
        layers.append(block(self.inplanes, planes, stride, upsample, self.groups, self.base_width, previous_dilation, norm_layer))
        self.inplanes = planes * block.expansion
        for _ in range(1, blocks):
            layers.append(block(self.inplanes, planes, groups=self.groups, base_width=self.base_width, dilation=self.dilation, norm_layer=norm_layer))
        return nn.Sequential(*layers)

    def _forward_impl(self, x: Tensor) -> Tensor:
        feature_a = self.layer1(x)
        feature_b = self.layer2(feature_a)
        feature_c = self.layer3(feature_b)
        # feature_d = self.layer4(feature_c)
        return [feature_c, feature_b, feature_a]

    def forward(self, x: Tensor) -> Tensor:
        return self._forward_impl(x)

def _resnet(arch: str, block: Type[Union[BasicBlock, Bottleneck]], layers: List[int], pretrained: bool, progress: bool, **kwargs: Any) -> ResNet:
    model = ResNet(block, layers, **kwargs)
    if pretrained:
        state_dict = load_state_dict_from_url(model_urls[arch], progress=progress)
        model.load_state_dict(state_dict)
    return model

def de_resnet18(pretrained: bool = False, progress: bool = True, **kwargs: Any) -> ResNet:
    return _resnet('resnet18', BasicBlock, [2, 2, 2, 2], pretrained, progress, **kwargs)

def de_resnet34(pretrained: bool = False, progress: bool = True, **kwargs: Any) -> ResNet:
    return _resnet('resnet34', BasicBlock, [3, 4, 6, 3], pretrained, progress, **kwargs)

def de_resnet50(pretrained: bool = False, progress: bool = True, **kwargs: Any) -> ResNet:
    return _resnet('resnet50', Bottleneck, [3, 4, 6, 3], pretrained, progress, **kwargs)

def resnet101(pretrained: bool = False, progress: bool = True, **kwargs: Any) -> ResNet:
    return _resnet('resnet101', Bottleneck, [3, 4, 23, 3], pretrained, progress, **kwargs)

def resnet152(pretrained: bool = False, progress: bool = True, **kwargs: Any) -> ResNet:
    return _resnet('resnet152', Bottleneck, [3, 8, 36, 3], pretrained, progress, **kwargs)

def resnext50_32x4d(pretrained: bool = False, progress: bool = True, **kwargs: Any) -> ResNet:
    kwargs['groups'] = 32
    kwargs['width_per_group'] = 4
    return _resnet('resnext50_32x4d', Bottleneck, [3, 4, 6, 3], pretrained, progress, **kwargs)

def resnext101_32x8d(pretrained: bool = False, progress: bool = True, **kwargs: Any) -> ResNet:
    kwargs['groups'] = 32
    kwargs['width_per_group'] = 8
    return _resnet('resnext101_32x8d', Bottleneck, [3, 4, 23, 3], pretrained, progress, **kwargs)

def de_wide_resnet50_2(pretrained: bool = False, progress: bool = True, **kwargs: Any) -> ResNet:
    kwargs['width_per_group'] = 64 * 2
    return _resnet('wide_resnet50_2', Bottleneck, [3, 4, 6, 3], pretrained, progress, **kwargs)

def de_wide_resnet101_2(pretrained: bool = False, progress: bool = True, **kwargs: Any) -> ResNet:
    kwargs['width_per_group'] = 64 * 2
    return _resnet('wide_resnet101_2', Bottleneck, [3, 4, 23, 3], pretrained, progress, **kwargs)