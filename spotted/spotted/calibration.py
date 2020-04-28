"""
Calibration is responsible for restoring an original image taken through a
fisheye lens
"""

import numpy as np
import cv2 as cv

class Calibration:
  """
  Calibration is responsible for restoring an original image taken through a
  fisheye lens
  """
  def __init__(self, json):
    """
    Creates a new instance of Calibration

    Arguments:
      json {dict} -- dictionary to configure the instance

    Returns:
      Calibration -- The populated calibration instance
    """
    dimension = (json['dimension'][0], json['dimension'][1])
    distortion = np.array(json['distortion'])
    camera = np.array(json['camera'])

    # pylint: disable=no-member
    self.map1, self.map2 = cv.fisheye.initUndistortRectifyMap(
      camera, distortion, np.eye(3), camera, dimension, cv.CV_16SC2
    )

  def restore(self, frame):
    """
    Reverts the effect of the fish eye lens on a given frame

    Arguments:
      frame {array} -- frame to apply the filter to

    Returns:
      array -- frame after applying the filter, same dimension as passed frame
    """
    return cv.remap(
      frame,
      self.map1,
      self.map2,
      interpolation=cv.INTER_LINEAR,
      borderMode=cv.BORDER_CONSTANT
    )
