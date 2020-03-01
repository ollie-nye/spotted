import numpy as np
import cv2 as cv

class SpottedCalibration:
  def __init__(self, json):
    self.dim = (json['dim'][0], json['dim'][1])
    self.d = np.array(json['d'])
    self.k = np.array(json['k'])

    self.map1, self.map2 = cv.fisheye.initUndistortRectifyMap(self.k, self.d, np.eye(3), self.k, self.dim, cv.CV_16SC2)

  def restore(self, frame):
    return cv.remap(frame, self.map1, self.map2, interpolation=cv.INTER_LINEAR, borderMode=cv.BORDER_CONSTANT)
