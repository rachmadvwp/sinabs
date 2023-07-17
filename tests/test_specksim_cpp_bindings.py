def test_specksim_conv_layer():
    import samna
    import numpy as np
    weight_shape = (2, 2, 3, 3)
    event = samna.specksim.events.Spike(
        0, # channel 
        2, # y
        2, # x 
        10 # timestamp
    )
    events = [event]

    conv_weights = np.ones(
        shape=weight_shape
    ).tolist()
    
    conv_layer = samna.specksim.convolution.Convolution2d(
        weight_shape[1], # in channels
        weight_shape[0], # out channels
        (weight_shape[2], weight_shape[3]), # kernel size (y, x)
        (5, 5), # input shape (y, x)
        (1, 1), # stride (y, x)
        (0, 0) # padding (y, x)
    )
    conv_layer.set_weights(conv_weights)

    out = conv_layer.forward(events)
    assert len(out) == weight_shape[1] * weight_shape[2] * weight_shape[3]

def test_specksim_conv_filter():
    import samna
    import numpy as np
    import time
    weight_shape = (2, 2, 3, 3)
    event = samna.specksim.events.Spike(
        0, # channel 
        2, # y
        2, # x 
        10 # timestamp
    )
    events = [event]
    conv_weights = np.ones(
        shape=weight_shape
    ).tolist()
    
    graph = samna.graph.EventFilterGraph()
    source, conv_filter, sink = graph.sequential([
        samna.BasicSourceNode_specksim_events_spike(),        
        samna.specksim.nodes.SpecksimConvolutionalFilterNode(),
        samna.BasicSinkNode_specksim_events_weighted_event()
    ])
    conv_filter.set_parameters(
        weight_shape[1], # in channels
        weight_shape[0], # out channels
        (weight_shape[2], weight_shape[3]), # kernel shape y, x
        (5, 5), # input shape y, x
        (1, 1), # stride
        (0, 0)  # padding
    )
    conv_filter.set_weights(conv_weights)
    graph.start()
    
    source.write(events)
    time.sleep(1)
    out = sink.get_events()
    assert len(out) == weight_shape[1] * weight_shape[2] * weight_shape[3]
    graph.stop()

def test_specksim_iaf_layer():
    import samna
    events = [samna.specksim.events.WeightedEvent(
        0,  # channel
        2,  # y
        2,  # x
        10, # timestamp
        0.2 # weight
    )] * 5
    
    iaf_layer = samna.specksim.spiking.IntegrateAndFire(
        2, # in channels
        (5, 5), # input shape y, x
        1.0, # spike threshold
        0.0  # min v mem
    ) 
    out = iaf_layer.forward(events)
    assert len(out) == 1

def test_specksim_iaf_filter():
    import time

    import samna
    events = [samna.specksim.events.WeightedEvent(
        0,  # channel
        2,  # y
        2,  # x
        10, # timestamp
        0.2 # weight
    )] * 5

    graph = samna.graph.EventFilterGraph()

    source, iaf_node, sink = graph.sequential([
        samna.BasicSourceNode_specksim_events_weighted_event(),
        samna.specksim.nodes.SpecksimIAFFilterNode(),
        samna.BasicSinkNode_specksim_events_spike()
    ])
    iaf_node.set_parameters(
        2, # in channels
        (5, 5), # input shape y, x
        1.0, # spike threshold
        0.0  # min v mem
    )
    graph.start()
    source.write(events)
    time.sleep(2)
    out = sink.get_events()
    graph.stop()
    assert len(out) == 1

def test_specksim_sum_pooling_layer():
    import samna
    y, x = 4, 4
    pool_y, pool_x = 2, 2
    pool_layer = samna.specksim.pooling.SumPooling(
        (pool_y, pool_x),
        (8, 8)
    )
    event = samna.specksim.events.Spike(
        0, # channel 
        y, # y
        x, # x 
        10 # timestamp
    )
    events = [event]
    out = pool_layer.forward(events)
    out_event = out[0]
    assert out_event.x == x // pool_x
    assert out_event.y == y // pool_y

def test_specksim_sum_pooling_filter():
    import samna
    import time

    y, x = 4, 4
    pool_y, pool_x = 2, 2
    event = samna.specksim.events.Spike(
        0, # channel 
        y, # y
        x, # x 
        10 # timestamp
    )
    events = [event]
    graph = samna.graph.EventFilterGraph()
    source, pooling_node, sink = graph.sequential([
        samna.BasicSourceNode_specksim_events_spike(),
        samna.specksim.nodes.SpecksimSumPoolingFilterNode(),
        samna.BasicSinkNode_specksim_events_spike()
    ])
    pooling_node.set_parameters(
        (pool_y, pool_x),
        (8, 8)
    )

    graph.start()
    source.write(events)
    time.sleep(1)
    out = sink.get_events()
    graph.stop()
    out_event = out[0]
    assert out_event.y == y // pool_y
    assert out_event.x == x // pool_x