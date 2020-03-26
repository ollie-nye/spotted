"""
OpenCV Contour handler
"""

import numpy as np
import cv2 as cv

class Contour:
  """
  OpenCV Contour handler
  """
  def __init__(self, points):
    """

    """

    if isinstance(points, list):
      self.points = points
      self.np_points = np.array(points)
    else:
      self.points = points.tolist()
      self.np_points = points
    (self.center_x, self.center_y), self.radius = cv.minEnclosingCircle(self.np_points)
    self.area = cv.contourArea(self.np_points)
