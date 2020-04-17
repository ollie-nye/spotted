"""
Main runner for Spotted
"""

import sys
import math
import json
from datetime import datetime

import cv2 as cv
from cv2 import aruco
import numpy as np

from spotted.spotted import Spotted

# pylint: disable=invalid-name,no-member
if __name__ == '__main__':
  args_count = len(sys.argv) - 1
  if args_count == 0:
    FUNC = 'default'
  else:
    FUNC = sys.argv[1]

  if FUNC == 'create_board':
    aruco_dictionary = aruco.Dictionary_get(aruco.DICT_6X6_250)
    board = aruco.CharucoBoard_create(7, 5, 1, 0.8, aruco_dictionary)
    imboard = board.draw((2000, 2000))
    cv.imwrite("chessboard.png", imboard)

    print('Board has been written to "./chessboard.png"')

  elif FUNC == 'default':
    skip_cameras = False
    if args_count == 2:
      if sys.argv[2] == 'true':
        skip_cameras = True
    Spotted(skip_cameras).start_spotted()

  elif FUNC == 'calibrate_lens':
    camera = Spotted().cameras[0]

    images = []
    captured_count = 0
    capture_limit = 15
    last_capture_timestamp = datetime.now()

    print('Ready to capture')

    more_to_capture = True
    while more_to_capture:
      ret, frame = camera.capture.read()
      if (datetime.now() - last_capture_timestamp).total_seconds() > 3:
        print('Capturing frame')
        last_capture_timestamp = datetime.now()

        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        images.append(gray)

        captured_count += 1
        if captured_count >= capture_limit:
          more_to_capture = False

    print('Frames captured, processing...')

    CHECKERBOARD = (6, 9)
    subpix_criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.1)
    calibration_flags = cv.fisheye.CALIB_RECOMPUTE_EXTRINSIC + cv.fisheye.CALIB_FIX_SKEW
    objp = np.zeros((1, CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
    objp[0, :, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
    _img_shape = gray.shape[:2]
    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane.
    for img in images:
      # Find the chess board corners
      ret, corners = cv.findChessboardCorners(
        img,
        CHECKERBOARD,
        cv.CALIB_CB_ADAPTIVE_THRESH + cv.CALIB_CB_FAST_CHECK + cv.CALIB_CB_NORMALIZE_IMAGE
      )
      # If found, add object points, image points (after refining them)
      if ret:
        objpoints.append(objp)
        cv.cornerSubPix(img, corners, (3, 3), (-1, -1), subpix_criteria)
        imgpoints.append(corners)
    N_OK = len(objpoints)
    K = np.zeros((3, 3))
    D = np.zeros((4, 1))
    rvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(N_OK)]
    tvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(N_OK)]

    print('obj:', len(objpoints))
    print('img:', len(imgpoints))

    rms, _, _, _, _ = cv.fisheye.calibrate(
      objpoints,
      imgpoints,
      img.shape[::-1],
      K,
      D,
      rvecs,
      tvecs,
      calibration_flags,
      (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 1e-6)
    )
    print("Found " + str(N_OK) + " valid images for calibration")
    print("DIM=" + str(_img_shape[::-1]))
    print("K=np.array(" + str(K.tolist()) + ")")
    print("D=np.array(" + str(D.tolist()) + ")")

  elif FUNC == 'calibrate_position':
    camera = Spotted().cameras[0]

    images = []
    captured_count = 0
    capture_limit = 30
    last_capture_timestamp = datetime.now()

    print('Ready to capture')

    more_to_capture = True
    while more_to_capture:
      ret, frame = camera.capture.read()
      if (datetime.now() - last_capture_timestamp).total_seconds() > 4:
        print('Capturing frame')
        last_capture_timestamp = datetime.now()

        frame = camera.calibration.restore(frame)
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        images.append(gray)

        captured_count += 1
        if captured_count >= capture_limit:
          more_to_capture = False

    print('Frames captured, processing...')

    aruco_dictionary = cv.aruco.Dictionary_get(cv.aruco.DICT_6X6_250)
    # board = cv.aruco.CharucoBoard_create(7, 5, 3.57, 2.82, aruco_dictionary)
    board = cv.aruco.CharucoBoard_create(7, 5, 7.4, 5.7, aruco_dictionary)
    parameters = cv.aruco.DetectorParameters_create()

    allCorners = []
    allIds = []
    decimator = 0

    imsize = images[0].shape
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 100, 0.00001)

    for img in images:
      corners, ids, rejectedImgPoints = cv.aruco.detectMarkers(img, aruco_dictionary)
      if len(corners) > 0:
        for corner in corners:
          cv.cornerSubPix(img, corner, winSize=(3, 3), zeroZone=(-1, -1), criteria=criteria)

        res2 = cv.aruco.interpolateCornersCharuco(corners, ids, img, board)

        if res2[1] is not None and res2[2] is not None and len(res2[1]) > 3 and decimator % 1 == 0:
          allCorners.append(res2[1])
          allIds.append(res2[2])

      decimator += 1

    print('Calibrating camera position...')

    cameraMatrixInit = np.array([
      [1000.0, 0.0, imsize[0] / 2.0],
      [0.0, 1000.0, imsize[1] / 2.0],
      [0.0, 0.0, 1.0]
    ])

    distCoeffsInit = np.zeros((5, 1))
    flags = (cv.CALIB_USE_INTRINSIC_GUESS + cv.CALIB_RATIONAL_MODEL + cv.CALIB_FIX_ASPECT_RATIO)
    (
      ret,
      camera_matrix,
      distortion_coefficients,
      camera_rvecs,
      camera_tvecs,
      stdDeviationsIntrinsics,
      stdDeviationsExtrinsicts,
      perViewErrors
    ) = cv.aruco.calibrateCameraCharucoExtended(
      charucoCorners=allCorners,
      charucoIds=allIds,
      board=board,
      imageSize=imsize,
      cameraMatrix=cameraMatrixInit,
      distCoeffs=distCoeffsInit,
      flags=flags,
      criteria=(cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_COUNT, 10000, 1e-9)
    )








    # N_OK = len(objpoints)
    # K = np.zeros((3, 3))
    # D = np.zeros((4, 1))
    # rvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(N_OK)]
    # tvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(N_OK)]
    # rms, _, _, _, _ = cv.fisheye.calibrate(
    #   objpoints,
    #   imgpoints,
    #   gray.shape[::-1],
    #   K,
    #   D,
    #   rvecs,
    #   tvecs,
    #   calibration_flags,
    #   (cv.TERM_CRITERIA_EPS+cv.TERM_CRITERIA_MAX_ITER, 30, 1e-6)
    # )
    # print("Found " + str(N_OK) + " valid images for calibration")
    # print("DIM=" + str(_img_shape[::-1]))
    # print("K=np.array(" + str(K.tolist()) + ")")
    # print("D=np.array(" + str(D.tolist()) + ")")


    print('cam:', camera_matrix)
    print('dist:', distortion_coefficients)

    calibration = {
      'camera_matrix': list([list(arry) for arry in camera_matrix]),
      'distortion_coefficients': list([list(arry) for arry in distortion_coefficients]),
      'board_type': cv.aruco.DICT_6X6_250,
      'board_width': 5,
      'board_height': 7,
      'cell_size': 7.4,
      'marker_size': 5.7
    }

    with open('config/calibration.json', 'w') as fp:
      json.dump(calibration, fp)
    print('Calibration finished and written to file.')

  elif FUNC == 'test_calibration':
    spotted = Spotted()

    # spotted.start_websocket()
    # start_ui()

    # pattern = [x, y, z]
    pattern = np.array([189.7, 27.6, 340.2])

    camera = spotted.cameras[1]
    with open('config/calibration.json', 'r') as fp:
      calibration = json.load(fp)

    aruco_dictionary = cv.aruco.Dictionary_get(calibration['board_type'])
    board = cv.aruco.CharucoBoard_create(
      calibration['board_height'],
      calibration['board_width'],
      calibration['cell_size'],
      calibration['marker_size'],
      aruco_dictionary
    )
    parameters = cv.aruco.DetectorParameters_create()
    camera_matrix = np.array(calibration['camera_matrix'])
    distortion_coefficients = np.array(calibration['distortion_coefficients'])

    frame_count = 60

    rotations = []
    tvecs = []

    while frame_count > 0:
      ret, frame = camera.capture.read()
      frame = camera.calibration.restore(frame)

      corners, ids, rejectedImgPoints = cv.aruco.detectMarkers(
        frame,
        aruco_dictionary,
        parameters=parameters
      )
      cv.aruco.refineDetectedMarkers(frame, board, corners, ids, rejectedImgPoints)

      if ids is not None:
        charuco_ret, charuco_corners, charuco_ids = cv.aruco.interpolateCornersCharuco(
          corners,
          ids,
          frame,
          board
        )

        frame = cv.aruco.drawDetectedCornersCharuco(frame, charuco_corners, charuco_ids, (255))
        retval, rvec, tvec = cv.aruco.estimatePoseCharucoBoard(
          charuco_corners,
          charuco_ids,
          board,
          camera_matrix,
          distortion_coefficients,
          np.array([]),
          np.array([])
        )

        if retval:
          frame = cv.aruco.drawAxis(frame, camera_matrix, distortion_coefficients, rvec, tvec, 100)
          # print('rvec:', rvec)
          R, jacobean = cv.Rodrigues(rvec)

          initial_rotation = np.array([ # -90 in z then 90 in x
            [0.0, 0.0, -1.0],
            [-1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0]
          ])

          # R = -R.dot(initial_rotation)
          # R = initial_rotation.dot(-R)
          inv_r = np.linalg.inv(R)
          cam_pos = -inv_r.dot([pos[0] for pos in tvec])
          #  = R.dot(tvec)
          # r = [
          #   r11, r12, r13
          #   r21, r22, r23
          #   r31, r32, r33
          # ]

          # z = o, y = theta, x = /v

          x = 0.0
          y = 0.0
          z = 0.0

          if R[2][0] != -1 and R[2][0] != 1:
            x = -math.asin(R[2][0])
            z = math.atan2((R[2][1]/math.cos(x)), (R[2][2]/math.cos(x)))
            y = math.atan2((R[1][0]/math.cos(x)), (R[0][0]/math.cos(x)))
          else:
            y = 0
            if R[2][0] == -1:
              x = math.pi / 2.0
              z = math.atan2(R[0][1], R[0][2])
            else:
              x = -math.pi / 2.0
              z = math.atan2(-R[0][1], -R[0][2])

          x = round(math.degrees(x), 2)
          y = round(math.degrees(y), 2)
          z = round(math.degrees(z), 2)


          # spotted.current_state['rotations'] = [y, z, x]
          # print('rod:', R)
          # camera_rotation = np.array([-x, z, y])
          camera_rotation = np.array([x, y, z])

          print('rotation:', camera_rotation)
          print('tvec:', tvec)

          distance = math.sqrt(sum([axis**2 for axis in tvec]))

          unit_vector = np.array([distance, 0, 0])
          # pos = R.dot(unit_vector)
          pos = R.dot(unit_vector)
          pos = np.array(pos) + pattern
          print('dist in x:', pos)

          unit_vector = [0, distance, 0]
          pos = R.dot(unit_vector)
          pos = np.array(pos) + pattern
          print('dist in y:', pos)

          unit_vector = [0, 0, distance]
          pos = R.dot(unit_vector)
          pos = np.array(pos) + pattern
          print('dist in z:', pos)

          print('distance:', distance)

          # rot = np.array([pos[0] for pos in rot])

          # print('new dist', rot + pattern)

          print('cam_pos:', cam_pos)
      frame = cv.resize(frame, (960, 720))
      cv.imshow('frame', frame)
      cv.waitKey(1)
