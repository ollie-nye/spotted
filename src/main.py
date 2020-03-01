import cv2 as cv
import numpy as np
import sys

import json

from datetime import datetime

from spotted_camera import SpottedCamera
from spotted_personality import SpottedPersonality
from spotted_fixture import SpottedFixture
from spotted_universe import SpottedUniverse
from spotted_universes import SpottedUniverses
from spotted_coordinate import SpottedCoordinate
from spotted_room import SpottedRoom
from spotted_calibration import SpottedCalibration



from artnet_dmx import ArtnetDmx
import time
import threading
import sys, socket

cameras_json = json.load(open('config/cameras.json'))
config_json = json.load(open('config/config.json'))
fixtures_json = json.load(open('config/fixtures.json'))

cameras = []
for camera in cameras_json:
  cameras.append(SpottedCamera(camera))

calibration = SpottedCalibration(config_json['calibration'])

universes = SpottedUniverses()
universe = SpottedUniverse(0, 0, 0)
for fixture in fixtures_json:
  fxt = SpottedFixture(fixture)
  universe.add_fixture(fxt)
universes.add_universe(universe)


count = 0

start = datetime.now()

def int_to_float(frame):
  return np.array(frame, dtype=np.float)

def float_to_int(frame):
  return np.array(frame, dtype=np.uint8)

def normalize(frame):
  cv.normalize(frame, frame, 255, 0)
  return frame

# while(count < 1200):
#   for index, camera in enumerate(cameras):
#     print('Capturing from camera ', index)
    

#     else:
#       print('Skipped a frame')

#   count += 1
#   print('Count ', count)

# finish = datetime.now()

# print(count, 'cycles took', (finish - start).total_seconds(), 'for a frame rate of', count / (finish - start).total_seconds())

# cv.imshow('VIDEO', cameras[0].current_background)
# cv.waitKey(10000)

# cv.imwrite('output.png', cameras[0].current_background)




  
def start_artnet():
  print('Starting artnet')
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

  while(1):
    for universe in universes.universes:
      output = universe.get_levels()
      packet = ArtnetDmx(output)
      sock.sendto(packet.serialize(), ('10.0.0.50', 6454))
      time.sleep(1/30)


  

room = SpottedRoom(4, 2.4, 4.5)

for fixture in universes.universes[0].fixtures:
  fixture.calibrate(room)

artnet = threading.Thread(target=start_artnet, daemon=True)
artnet.start()

for camera in cameras:
  thrd = threading.Thread(target=camera.begin_capture, daemon=True, args=[calibration])
  thrd.start()

# while(1):
#   if len(cameras[0].points_of_interest) > 0:
#     for universe in universes.universes:
#       for fixture in universe.fixtures:
#         fixture.point_at(cameras[0].points_of_interest[0])
#         fixture.open()
#   else:
#     for universe in universes.universes:
#       for fixture in universe.fixtures:
#         fixture.close()

#   if cameras[0].current_frame is not None:
#     frame = cv.resize(cameras[0].current_frame, (960, 720))
#     cv.imshow('VIDEO', frame)
#     cv.waitKey(1)
#     time.sleep(1/100)




while(1):
#   for fixture in universes.universes[0].fixtures:
#     fixture.point_at(SpottedCoordinate(0, 2.0, 4.0))
#   time.sleep(2)

#   for fixture in universes.universes[0].fixtures:
#     fixture.point_at(SpottedCoordinate(3.3, 2.0, 4.0))
#   time.sleep(2)

  for fixture in universes.universes[0].fixtures:
    fixture.point_at(SpottedCoordinate(2, 0, 2.25))
  time.sleep(2)

#   for fixture in universes.universes[0].fixtures:
#     fixture.point_at(SpottedCoordinate(0, 1.2, 2.5))
#   time.sleep(2)

