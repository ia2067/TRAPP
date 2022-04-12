from app import Config
from TrafficLight import TrafficLight
import sys,os

import xml.etree.ElementTree as ET

class NullTL:
    """ a TL with no function used for error prevention"""
    def __init__(self):
        pass


class TrafficLightRegistry(object):
    """ Central Registry for all our traffic Lights in the sumo simulation"""

    # list of all tls
    tls = {}

    @classmethod
    def updateTLs(cls):
        tree = ET.parse(Config.sumoNet)
        root = tree.getroot()
        for child in root.iter('junction'):
            junction_type = child.get('type')
            junction_id = child.get('id')
            if junction_type == "traffic_light":
                inc_lanes = child.attrib["incLanes"]
                int_lanes = child.attrib["intLanes"]
                shape = child.attrib["shape"]
                x = child.attrib["x"]
                y = child.attrib["y"]
                cls.tls[junction_id] = TrafficLight(junction_id, inc_lanes, int_lanes, shape, x, y)

    @classmethod
    def findById(cls, tl_id):
        """ Returns a car by a given tlID"""
        try:
            return cls.tls[tl_id]
        except:
            return NullTL()
