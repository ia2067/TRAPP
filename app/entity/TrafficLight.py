import traci
import traci.constants as tc


from app import Config

class TrafficLight:
    """ a class to represent an individual traffic light """

    def __init__(self, name, id, incLanes, intLanes, shape, x, y):
        # the string name
        self.name = name
        # the string id
        self.id = id
        self.incLanes = incLanes
        self.intLanes = intLanes
        self.shape = shape
        self.x = x
        self.y = y


    def getControlledLanes(self):
        """ wrapper method to get the lanes controlled by this traffic light"""
        try:
            return traci.trafficlight.getControlledLanes(self.id)
        except:
            return None

    def getControlledLinks(self):
        """ wrapper method to get the links controlled by this traffic light"""
        try:
            return traci.trafficlight.getControlledLinks(self.id)
        except Exception as ex:
            print(ex)
            return None

    def getProgram(self):
        """ wrapper method to get the ID of the program currently running"""
        try:
            pID = traci.trafficlight.getProgram(self.id)
            currPhaseIndex = traci.trafficlight.getPhase(self.id)
            prog = traci.trafficlight.Logic(pID, None, currPhaseIndex)
            return prog
        except:
            return None
