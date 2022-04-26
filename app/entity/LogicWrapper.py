

class LogicWrapper:
    """
    A class to wrap around the traci built in type of Logic
    This class will include some convenience functions for increasing
    the durations of phases, etc
        """

    def __init__(self, logic, lanes):
        self.logic = logic
        self.lanes = lanes

    def getId(self):
        if self.logic is not None:
            return self.logic.programID
        else:
            return None

    def getType(self):
        if self.logic is not None:
            return self.logic.type
        else:
            return None

    def _sublaneInLane(self, sublane, lane):
        return sublane.startswith(lane)

    def getGreenPhasesOf(self, lane):
        # get indices of lane param
        indices = [i for i, x in enumerate(self.lanes) if self._sublaneInLane(x, lane)]
        retval = set()
        for i, x in enumerate(self.logic.getPhases()):
            for l in indices:
                if 'y' not in x.state and (x.state[l] is 'g' or x.state[l] is 'G'):
                    retval.add(i)
        return retval

    def changeGreenPhasesDuration(self, lane, amount):
        # green phases
        gp = self.getGreenPhasesOf(lane)
        phases = self.logic.getPhases()
        for i in gp:
            phases[i].duration *= amount
            phases[i].duration = round(phases[i].duration)
            if phases[i].duration < 3:
                phases[i].duration = 3 # Cant go lower than 3 seconds of green time (unsure if this is appropriate)
