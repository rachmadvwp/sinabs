"""
This module is meant to test a real use case. It will include testing of
the network equivalence, and of the correct output configuration.
"""

import samna
samna
# this is necessary as a workaround because of a problem
# that occurs when samna is imported after torch

from torch import nn
import torch
from sinabs.layers import NeuromorphicReLU
from sinabs.from_torch import from_model
from backend.Speck.tospeck import SpeckCompatibleNetwork


class SmartDoorClassifier(nn.Module):
    def __init__(
        self,
        quantize=False,
        linear_size=32,
        n_channels_in=2,
        n_channels_out=1,
    ):
        super().__init__()

        self.seq = [
            nn.Conv2d(
                in_channels=n_channels_in,
                out_channels=8,
                kernel_size=(3, 3),
                bias=False,
            ),
            NeuromorphicReLU(quantize=quantize, fanout=108),
            nn.AvgPool2d(kernel_size=(2, 2), stride=(2, 2)),
            nn.Conv2d(in_channels=8, out_channels=12, kernel_size=(3, 3), bias=False),
            NeuromorphicReLU(quantize=quantize, fanout=108),
            nn.AvgPool2d(kernel_size=(2, 2), stride=(2, 2)),
            nn.Conv2d(in_channels=12, out_channels=12, kernel_size=(3, 3), bias=False),
            NeuromorphicReLU(quantize=quantize, fanout=linear_size),
            nn.AvgPool2d(kernel_size=(2, 2), stride=(2, 2)),
            nn.Dropout2d(0.5),
            nn.Flatten(),
            nn.Linear(432, linear_size, bias=False),
            NeuromorphicReLU(quantize=quantize, fanout=1),
            nn.Linear(linear_size, n_channels_out, bias=False),
            NeuromorphicReLU(quantize=quantize, fanout=0),
        ]

        self.seq = nn.Sequential(*self.seq)

    def forward(self, x):
        return self.seq(x)


sdc = SmartDoorClassifier()
snn = from_model(sdc)

input_shape = (2, 64, 64)
input = torch.rand((1, *input_shape)) * 1000
snn.eval()
snn_out = snn(input)  # forward pass

snn.reset_states()
speck_net = SpeckCompatibleNetwork(snn, input_shape=input_shape, discretize=False)
speck_out = speck_net(input)

print("Snn out", snn_out.sum().item())
print("Speck out", speck_out.sum().item())

speck_config = speck_net.make_config(speck_layers_ordering=[8, 5, 4, 1, 3])
