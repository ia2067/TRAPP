import traci

class Lane:
    """ a class to represent an individual lane"""

    def __init__(self, id, index, speed, length, shape):
        self.id = id
        self.index = index
        self.speed = speed
        self.length = length
        self.shape = shape
