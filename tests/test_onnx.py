import torch
import torch.nn as nn


def test_sinabs_model_to_onnx():
    import onnx
    from sinabs.from_torch import from_model
    from sinabs.onnx import print_onnx_model, get_graph, print_graph

    layers = [
        nn.Conv2d(2, 8, kernel_size=2),
        nn.AvgPool2d(2, stride=2),
        nn.ReLU(),
        nn.Conv2d(8, 10, kernel_size=3),
        nn.AvgPool2d(3),
        nn.ReLU(),
    ]

    ann = nn.Sequential(*layers)
    snn = from_model(ann)
    print(snn)
    dummy_input = torch.zeros([1, 2, 64, 64])  # One time step
    snn(dummy_input) # first pass to create all state variables
    fname = "snn.onnx"

    torch.onnx.export(
        snn.spiking_model,
        dummy_input,
        fname,
        input_names=["tchw_input"],
        output_names=["tchw_output"],
        dynamic_axes={"tchw_input": [0],"tchw_output": {0: "time"}},
        verbose=False,
    )
    snn_model = onnx.load(fname)
    ann_graph = get_graph(snn, dummy_input)
    print("................")
    print_graph(ann_graph)
    print("................")
    print_onnx_model(snn_model)



def test_graph_generation_ann():
    import torchvision.models
    import onnx
    from sinabs.onnx import print_onnx_model

    model = torchvision.models.resnet18()
    dummy_input = torch.zeros([1, 3, 224, 224])
    fname = "resnet18.onnx"

    torch.onnx.export(model, dummy_input, fname)
    onnx_model = onnx.load(fname)

    print_onnx_model(onnx_model)

