"""
Spotted
"""

import math
import json

import time
import threading
import socket
import asyncio
import itertools

from http.server import HTTPServer

import websockets

import numpy as np
import cv2 as cv

from artnet.dmx import Dmx
from spotted.camera import Camera
from spotted.personality import load_personalities
from spotted.fixture import Fixture
from spotted.universe import Universe
from spotted.universes import Universes
from spotted.coordinate import Coordinate
from spotted.room import Room
from spotted.calibration import Calibration
from spotted.websocket import Websocket
from spotted.static_server import StaticServer

# pylint: disable=invalid-name, too-many-locals
def calculate_intersection(poi1, poi2, close_enough, points):
  """
  Determines if poi1 is close enough to poi2 to be a possibility for an intersection
  """

  u = poi1.direction_vector
  v = poi2.direction_vector

  a = np.dot(u, u)
  b = np.dot(u, v)
  c = np.dot(v, v)

  w = np.subtract(poi1.position.as_vector(), poi2.position.as_vector())
  d = np.dot(u, w)
  e = np.dot(v, w)

  acb = (a * c) - (b * b)

  s = np.dot(((b * e) - (c * d)) / acb, u)
  t = np.dot(((a * e) - (b * d)) / acb, v)

  z = abs(np.subtract(t, s))

  distance = np.add(w, z)

  euclid_distance = math.sqrt(distance[0]**2 + distance[1]**2 + distance[2]**2)

  if euclid_distance > 0.2:
    close_enough = False
  else:
    ps = np.add(poi1.position.as_vector(), s)
    qt = np.add(poi2.position.as_vector(), t)
    abs_point = np.add(qt, ps) / 2
    points.append(abs_point)

  return (close_enough, points)

def start_ui(server_class=HTTPServer, handler_class=StaticServer, port=8080):
  """
  UI thread
  """

  print('Starting UI on port', port)
  server_address = ('', port)
  httpd = server_class(server_address, handler_class)
  httpd.serve_forever()

class Spotted:
  """
  Spotted
  """

  def __init__(self):
    """
    Create spotted instance
    Sets up state, calibration, personalities, cameras, room, fixtures and universes
    """

    self.config = json.load(open('config/config.json'))
    load_personalities('config/personalities.json')

    self.current_state = dict()
    self.calibration = Calibration(self.config['calibration'])
    self.cameras = []
    for camera in self.config['cameras']:
      self.cameras.append(Camera(camera, self.calibration))


    room_json = self.config['room']
    self.room = Room(room_json['x'], room_json['y'], room_json['z'])

    self.universes = Universes()
    for fixture_config in self.config['fixtures']:
      fixture = Fixture(fixture_config)
      addr = fixture.address
      universe = self.universes.get_universe(addr['net'], addr['subnet'], addr['universe'])
      if universe is None:
        universe = Universe(addr['net'], addr['subnet'], addr['universe'])
        self.universes.add_universe(universe)
      universe.add_fixture(fixture)

  def combine_points(self):
    """
    Intersects all points from all cameras to find possible 3d world points of
    interest
    """

    pois = []
    for camera in self.cameras:
      pois.append(camera.points_of_interest)
    if len(pois) == 0:
      return []

    pois = list(itertools.product(*pois))

    points_of_interest = []

    for poi in pois:
      close_enough = True

      points = []

      for poi1, poi2 in itertools.combinations(poi, len(poi)):
        close, points = calculate_intersection(poi1, poi2, close_enough, points)
        if not close:
          close_enough = False

      if close_enough:
        points_of_interest.append(Coordinate(*np.mean(list(zip(*points)), axis=1)))

    return points_of_interest

  def start_artnet(self):
    """
    ArtNet transmission thread
    """

    print('Starting artnet')
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while 1:
      for universe in self.universes.universes:
        packet = Dmx(0, universe)
        sock.sendto(packet.serialize(), ('10.0.0.50', 6454))
        time.sleep(1/30)

  def start_websocket(self, port=8081):
    """
    Websocket thread
    """

    print('Starting websocket server on port', port)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    websocket = Websocket(self.config, self.current_state)
    start_server = websockets.serve(websocket.push_state, '0.0.0.0', port)
    loop.create_task(websocket.broadcast_state(1/30))
    loop.run_until_complete(start_server)
    loop.run_forever()

  def start_spotted(self):
    """
    Starts up all essential threads and drops to processing points from cameras
    """

    threading.Thread(target=self.start_artnet, daemon=True).start()
    threading.Thread(target=start_ui, daemon=True).start()
    threading.Thread(target=self.start_websocket, daemon=True).start()

    for camera in self.cameras:
      threading.Thread(target=camera.begin_capture, daemon=True).start()

    while 1:
      # pois = self.combine_points()
      # if len(pois) > 0:
        # point = pois[0]
      point = Coordinate(2.8, 1.7, 2.5)
      # self.current_state.clear()
      self.current_state['subjects'] = []
      self.current_state['subjects'].append(point.as_dict())
      self.current_state['maps'] = dict()
      for fixture in self.universes.universes[0].fixtures:
        fixture.point_at(point)
        self.current_state['maps'][fixture.fixture_id] = 0

        # time.sleep(1/30)

        out_frame = None
        if self.cameras[0].current_frame is not None:
          out_frame = self.cameras[0].current_frame
        if self.cameras[1].current_frame is not None:
          if out_frame is not None:
            out_frame = np.hstack((out_frame, self.cameras[1].current_frame))
          else:
            out_frame = self.cameras[1].current_frame
        if out_frame is not None:
          cv.imshow('VIDEO', out_frame)
          cv.waitKey(1)
        time.sleep(1/30)
