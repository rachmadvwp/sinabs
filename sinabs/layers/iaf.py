import torch
from copy import deepcopy
from typing import Optional, Callable
from sinabs.activation import ActivationFunction
from .reshape import SqueezeMixin
from .lif import LIF, LIFRecurrent
import numpy as np


class IAF(LIF):
    """
    Pytorch implementation of a Integrate and Fire neuron with learning enabled.

    Parameters
    ----------
    spike_threshold: float
        Spikes are emitted if v_mem is above that threshold. By default set to 1.0.
    activation_fn: Callable
        a sinabs.activation.ActivationFunction to provide spiking and reset mechanism. Also defines a surrogate gradient.
    tau_syn: float
        Synaptic decay time constants. If None, no synaptic dynamics are used, which is the default.
    min_v_mem: float or None
        Lower bound for membrane potential v_mem, clipped at every time step.
    shape: torch.Size
        Optionally initialise the layer state with given shape. If None, will be inferred from input_size.
    """

    def __init__(
        self,
        spike_threshold: float = 1.0,
        activation_fn: Callable = ActivationFunction(),
        tau_syn: Optional[float] = None,
        min_v_mem: Optional[float] = None,
        shape: Optional[torch.Size] = None,
    ):
        super().__init__(
            tau_mem=np.inf,
            tau_syn=tau_syn,
            spike_threshold=spike_threshold,
            activation_fn=activation_fn,
            min_v_mem=min_v_mem,
            shape=shape,
            norm_input=False,
        )
        # deactivate tau_mem being learned
        self.tau_mem.requires_grad = False

    @property
    def _param_dict(self) -> dict:
        param_dict = super()._param_dict
        param_dict.pop("tau_mem")
        param_dict.pop("train_alphas")
        param_dict.pop("norm_input")
        return param_dict


class IAFRecurrent(LIFRecurrent):
    """
    Pytorch implementation of a Integrate and Fire neuron with learning enabled.

    Parameters
    ----------
    rec_connect: torch.nn.Module
        An nn.Module which defines the recurrent connectivity, e.g. nn.Linear
    spike_threshold: float
        Spikes are emitted if v_mem is above that threshold. By default set to 1.0.
    activation_fn: Callable
        a sinabs.activation.ActivationFunction to provide spiking and reset mechanism. Also defines a surrogate gradient.
    tau_syn: float
        Synaptic decay time constants. If None, no synaptic dynamics are used, which is the default.
    min_v_mem: float or None
        Lower bound for membrane potential v_mem, clipped at every time step.
    shape: torch.Size
        Optionally initialise the layer state with given shape. If None, will be inferred from input_size.
    """

    def __init__(
        self,
        rec_connect: torch.nn.Module,
        spike_threshold: float = 1.0,
        activation_fn: Callable = ActivationFunction(),
        tau_syn: Optional[float] = None,
        min_v_mem: Optional[float] = None,
        shape: Optional[torch.Size] = None,
    ):
        super().__init__(
            rec_connect=rec_connect,
            tau_mem=np.inf,
            tau_syn=tau_syn,
            spike_threshold=spike_threshold,
            activation_fn=activation_fn,
            min_v_mem=min_v_mem,
            shape=shape,
            norm_input=False,
        )
        # deactivate tau_mem being learned
        self.tau_mem.requires_grad = False

    @property
    def _param_dict(self) -> dict:
        param_dict = super()._param_dict
        param_dict.pop("tau_mem")
        param_dict.pop("train_alphas")
        param_dict.pop("norm_input")
        return param_dict


class IAFSqueeze(IAF, SqueezeMixin):
    """
    Same as parent IAF class, only takes in squeezed 4D input (Batch*Time, Channel, Height, Width)
    instead of 5D input (Batch, Time, Channel, Height, Width) in order to be compatible with
    layers that can only take a 4D input, such as convolutional and pooling layers.
    """

    def __init__(
        self,
        batch_size=None,
        num_timesteps=None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.squeeze_init(batch_size, num_timesteps)

    def forward(self, input_data: torch.Tensor) -> torch.Tensor:
        return self.squeeze_forward(input_data, super().forward)

    @property
    def _param_dict(self) -> dict:
        return self.squeeze_param_dict(super()._param_dict)
