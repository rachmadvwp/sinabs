#  Copyright (c) 2019-2019     aiCTX AG (Sadique Sheik, Massimo Bortone).
#
#  This file is part of sinabs
#
#  sinabs is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  sinabs is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with sinabs.  If not, see <https://www.gnu.org/licenses/>.


def test_forward():
    import torch
    from sinabs.layers import Sig2SpikeLayer

    channels = 1
    length = 3
    b = 3.0
    tw = 5
    thr = b / tw

    lyr = Sig2SpikeLayer(
        sig_shape=(channels, length), tw=tw, threshold=thr, layer_name="sig2spk"
    )

    sig = torch.tensor([[1.0, 0.5, 0.25]])*b
    sig = torch.stack([sig]*tw, dim=0)

    spk = lyr(sig)

    assert spk.shape == (tw, channels, length)
