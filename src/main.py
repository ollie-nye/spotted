import cv2 as cv
import numpy as np
import sys

import json

from datetime import datetime

from spotted_camera import SpottedCamera
from spotted_personality import SpottedPersonality

cameras_json = json.load(open('config/cameras.json'))
config_json = json.load(open('config/config.json'))
fixtures_json = json.load(open('config/fixtures.json'))
personalities_json = json.load(open('config/personalities.json'))

cameras = []
personalities = []

for camera in cameras_json:
  cameras.append(SpottedCamera(camera))

# def process_frame(frame):
  #   frame = downsample(frame[0])
  #   # print('Frame processed')
  #   return frame
  # else:
  #   return False

count = 0

start = datetime.now()

def int_to_float(frame):
  return np.array(frame, dtype=np.float)

def float_to_int(frame):
  return np.array(frame, dtype=np.uint8)

def normalize(frame):
  cv.normalize(frame, frame, 255, 0)
  return frame

while(count < 180):
  for index, camera in enumerate(cameras):
    print('Capturing from camera ', index)
    ret, frame = camera.capture.read()
    if frame is not None:
      frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
      # cv.threshold(frame, 120, 255, cv.THRESH_TOZERO, frame)
      camera.update_background(frame)

      # frame[500:540, :] = 255

      # cv.imshow('VIDEO', frame)

      diff = np.subtract(frame, float_to_int(camera.current_background))

      print(diff[0,0])

      cv.threshold(diff, 160, 255, cv.THRESH_TOZERO, diff)
      cv.threshold(diff, 180, 255, cv.THRESH_TOZERO_INV, diff)

      # cv.normalize(diff, diff, 0, 255, cv.NORM_MINMAX)

      # diff = float_to_int(diff)
      # ret, diff = cv.threshold(float_to_int(diff), 200, 255, cv.THRESH_TOZERO)
      # cv.imshow('VIDEO', float_to_int(camera.current_background))

      # diff = float_to_int(camera.current_background)

      diff = cv.resize(diff, ( 1024, 576 ))
      cv.imshow('VIDEO', diff)
      # cv.imshow('VIDEO', frame)
      cv.waitKey(1)

    else:
      print('Skipped a frame')

  count += 1
  print('Count ', count)

finish = datetime.now()

print(count, ' cycles took ', (finish - start).total_seconds())

# cv.imshow('VIDEO', cameras[0].current_background)
# cv.waitKey(10000)

# cv.imwrite('output.png', cameras[0].current_background)
