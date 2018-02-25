from __future__ import absolute_import
from __future__ import print_function


import os
import sys

try:
    sys.path.append(os.path.join(os.path.dirname(
        __file__), '..', '..', '..', '..', "tools"))  # tutorial in tests
    sys.path.append(os.path.join(os.environ.get("SUMO_HOME", os.path.join(
        os.path.dirname(__file__), "..", "..", "..")), "tools"))  # tutorial in docs
    from sumolib import checkBinary  # noqa
except ImportError:
    sys.exit(
        "please declare environment variable 'SUMO_HOME' as the root directory of your sumo installation (it should contain folders 'bin', 'tools' and 'docs')")
import traci
from traffic_simulator.vehicles import Vehicles
from traffic_simulator.stepListeners import TrafficLightController, NNTLC
sumoBinary = checkBinary('sumo-gui')

sumoCmd = [sumoBinary, "-c", "data/uv.sumocfg", "-S", "--log", "log", "--error-log", "error", "--duration-log.statistics"]

traci.start(sumoCmd)
traci.simulationStep()

vehicles = Vehicles()
vehicles.addVehicles()
# traci.addStepListener(TrafficLightController())
traci.addStepListener(NNTLC())
step=0
while step < 10000:
	traci.simulationStep()
	step += 1	
traci.close()
sys.stdout.flush()