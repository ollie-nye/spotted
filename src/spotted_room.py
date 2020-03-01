from spotted_coordinate import SpottedCoordinate

class SpottedRoom:
  def __init__(self, width, height, depth):
    self.width = width
    self.height = height
    self.depth = depth

  def center(self):
    return SpottedCoordinate(self.width / 2.0, self.height / 2.0, self.depth / 2.0)
