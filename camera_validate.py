from spotted.spotted.spotted import Spotted
from spotted.spotted.coordinate import Coordinate
import threading
import time
import queue
import cv2 as cv
import numpy as np
import sys

spotted = Spotted()


daemon = False

for camera in spotted.cameras:
  threading.Thread(target=camera.begin_capture, daemon=daemon).start()

transmit = queue.Queue()
threading.Thread(target=spotted.start_artnet, args=(transmit,), daemon=daemon).start()
threading.Thread(target=spotted.start_artnet_reply, args=(transmit,), daemon=daemon).start()
threading.Thread(target=spotted.artnet_transmitter, args=(transmit,), daemon=daemon).start()

for universe in spotted.universes.universes:
  for fixture in universe.fixtures:
    threading.Thread(target=fixture.follow, daemon=daemon).start()

time.sleep(3)

for _ in range(255):
  point = Coordinate(2.0, 0.0, 4.5)
  for fixture in spotted.universes.universes[0].fixtures:
    fixture.point_at(point)
    fixture.open()
    # self.current_state['maps'][fixture.fixture_id] = id(live_pois[index])
time.sleep(2)

outframe = None
if spotted.cameras[0].current_frame is not None:
  out_frame = spotted.cameras[0].current_frame
if spotted.cameras[1].current_frame is not None:
  if out_frame is not None:
    out_frame = np.vstack((out_frame, spotted.cameras[1].current_frame))
  else:
    out_frame = spotted.cameras[1].current_frame
if out_frame is not None:
  cv.imshow('VIDEO', out_frame)
  cv.waitKey(1000)



pois = spotted.combine_points()

for camera in spotted.cameras:
  print(camera.points_of_interest[0].direction_vector)

poi = pois[0]
print(poi.position.x)
print(poi.position.y)
print(poi.position.z)

print(pois)

# sys.exit(0)
