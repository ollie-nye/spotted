"""
Room to contain all fixtures and cameras
"""

from spotted.spotted.coordinate import Coordinate

class Room:
  """
  Room to contain all fixtures and cameras
  """

  def __init__(self, width, height, depth):
    """
    Creates a room from the given parameters

    Arguments:
      width {float} -- Room width
      height {float} -- Room height
      depth {float} -- Room depth

    Returns:
      Room -- Configured with given parameters
    """

    self.width = width
    self.height = height
    self.depth = depth

  def center(self):
    """
    Gets the centerpoint of the room

    Returns:
      Coordinate -- centerpoint of the room
    """

    return Coordinate(self.width / 2.0, self.height / 2.0, self.depth / 2.0)
