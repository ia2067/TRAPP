from app.adaptation.Strategy import Strategy
from app.adaptation.Util import *
from app.adaptation import Knowledge
from app.network.Network import Network
from app.Config import adaptation_period
from app.entity.TrafficLightRegistry import TrafficLightRegistry
import csv
from numpy import mean


class TL_MoreGreen4MoreUtilization(Strategy):

    def monitor(self):
        return Util.get_lane_wait_times(Knowledge.time_of_last_adaptation, adaptation_period)[0]

    def analyze(self, wait_times):
        too_long_wait_lanes = []
        too_short_wait_lanes = []
        for lane, wait_time in wait_times.iteritems():
            mean_wait_time = mean(wait_time)
            # increase green time
            if mean_wait_time > 15:
                print "Too Long of a wait: " + str(lane)
                too_long_wait_lanes.append(lane)
            if mean_wait_time < 3:
                print "Too short of a wait: " + str(lane)
                too_short_wait_lanes.append(lane)
        return too_long_wait_lanes, too_short_wait_lanes

    def plan(self, affected_lanes):
        increasing_lights = []
        decreasing_lights = []
        for tl_id in TrafficLightRegistry.tls:
            tl = TrafficLightRegistry.findById(tl_id)
            for lane in affected_lanes[0]:
                if lane in tl.incLanes:
                    increasing_lights.append((tl, lane))
            for lane in affected_lanes[1]:
                if lane in tl.incLanes:
                    decreasing_lights.append((tl, lane))

        return increasing_lights, decreasing_lights

    def execute(self, changing_lights):
        increasing_lights = changing_lights[0]
        decreasing_lights = changing_lights[1]
        for pair in increasing_lights:
            tl = pair[0]
            lane = pair[1]
            prog = tl.getProgramLogic()
            prog.changeGreenPhasesDuration(lane, 5)
            tl.setProgramLogic(prog)
        for pair in decreasing_lights:
            tl = pair[0]
            lane = pair[1]
            prog = tl.getProgramLogic()
            prog.changeGreenPhasesDuration(lane, -2)
            tl.setProgramLogic(prog)
