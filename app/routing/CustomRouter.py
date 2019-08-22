from random import gauss
import traci
import random

from dijkstar import Graph, find_path

from app.network.Network import Network
from app.routing.RouterResult import RouterResult
from app.catastrophe.Accident import getAccidentInstance


class CustomRouter(object):
    """ our own custom defined router """

    # Empty starting references
    edgeMap = None
    graph = None

    # the percentage of smart cars that should be used for exploration
    explorationPercentage = 0.0 # INITIAL JSON DEFINED!!!
    # randomizes the routes
    routeRandomSigma = 0.2 # INITIAL JSON DEFINED!!!
    # how much speed influences the routing
    maxSpeedAndLengthFactor = 1 # INITIAL JSON DEFINED!!!
    # multiplies the average edge value
    averageEdgeDurationFactor = 1 # INITIAL JSON DEFINED!!!
    # how important it is to get new data
    freshnessUpdateFactor = 10 # INITIAL JSON DEFINED!!!
    # defines what is the oldest value that is still a valid information
    freshnessCutOffValue = 500.0 # INITIAL JSON DEFINED!!!
    # how often we reroute cars
    reRouteEveryTicks = 20 # INITIAL JSON DEFINED!!!

    accidentInstance = getAccidentInstance()
    accidentFlag = False
    accidentEdge = ''

    @classmethod
    def init(self):
        """ set up the router using the already loaded network """
        self.graph = Graph()
        self.edgeMap = {}
        for edge in Network.routingEdges:
            self.edgeMap[edge.id] = edge
            self.graph.add_edge(edge.fromNodeID, edge.toNodeID,
                                {'length': edge.length, 'maxSpeed': edge.maxSpeed,
                                 'lanes': len(edge.lanes), 'edgeID': edge.id})
        
        """Register event handler to accident event"""
        self.accidentInstance.subscribe(self.accidentEventHandler)

    # Whenever new car enters the route is calculated for it.
    # This flag is used to put penalty on blocked edges
    @classmethod
    def accidentEventHandler(cls, event):
        if(event.blocked == True):
            cls.accidentEdge = event.edge
            cls.accidentFlag = True
        if(event.blocked == False):
            cls.accidentFlag = False
    

    @classmethod
    def minimalRoute(cls, fr, to):
        """creates a minimal route based on length / speed  """
        #cost_func = lambda u, v, e, prev_e: e['length'] / e['maxSpeed']
        route = find_path(cls.graph, fr, to, cost_func=cls.minimalRouteCostFn)
        return RouterResult(route, False)

    @classmethod
    def minimalRouteCostFn(cls, u, v, e, prev_e):
        if(e['edgeID'] == cls.accidentEdge and cls.accidentFlag == True):
            return 9999
        else:
            return e['length'] / e['maxSpeed']

    @classmethod
    def route(cls, fr, to, tick, car):
        """ creates a route from the f(node) to the t(node) """
        # 1) SIMPLE COST FUNCTION
        # cost_func = lambda u, v, e, prev_e: max(0,gauss(1, CustomRouter.routeRandomSigma) \
        #                                         * (e['length']) / (e['maxSpeed']))

        # if car.victim:
        #     # here we reduce the cost of an edge based on how old our information is
        #     print("victim routing!")
        #     cost_func = lambda u, v, e, prev_e: (
        #         cls.getAverageEdgeDuration(e["edgeID"]) -
        #         (tick - (cls.edgeMap[e["edgeID"]].lastDurationUpdateTick))
        #     )
        # else:
        # 2) Advanced cost function that combines duration with averaging
        # isVictim = ??? random x percent (how many % routes have been victomized before)

        # isVictim = cls.explorationPercentage > random()
        isVictim = False

        if isVictim:
            victimizationChoice = 1
        else:
            victimizationChoice = 0

        cost_func = lambda u, v, e, prev_e: \
            cls.getFreshness(e["edgeID"], tick) * \
            cls.averageEdgeDurationFactor * \
            cls.getAverageEdgeDuration(e["edgeID"]) \
            + \
            (1 - cls.getFreshness(e["edgeID"], tick)) * \
            cls.maxSpeedAndLengthFactor * \
            max(1, gauss(1, cls.routeRandomSigma) *
            (e['length']) / e['maxSpeed']) \
            - \
            (1 - cls.getFreshness(e["edgeID"], tick)) * \
            cls.freshnessUpdateFactor * \
            victimizationChoice

        # generate route
        route = find_path(cls.graph, fr, to, cost_func=cost_func)
        # wrap the route in a result object
        return RouterResult(route, isVictim)

    @classmethod
    def getFreshness(cls, edgeID, tick):
        try:
            lastUpdate = float(tick) - cls.edgeMap[edgeID].lastDurationUpdateTick
            return 1 - min(1, max(0, lastUpdate / cls.freshnessCutOffValue))
        except TypeError as e:
            # print("error in getFreshnessFactor" + str(e))
            return 1

    @classmethod
    def getAverageEdgeDuration(cls, edgeID):
        """ returns the average duration for this edge in the simulation """
        try:
            return cls.edgeMap[edgeID].averageDuration
        except:
            print("error in getAverageEdgeDuration")
            return 1

    @classmethod
    def applyEdgeDurationToAverage(cls, edge, duration, tick):
        """ tries to calculate how long it will take for a single edge """
        try:
            cls.edgeMap[edge].applyEdgeDurationToAverage(duration, tick)
        except:
            return 1

    @classmethod
    def route_by_max_speed(cls, fr, to):
        """ creates a route from the f(node) to the t(node) """
        #cost_func = lambda u, v, e, prev_e: (1 / e['maxSpeed'])
        route = find_path(cls.graph, fr, to, cost_func=cls.maxSpeedCostFn)
        return RouterResult(route, False)

    @classmethod
    def maxSpeedCostFn(cls, u, v, e, prev_e):
        if(e['edgeID'] == cls.accidentEdge and cls.accidentFlag == True):
            return 9999
        else:
            return 1 / e['maxSpeed']

    @classmethod
    def route_by_min_length(cls, fr, to):
        """ creates a route from the f(node) to the t(node) """
        #cost_func = lambda u, v, e, prev_e: (e['length'])
        route = find_path(cls.graph, fr, to, cost_func=cls.minLenCostFn)
        return RouterResult(route, False)

    @classmethod
    def minLenCostFn(cls, u, v, e, prev_e):
        if(e['edgeID'] == cls.accidentEdge and cls.accidentFlag == True):
            return 9999
        else:
            return e['length']

    @classmethod
    def calculate_length_of_route(cls, route):
        return sum([cls.edgeMap[e].length for e in route])

    @classmethod
    def dynamicRouter(cls, fr, to, currentRoute):
        """ this is a dynamic fourth custom router that will check
         the cars on the next edge and increase the cost respectively"""
        def dynamicTrafficCostFunc(u, v, e, prev_e):
                stre = str(e['edgeID'])   # to remove unicode encoding u'2814#3'
                if(e['edgeID'] == cls.accidentEdge and cls.accidentFlag == True):
                    return 9999
                elif( len(currentRoute) > 1):
                    # find the current edge in route in route list
                    try:
                        carAtEdge = currentRoute.index(stre)
                        if carAtEdge < (len(currentRoute) - 3):
                            numCarsOnLane = traci.edge.getLastStepVehicleNumber(stre)
                            numCarsOnLane1 = traci.edge.getLastStepVehicleNumber(currentRoute[carAtEdge+1])
                            numCarsOnLane2 = traci.edge.getLastStepVehicleNumber(currentRoute[carAtEdge+2])

                            if numCarsOnLane + numCarsOnLane1 + numCarsOnLane2 > 10:
                                # todo randomize assign high value to some and normal to others
                                randno = random.uniform(0,1)
                                if randno > 0.5:
                                    return 5000
                                else:
                                    return e['length']
                            else:
                                return e['length']
                        else:
                            return e['length']
                    except:
                        return e['length']
                else:
                    return e['length']    

        route = find_path(cls.graph, fr, to, cost_func=dynamicTrafficCostFunc)
        return RouterResult(route, False)    

    # @classmethod
    # def dynamicTrafficCostFunc(cls, u, v, e, prev_e):
    #     if(e['edgeID'] == cls.accidentEdge and cls.accidentFlag == True):
    #         return 9999
    #     else:
    #         return e['length']
