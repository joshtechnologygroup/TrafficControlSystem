import traci

vehicleDomain = traci.vehicle
edgeDomain = traci.edge
routeDomain = traci.route
sim = traci.simulation


class Vehicles:
    lastRouteId = 0
    lastVehId = 0
    depart_at = 1

    def addVehicles(self):
        edgeList = filter(lambda edge: 'to' in edge, edgeDomain.getIDList())

        for fromEdge in edgeList[::5]:
            for toEdge in edgeList[::7]:
                self.addVehicle(fromEdge, toEdge)

    def addVehicle(self, fromEdge, toEdge):
        route = sim.findRoute(fromEdge, toEdge).edges
        routeID = 'v{}'.format(self.lastRouteId)
        routeDomain.add(routeID, route)
        vehicleDomain.add('v{}'.format(self.lastVehId), routeID, depart=1)
        self.lastRouteId += 1
        self.lastVehId += 1
        self.depart_at += 10

