import samna
# this is necessary as a workaround because of a problem
# that occurs when samna is imported after other libraries

from sinabs.backend.Speck import SpeckCompatibleNetwork
from torch import nn
from sinabs.from_torch import from_model
import sinabs.layers as sl
import torch


class SmartDoorClassifier(nn.Module):
    def __init__(self, quantize=False, linear_size=32,
                 n_channels_in=2, n_channels_out=1):
        super().__init__()

        self.seq = [
            nn.Conv2d(in_channels=n_channels_in, out_channels=8,
                      kernel_size=(3, 3), bias=False),
            nn.ReLU(),
            sl.SumPooling2dLayer(
                image_shape=(64, 64), pool_size=(2, 2), layer_name="pool1"
            ),
            nn.Conv2d(in_channels=8, out_channels=12,
                      kernel_size=(3, 3), bias=False),
            nn.ReLU(),
            sl.SumPooling2dLayer(
                image_shape=(64, 64), pool_size=(2, 2), layer_name="pool1"
            ),
            nn.Conv2d(in_channels=12, out_channels=12,
                      kernel_size=(3, 3), bias=False),
            nn.ReLU(),
            nn.Conv2d(in_channels=12, out_channels=12,
                      kernel_size=(3, 3), bias=False),
            nn.ReLU(),
            # sl.SumPooling2dLayer(
            #     image_shape=(24, 24), pool_size=(2, 2), layer_name="pool1"
            # ),
            # nn.Dropout2d(0.5),
            # nn.Flatten(),
            # nn.Linear(432, linear_size, bias=False),
            # nn.ReLU(),
            # nn.Linear(linear_size, n_channels_out, bias=False),
        ]

        self.seq = nn.Sequential(*self.seq)

    def forward(self, x):
        return self.seq(x)


def test_initialized_network():
    input_shape = (4, 64, 64)
    cnn = SmartDoorClassifier(n_channels_in=input_shape[0])
    snn = from_model(cnn)

    input = torch.rand((1, *input_shape))
    snn(input)  # forward pass

    speck_config = SpeckCompatibleNetwork(snn, input_shape=input_shape).get_config()
