"""
Spotted Coordinate
"""

import numpy as np

class Coordinate:
  """
  Spotted Coordinate
  """

  # pylint: disable=invalid-name
  def __init__(self, x, y, z):
    """
    Creates a coordinate with the given positions

    Arguments:
      x {float} -- x position
      y {float} -- y position
      z {float} -- z position

    Returns:
      Coordinate
    """

    self.x = x
    self.y = y
    self.z = z

  def __str__(self):
    return f"({self.x}, {self.y}, {self.z})"

  def __repr__(self):
    return f"({self.x}, {self.y}, {self.z})"

  def __add__(self, coordinate):
    return Coordinate(self.x + coordinate.x, self.y + coordinate.y, self.z + coordinate.z)

  def __sub__(self, coordinate):
    return Coordinate(self.x - coordinate.x, self.y - coordinate.y, self.z - coordinate.z)

  def __truediv__(self, divisor):
    return Coordinate(self.x / divisor, self.y / divisor, self.z / divisor)

  def as_vector(self):
    """
    Return coordinate as indexed list in x, y, z order
    """

    return np.array([self.x, self.y, self.z])

  def as_dict(self):
    """
    Return coordinate as keyed dictionary
    """

    return {'x': self.x, 'y': self.y, 'z': self.z}
