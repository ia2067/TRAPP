from app import Config
from Lane import Lane

import xml.etree.ElementTree as ET

class NullLane:
    """ a Lane with no function used for error prevention"""
    def __init__(self):
        pass

class LaneRegistry(object):
    """ Central Registry for all the individual lanes in the sumo simulation"""

    # list of all lanes
    lanes = {}

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

    @classmethod
    def findById(cls, lane_id):
        """ returns a lane by a given laneID"""
        try:
            return cls.lanes[lane_id]
        except:
            return NullLane()
