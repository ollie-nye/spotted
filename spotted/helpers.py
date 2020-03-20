"""
Helper functions shared between classes
"""

import math
import numpy as np
import cv2 as cv

def imfill(frame):
  """
  Fill holes in a given frame

  Arguments:
    frame {2D np.array} -- Frame to fill

  Returns:
    2D np.array -- Frame with holes filled
  """

  im_flood_fill = frame.copy()
  height, width = frame.shape[:2]
  mask = np.zeros((height + 2, width + 2), np.uint8)
  im_flood_fill = im_flood_fill.astype('uint8')
  cv.floodFill(im_flood_fill, mask, (0, 0), 255)
  im_flood_fill_inv = cv.bitwise_not(im_flood_fill)
  frame = frame.astype('uint8')
  return frame | im_flood_fill_inv

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

  a = math.radians(z)
  b = math.radians(y)
  c = math.radians(x)

  return np.array([
    [
      math.cos(a) * math.cos(b),
      (math.cos(a) * math.sin(b) * math.sin(c)) - (math.sin(a) * math.cos(c)),
      (math.cos(a) * math.sin(b) * math.cos(c)) + (math.sin(a) * math.sin(c))
    ],
    [
      math.sin(a) * math.cos(b),
      (math.sin(a) * math.sin(b) * math.sin(c)) + (math.cos(a) * math.cos(c)),
      (math.sin(a) * math.sin(b) * math.cos(c)) - (math.cos(a) * math.sin(c))
    ],
    [
      -math.sin(b),
      math.cos(b) * math.sin(c),
      math.cos(b) * math.cos(c)
    ]
  ])
