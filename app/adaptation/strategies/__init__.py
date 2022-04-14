import app.Config as Config
from app.adaptation.strategies.AvoidOverloadedStreets import AvoidOverLoadedStreets
from app.adaptation.strategies.LoadBalancing import LoadBalancing
from app.adaptation.strategies.TunePlanningResolution import TunePlanningResolution
from app.adaptation.strategies.TL_MoreGreen4MoreUtilization import TL_MoreGreen4MoreUtilization


def get_adaptation_stategy(tick):

    if Config.adaptation_strategy == "load_balancing":
        return LoadBalancing(tick)
    elif Config.adaptation_strategy == "avoid_overloaded_streets":
        return AvoidOverLoadedStreets(tick)
    elif Config.adaptation_strategy == "tune_planning_resolution":
        return TunePlanningResolution(tick)
    elif Config.adaptation_strategy == "TL_MoreGreen4MoreUtilization":
        return TL_MoreGreen4MoreUtilization(tick)