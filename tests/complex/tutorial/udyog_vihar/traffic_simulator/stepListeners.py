import traci

from neupy import algorithms
from neupy import layers, storage

import numpy as np

from collections import OrderedDict
from .ordered_set import OrderedSet


class Light:
    def __init__(self, lanes, state, timer=0):
        self.laneState = OrderedDict()
        self.timer = timer
        totalCharsRead = 0
        for lane in lanes:
            self.laneState[lane] = {'linkNumber': traci.lane.getLinkNumber(lane)}
            self.laneState[lane]['state'] = state[totalCharsRead: totalCharsRead + self.laneState[lane]['linkNumber']]
            totalCharsRead += self.laneState[lane]['linkNumber']

    def setGreen(self, lane):
        for _lane, info in self.laneState.items():
            if (_lane == lane):
                info['state'] = 'g'*info['linkNumber']
            else:
                info['state'] = 'r' * info['linkNumber']

    @property
    def state(self):
        return ''.join(map(lambda info: info['state'], self.laneState.values()))

    @property
    def lanes(self):
        return tuple(self.laneState.keys())

    def updateGreenToMaxVehicle(self):
        lanes = self.lanes
        maxTrafficLane = lanes[0]
        for lane in self.lanes[1:]:
            if (traci.lane.getLastStepVehicleNumber(lane) > traci.lane.getLastStepVehicleNumber(maxTrafficLane)):
                maxTrafficLane = lane
        self.setGreen(maxTrafficLane)

    def updateGreenToMinVehicle(self):
        lanes = map(lambda x: {'id': x, 'traffic': traci.lane.getLastStepVehicleNumber(x)}, tuple(self.lanes))
        lanes = filter(lambda x: x['traffic'] != 0, lanes)
        lanes = map(lambda x: x['id'], lanes)
        if lanes:
            minTrafficLane = lanes[0]
            for lane in lanes[1:]:
                if (traci.lane.getLastStepVehicleNumber(lane) < traci.lane.getLastStepVehicleNumber(minTrafficLane)):
                    minTrafficLane = lane
            self.setGreen(minTrafficLane)

    def setLightFromNN(self, nn):
        vehicles = map(lambda x: traci.lane.getLastStepVehicleNumber(x), tuple(self.lanes))
        if len(vehicles) == 3:
            vehicles.append(0)

        inputs = []
        for vehicle in vehicles:
            inputs.extend([vehicle, 0])
        outputs = list(nn.predict([inputs])[0])
        # print(inputs, outputs)
        self.setGreen(self.lanes[outputs.index(max(outputs))])


class TrafficLightController(traci.StepListener):

    def __init__(self):
        self.cache = {}

    def step(self, s=0):
        for tlId in traci.trafficlights.getIDList():
            self.handleTrafficLights(s, tlId)

    def handleTrafficLights(self, step, id):
        lanes = tuple(OrderedSet(traci.trafficlights.getControlledLanes(id)))
        state = traci.trafficlights.getRedYellowGreenState(id)
        # print ('lanes', lanes, state)
        # print(traci.trafficlights.getControlledLanes(id))

        light = self.cache.get(id, Light(lanes, state))
        if light.timer <= 0:
            light.updateGreenToMaxVehicle()
            # light.updateGreenToMinVehicle()
            traci.trafficlights.setRedYellowGreenState(id, light.state)
            light.timer = 12
        light.timer -= 1
        self.cache[id] = light
        # for lane in lanes:
        #     print ("traffic on lane {}: ".format(lane), traci.lane.getLastStepVehicleNumber(lane), traci.lane.getLinkNumber(lane))


class NNTLC(TrafficLightController):

    def __init__(self):
        super(NNTLC, self).__init__()
        self.nn = algorithms.RMSProp(
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
        storage.load(self.nn, '/home/ubuntu/nn')


    def handleTrafficLights(self, step, id):
        lanes = tuple(OrderedSet(traci.trafficlights.getControlledLanes(id)))
        state = traci.trafficlights.getRedYellowGreenState(id)
        # print ('lanes', lanes, state)
        # print(traci.trafficlights.getControlledLanes(id))

        light = self.cache.get(id, Light(lanes, state))
        if light.timer <= 0:
            light.setLightFromNN(self.nn)
            # light.updateGreenToMinVehicle()
            traci.trafficlights.setRedYellowGreenState(id, light.state)
            light.timer = 12
        light.timer -= 1
        self.cache[id] = light

