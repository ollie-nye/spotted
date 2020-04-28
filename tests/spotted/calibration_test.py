import numpy as np
import cv2 as cv
from spotted.spotted.calibration import Calibration

def test_init():
  dimension = (2048, 1536)
  camera = [
    [1560.4213486225046, 0, 1050.8972596532385],
    [0, 1563.2664464043153, 747.1487200699582],
    [0, 0, 1]
  ]
  distortion = [
    [-0.059142684903839664],
    [0.02386601511813416],
    [-0.32038269497024474],
    [0.34536003649836755]
  ]

  config = {
    "dimension": [dimension[0], dimension[1]],
    "camera": camera,
    "distortion": distortion
  }

  calibration = Calibration(config)

  map1, map2 = cv.fisheye.initUndistortRectifyMap(
    np.array(camera), np.array(distortion), np.eye(3), np.array(camera), dimension, cv.CV_16SC2
  )

  assert calibration.map1.all() == map1.all()
  assert calibration.map2.all() == map2.all()

  # assert calibration.dimension == (1024, 768)
  # assert calibration.distortion == np.array([[1], [2]])
  # assert calibration.camera == np.array([[1, 2, 3]])
