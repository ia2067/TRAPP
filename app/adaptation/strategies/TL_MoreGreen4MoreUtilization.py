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
        return Util.get_street_utilizations(Knowledge.time_of_last_adaptation, adaptation_period)[0]

    def analyze(self, utilizations):
        overloaded_streets = []
        for street, utilizations in utilizations.iteritems():
            mean_utilization = mean(utilizations)
            # increase green time
            if mean_utilization > 0.2:
                print "overloaded street: " + str(street)
                overloaded_streets.append(street)
            # if < 0.2 or 0.3
            # lower utilization
        return overloaded_streets

    def plan(self, overloaded_streets):
        TrafficLightRegistry.updateTLs()
        changing_lights = []
        for tl_id in TrafficLightRegistry.tls:
            tl = TrafficLightRegistry.findById(tl_id)
            for lane in overloaded_streets:
                if lane in tl.incLanes:
                    changing_lights.append((tl, lane))



        # avoid_streets_signal = []
        # for i in range(Knowledge.planning_steps):
        #     avoid_streets_signal += [0 if edge.id in overloaded_streets else 1 for edge in Network.routingEdges]
        return changing_lights

    def execute(self, changing_lights):
        for pair in changing_lights:
            tl = pair[0]
            lane = pair[1]
            prog = tl.getProgramLogic()
            prog.changeGreenPhasesDuration(lane, 5)
            tl.setProgramLogic(prog)
        # if len(avoid_streets_signal) > 0:
        #     print "Sending signal to avoid overloaded streets!"
        # with open('datasets/plans/signal.target', 'w') as signal_fil:
        #     signal_writer = csv.writer(signal_fil, dialect='excel')
        #     signal_writer.writerow(avoid_streets_signal)
        #
        # Knowledge.globalCostFunction = "XCORR"
