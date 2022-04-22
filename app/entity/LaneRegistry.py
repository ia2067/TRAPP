from app import Config
from Lane import Lane
from TrafficLightRegistry import TrafficLightRegistry

import xml.etree.ElementTree as ET

class NullLane:
    """ a Lane with no function used for error prevention"""
    def __init__(self):
        pass

class LaneRegistry(object):
    """ Central Registry for all the individual lanes in the sumo simulation"""

    # dict of all lanes
    lanes = {}

    # dict of lanes that go into traffic lights
    incLanes = {}

    @classmethod
    def updateLanes(cls):
        tree = ET.parse(Config.sumoNet)
        root = tree.getroot()
        for child in root.iter('lane'):
            lane_id = child.attrib["id"]
            lane_index = child.attrib["index"]
            lane_speed = child.attrib["speed"]
            lane_length = child.attrib["length"]
            lane_shape = child.attrib["shape"]
            cls.lanes[lane_id] = Lane(lane_id, lane_index, lane_speed, lane_length, lane_shape)
        cls._updateTlIncLanes()

    @classmethod
    def _updateTlIncLanes(cls):
        # update lanes entering traffic lights
        for tl_id in TrafficLightRegistry.tls:
            tl = TrafficLightRegistry.findById(tl_id)
            lanes = tl.incLanes.split()
            for lane in lanes:
                cls.incLanes[lane] = cls.findById(lane)

    @classmethod
    def findById(cls, lane_id):
        """ returns a lane by a given laneID"""
        try:
            return cls.lanes[lane_id]
        except:
            return NullLane()
