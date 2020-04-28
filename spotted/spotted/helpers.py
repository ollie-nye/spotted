"""
Helper functions shared between classes
"""

import math
import numpy as np

def scale(value, old_min, old_max, new_min, new_max):
  """
  Scales a given value from one range to another

  Arguments:
    value {float} -- Value to scale
    old_min {float} -- Lower value of old range
    old_max {float} -- Upper value of old range
    new_min {float} -- Lower value of new range
    new_max {float} -- Upper value of new range

  Returns:
    float -- value scaled to new range
  """

  old_range = (old_max - old_min)
  new_range = (new_max - new_min)
  return (((value - old_min) * new_range) / old_range) + new_min

# pylint: disable=invalid-name
def create_rotation_matrix(x, y, z):
  """
  Creates a 3D rotation matrix about the given axis

  Arguments:
    x {float} -- x axis rotation
    y {float} -- y axis rotation
    z {float} -- z axis rotation

  Returns:
    2D np.array -- rotation matrix
  """

  a = math.radians(x)
  b = math.radians(y)
  c = math.radians(z)

  return np.array([
    [
      [1, 0, 0],
      [0, math.cos(a), math.sin(a)],
      [0, -math.sin(a), math.cos(a)]
    ],
    [
      [math.cos(b), 0, -math.sin(b)],
      [0, 1, 0],
      [math.sin(b), 0, math.cos(b)]
    ],
    [
      [math.cos(c), math.sin(c), 0],
      [-math.sin(c), math.cos(c), 0],
      [0, 0, 1]
    ]
  ])

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

def handler_class_with_args(handler, handler_args):
  """
  Injects the given arguments into the given handler at init

  Arguments:
    handler {class} -- Handler to inject arguments into
    handler_args {any} -- Args to pass to the handler injection function

  Returns:
    CustomHandler with arguments set
  """

  # pylint: disable=too-few-public-methods
  class CustomHandler(handler):
    """
    Wrapper around handler
    """

    def __init__(self, *args, **kwargs):
      """
      Inits the handler with supplied handler_args
      """

      self.push_spotted_reference(handler_args)
      super(CustomHandler, self).__init__(*args, **kwargs)

  return CustomHandler
