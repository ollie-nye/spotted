import cv2 as cv
import numpy as np
import sys

import json

from datetime import datetime

from spotted.camera import Camera
from spotted.personality import Personality, load_personalities
from spotted.fixture import Fixture
from spotted.universe import Universe
from spotted.universes import Universes
from spotted.coordinate import Coordinate
from spotted.room import Room
from spotted.calibration import Calibration

import math

from artnet.dmx import Dmx
import time
import threading
import sys, socket

from http.server import HTTPServer
from spotted.static_server import StaticServer
from spotted.websocket import Websocket
# from spotted.websocket_server import Websocket
import asyncio
import websockets
import os

config_json = json.load(open('config/config.json'))
load_personalities('config/personalities.json')

current_state = dict()

# cameras = []
# for camera in config_json['cameras']:
#   cameras.append(Camera(camera))

calibration = Calibration(config_json['calibration'])

universes = Universes()
# universe = Universe(0, 0, 0)
for fixture in config_json['fixtures']:
  fxt = Fixture(fixture)
  universe = universes.get_universe(fxt.net, fxt.subnet, fxt.universe)
  if universe is None:
    universe = Universe(fxt.net, fxt.subnet, fxt.universe)
    universes.add_universe(universe)
  universe.add_fixture(fxt)


count = 0

start = datetime.now()

def int_to_float(frame):
  return np.array(frame, dtype=np.float)

def float_to_int(frame):
  return np.array(frame, dtype=np.uint8)

def normalize(frame):
  cv.normalize(frame, frame, 255, 0)
  return frame

def start_artnet():
  print('Starting artnet')
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

  while(1):
    for universe in universes.universes:
      packet = Dmx(0, universe)
      sock.sendto(packet.serialize(), ('10.0.0.50', 6454))
      time.sleep(1/30)


room_json = config_json['room']
room = Room(room_json['x'], room_json['y'], room_json['z'])

for fixture in universes.universes[0].fixtures:
  fixture.calibrate(room)

# artnet = threading.Thread(target=start_artnet, daemon=True)
# artnet.start()

# for camera in cameras:
#   thrd = threading.Thread(target=camera.begin_capture, daemon=True, args=[calibration])
#   thrd.start()

def combine_points():
  pois1 = cameras[0].points_of_interest
  pois2 = cameras[1].points_of_interest

  if len(pois1) > 0:
    if len(pois2) > 0:
      # for poi in pois2:
      #   print('Camera 1 can see', poi.position.as_vector())
      highest_weight_1 = 0
      poi1 = None
      highest_weight_2 = 0
      poi2 = None
      for poi in pois1:
        if poi.weight >= highest_weight_1:
          highest_weight_1 = poi.weight
          poi1 = poi

      for poi in pois2:
        if poi.weight >= highest_weight_2:
          highest_weight_2 = poi.weight
          poi2 = poi

      u = poi1.direction_vector
      v = poi2.direction_vector

      # print('u:', u, 'v:', v)

      a = np.dot(u, u)
      b = np.dot(u, v)
      c = np.dot(v, v)
      w = np.subtract(poi1.position.as_vector(), poi2.position.as_vector())
      d = np.dot(u, w)
      e = np.dot(v, w)

      # print('a:', a, 'b:', b, 'c:', c, 'd:', d, 'e:', e, 'w:', w)

      acb = (a * c) - (b * b)

      # print('acb:', acb)

      s = ((b * e) - (c * d)) / acb
      t = ((a * e) - (b * d)) / acb

      # print('s:', s, 't:', t)

      s = np.dot(s, u)
      t = np.dot(t, v)

      # print('s:', s, 't:', t)

      ps = np.add(poi1.position.as_vector(), s)
      qt = np.add(poi2.position.as_vector(), t)

      # print('ps:', ps, 'qt:', qt)

      # distance = abs(w + ((((b * e) - (c * d) * u) - ((a * e) - (b * d) * v)) / acb))

      # print('Shortest distance between', poi1.direction_vector, poi2.direction_vector)

      # z = [
      #   abs(s[0] - t[0]),
      #   abs(s[1] - t[1]),
      #   abs(s[2] - t[2]),
      # ]

      z = abs(np.subtract(t, s))

      # print('z:', z)
      distance = np.add(w, z)

      # print(distance)

      euclid_distance = math.sqrt(distance[0]**2 + distance[1]**2 + distance[2]**2)

      print(euclid_distance)

      # euclid_distance = math.sqrt(math.pow((ps[0] - qt[0]), 2) + math.pow((ps[1] - qt[1]), 2) + math.pow((ps[2] - qt[2]), 2))

      # print('Shortest distance between', poi1.direction_vector, poi2.direction_vector, 'is', euclid_distance)
      # print('Shortest distance is', distance)

      abs_point = np.add(qt, ps) / 2
      world_point = Coordinate(abs_point[0], abs_point[1], abs_point[2])
      print('Real world point is', abs_point)

      for universe in universes.universes:
        for fixture in universe.fixtures:
          fixture.point_at(world_point)

# while(1):
#   # if len(cameras[0].points_of_interest) > 0:
#   #   for universe in universes.universes:
#   #     for fixture in universe.fixtures:
#   #       fixture.point_at(cameras[0].points_of_interest[0])
#   #       fixture.open()
#   # else:
#   #   for universe in universes.universes:
#   #     for fixture in universe.fixtures:
#   #       fixture.close()

#   combine_points()

#   out_frame = None
#   if cameras[0].current_frame is not None:
#     out_frame = cameras[0].current_frame
#   if cameras[1].current_frame is not None:
#     if out_frame is not None:
#       out_frame = np.hstack((out_frame, cameras[1].current_frame))
#     else:
#       out_frame = cameras[1].current_frame
#   if out_frame is not None:
#     cv.imshow('VIDEO', out_frame)
#     cv.waitKey(1)
#   time.sleep(1/30)



# import curses
# stdscr = curses.initscr()
# curses.cbreak()
# stdscr.keypad(1)

# stdscr.addstr(0,10,"Hit 'q' to quit")
# stdscr.refresh()

fixture = universes.universes[0].fixtures[0]

# key = ''
# curses.noecho()
# while key != ord('q'):
#   key = stdscr.getch()
#   # stdscr.addch(20,25,key)
#   stdscr.refresh()
#   if key == curses.KEY_UP:
#     fixture.location = fixture.location.displace_by(Coordinate(0.01, 0, 0))
#     fixture.point_at(Coordinate(0, 0, 0))
#   elif key == curses.KEY_DOWN:
#     fixture.location = fixture.location.displace_by(Coordinate(-0.01, 0, 0))
#     fixture.point_at(Coordinate(0, 0, 0))
#   print(fixture.location.as_vector())

# curses.endwin()



# fixture.point_at(Coordinate(1, 0, 0))
# fixture.point_at(Coordinate(0, 1, 0))
# fixture.point_at(Coordinate(0, 0, 1))
# fixture.point_at(Coordinate(1, 1, 1))
# fixture.point_at(Coordinate(-1, 0, 0))
# fixture.point_at(Coordinate(0, -1, 0))
# fixture.point_at(Coordinate(0, 0, -1))
# fixture.point_at(Coordinate(-1, -1, -1))









def start_ui(server_class=HTTPServer, handler_class=StaticServer, port=8080):
  server_address = ('', port)
  httpd = server_class(server_address, handler_class)
  print('Starting httpd on port', port)
  httpd.serve_forever()

def start_websocket(port=8081):
  loop = asyncio.new_event_loop()
  asyncio.set_event_loop(loop)
  ws = Websocket(config_json, current_state)
  start_server = websockets.serve(ws.push_state, '0.0.0.0', port)
  print('Created websocket server')
  loop.create_task(ws.broadcast_state(1/30))
  loop.run_until_complete(start_server)
  loop.run_forever()

ui = threading.Thread(target=start_ui, daemon=True)
ui.start()

websocket = threading.Thread(target=start_websocket, daemon=True)
websocket.start()
# start_websocket()







incoming_frame = cv.cvtColor(cv.imread('ui/favicon.png'), cv.COLOR_BGR2GRAY).tolist()



while(1):
  for x in range(360):
    # for y in range(1):
    # for z in range(360):
    current_state.clear()
    point = Coordinate(2 + (2 * math.sin(math.radians(x))), 1, 2 + (2 *math.cos(math.radians(x))))
    current_state['subjects'] = []
    current_state['subjects'].append(point.as_dict())
    current_state['maps'] = dict()
    current_state['frames'] = []
    current_state['frames'].append(incoming_frame)
    for fixture in universes.universes[0].fixtures:
      fixture.point_at(point)
      current_state['maps'][fixture.fixture_id] = 0
    print('Pointing at', x, 0, x)
    time.sleep(0.01)

#   for fixture in universes.universes[0].fixtures:
#     fixture.point_at(Coordinate(3.3, 2.0, 4.0))
#   time.sleep(2)

#   for fixture in universes.universes[0].fixtures:
#     fixture.point_at(Coordinate(2, 0, 2.25))
#   time.sleep(2)

#   for fixture in universes.universes[0].fixtures:
#     fixture.point_at(Coordinate(0, 1.2, 2.5))
#   time.sleep(2)
