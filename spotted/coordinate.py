"""
Spotted Coordinate
"""

import math
import numpy as np

# pylint: disable=invalid-name
def pythagoras(a_x, a_y, b_x, b_y):
  """
  Returns the euclidian distance between two points

  Arguments:
    a_x {float} -- x coordinate of a
    a_y {float} -- y coordinate of a
    b_x {float} -- x coordinate of b
    b_y {float} -- y coordinate of b

  Returns:
    Distance
  """

  return math.sqrt((a_x - b_x) ** 2 + (a_y - b_y) ** 2)

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

  def diff(self, position):
    """
    Difference between self and position

    Arguments:
      position {Coordinate} -- position to diff to

    Returns:
      Coordinate with components as difference values
    """

    return Coordinate(self.x - position.x, self.y - position.y, self.z - position.z)

  def displace_by(self, position):
    """
    Add two coordinates

    Arguments:
      position {Coordinate} -- position to add to self

    Returns:
      Coordinate with components as summed values
    """

    return Coordinate(self.x + position.x, self.y + position.y, self.z + position.z)

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
