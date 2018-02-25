from neupy import algorithms
from neupy import layers, storage

import numpy as np

def calculate_energy(state):
    red_time = state[1::2]
    vehicles = state[::2]

    expected_output = []
    for i in range(4):
            expected_output.append(red_time[i] + 3 * vehicles[i] if vehicles[i] else 0)

    return expected_output

def train_network(network):
    data_points = [0, 2, 4, 8]
    inputs = []
    outputs = []

    for i in data_points:
        for j in data_points:
            for k in data_points:
                for l in data_points:
                    for m in data_points:
                        for n in data_points:
                            for o in data_points:
                                for p in data_points:
                                    inputs.append([i,j,k,l,m,n,o,p])
                                    outputs.append(calculate_energy([i,j,k,l,m,n,o,p]))
                                    print [i,j,k,l,m,n,o,p]


    print 'heeeererrerere'
    network.train(
        np.array(inputs),
        np.array(outputs)
        # np.array([[5, 4, 0, 4, 0, 4, 0, 4], [0, 4, 5, 4, 0, 4, 0, 4], [0, 4, 0, 4, 5, 4, 0, 4],
        #           [0, 4, 0, 4, 0, 4, 5, 4]]),
        # np.array([[10, 0, 0, 0], [0, 10, 0, 0], [0, 0, 10, 0], [0, 0, 0, 10]])
    )


network = algorithms.RMSProp(
    [
        layers.Input(8),
        layers.Relu(64),
        layers.Relu(48),
        layers.Relu(32),
        layers.Linear(4)
    ],
    step=0.001,
    error='rmse',
    batch_size=100,
    decay_rate=0.1,
    addons=[algorithms.WeightDecay]
)

print("Start training")
# train_network(network)

print network.predict([[0, 4, 0, 8, 0, 16, 10, 24]])
print network.predict([[0, 4, 0, 8, 10, 16, 0, 24]])
print network.predict([[0, 4, 10, 8, 0, 16, 0, 24]])
print network.predict([[10, 4, 0, 8, 0, 16, 0, 24]])


storage.save(network, '/home/ubuntu/nn')