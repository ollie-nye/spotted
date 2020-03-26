"""
An interesting point for the system, knows about the camera position it came
from, the position it is pointing at, and the relative pixel coordinates that
produced it
"""

import math
import numpy as np

class PointOfInterest:
  """
  An interesting point for the system, knows about the camera position it came
  from, the position it is pointing at, and the relative pixel coordinates that
  produced it
  """

  def __init__(self, position, location=None, camera_position=None, *, increment_step=2, decrement_step=30):
    """
    Creates an instance of a point

    Arguments:
      position {Coordinate} -- Position of the point
      location {tuple} -- Pixel coordinates of the point. Can be None
      camera_position {Coordinate} -- Position of the origin camera. Can be None

    Returns:
      Instance of PointOfInterest
    """

    self.camera_position = camera_position
    self.update_position(position, location)
    self.count = 100
    self.weight = 1

    self.increment_step = increment_step
    self.decrement_step = decrement_step

  def increment_count(self):
    """
    Increase count and recalculate weight
    """

    self.count += self.increment_step
    self.recalculate_weight()

  def decrement_count(self):
    """
    Decrease count by a proportionally larger value and recalculate weight
    Count cannot go below 1
    """

    self.count -= self.decrement_step
    if self.count < 1:
      self.count = 1
    self.recalculate_weight()

  def recalculate_weight(self):
    """
    Recalculate weight from instance count
    Weight cannot go above 255
    """

    self.weight = math.log10(self.count)
    if self.weight > 255:
      self.weight = 255

  def update_position(self, position, location=None):
    """
    Update position, location and direction vector from camera position

    Arguments:
      position {Coordinate} -- world location of point with camera as origin
      location {(x, y)} -- pixel location of point in camera frame
    """

    self.position = position
    self.location = location
    if self.camera_position is not None:
      self.direction_vector = np.subtract(position.as_vector(), self.camera_position.as_vector())

  def diff_from_position(self, position):
    """
    Euclidian distance from this point to a given position

    Arguments:
      position {Coordinate} -- position to measure distance to

    Returns:
      Euclidian distance between the two points
    """

    diff_x = (self.position.x - position.x) ** 2
    diff_y = (self.position.y - position.y) ** 2
    diff_z = (self.position.z - position.z) ** 2
    return math.sqrt(diff_x + diff_y + diff_z)
