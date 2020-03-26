"""
Spotted
"""

import sys
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
from spotted.point_of_interest import PointOfInterest
from spotted.fixture import Fixture
from spotted.universe import Universe
from spotted.universes import Universes
from spotted.coordinate import Coordinate
from spotted.room import Room
from spotted.calibration import Calibration
from spotted.websocket import Websocket
from spotted.static_server import StaticServer

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

    try:
      self.config = json.load(open('config/config.json'))
      load_personalities('config/personalities.json')
    except FileNotFoundError as error:
      print('A required config file could not be found:', error)
      sys.exit(2)

    self.current_state = dict()

    if 'calibration' in self.config:
      self.calibration = Calibration(self.config['calibration'])
    else:
      print("'calibration' key does not exist in the config")
      sys.exit(3)

    self.cameras = []
    if 'cameras' in self.config:
      for index, camera in enumerate(self.config['cameras']):
        cam = Camera(camera, self.calibration)
        self.cameras.append(cam)
        self.config['cameras'][index]['initial_point'] = cam.initial_point.as_dict()
    else:
      print("'cameras' key does not exist in the config")
      sys.exit(3)

    for camera in self.cameras:
      if not camera.capture.isOpened():
        print('Camera', camera.cam_id, 'could not be opened. Exiting')
        sys.exit(4)

    if 'room' in self.config:
      room_json = self.config['room']
      self.room = Room(room_json['x'], room_json['y'], room_json['z'])
    else:
      print("'room' key does not exist in the config")
      sys.exit(3)

    self.universes = Universes()
    if 'fixtures' in self.config:
      for fixture_config in self.config['fixtures']:
        fixture = Fixture(fixture_config)
        addr = fixture.address
        universe = self.universes.get_universe(addr['net'], addr['subnet'], addr['universe'])
        if universe is None:
          universe = Universe(addr['net'], addr['subnet'], addr['universe'])
          self.universes.add_universe(universe)
        universe.add_fixture(fixture)
      self.pois = []
    else:
      print("'fixtures' key does not exist in the config")
      sys.exit(3)




  # pylint: disable=invalid-name, too-many-locals
  def calculate_intersection(self, poi1, poi2, close_enough, points):
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

    if euclid_distance > 0.5:
      close_enough = False
    else:
      ps = np.add(poi1.position.as_vector(), s)
      qt = np.add(poi2.position.as_vector(), t)
      abs_point = np.add(qt, ps) / 2
      if not((0 <= abs_point[0] <= self.room.width) and (0 <= abs_point[1] <= self.room.height) and (0 <= abs_point[2] <= self.room.depth)):
        close_enough = False
      else:
        points.append(abs_point)

    return (close_enough, points)

  def update_pois(self):
    """

    """
    current_pois = self.combine_points()

    updated_pois = []

    print('There are', len(current_pois), 'pois coming in')

    for incoming_poi in current_pois:
      made_update = False
      if len(self.pois) > 0:
        poi = sorted(self.pois, key=lambda p: p.diff_from_position(incoming_poi.position))[0]
        diff_from_pos = poi.diff_from_position(incoming_poi.position)
        if diff_from_pos < 0.50:
          print('Updated position')
          poi.update_position(incoming_poi.position)
          poi.increment_count()
          updated_pois.append(poi)
          made_update = True
          break

        if not made_update:
          poi = PointOfInterest(incoming_poi.position, decrement_step=2)
          updated_pois.append(poi)
          self.pois.append(poi)
      else:
        poi = PointOfInterest(incoming_poi.position, decrement_step=2)
        updated_pois.append(poi)
        self.pois.append(poi)


    missing_pois = set(self.pois) - set(updated_pois)
    for poi in missing_pois:
      poi.decrement_count()

    self.pois = [p for p in self.pois if p.count != 1]
    self.pois = sorted(self.pois, key=lambda p: p.weight, reverse=True)

    print('There are', len(self.pois), 'pois going out')

    for poi in self.pois:
      print(poi, poi.weight)

  def combine_points(self):
    """
    Intersects all points from all cameras to find possible 3d world points of
    interest
    """

    pois = [camera.points_of_interest for camera in self.cameras]
    if len(pois) == 0:
      return []

    pois = list(itertools.product(*pois))

    # print('There are', len(pois), 'possible pois')

    points_of_interest = []

    for poi in pois:
      close_enough = True

      points = []

      for poi1, poi2 in itertools.combinations(poi, len(poi)):
        close, points = self.calculate_intersection(poi1, poi2, close_enough, points)
        if not close:
          close_enough = False

      if close_enough:
        poi = PointOfInterest(Coordinate(*np.mean(list(zip(*points)), axis=1)))
        points_of_interest.append(poi)

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
        sock.sendto(packet.serialize(), (self.config['artnet'], 6454))
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

    threading.Thread(target=start_ui, daemon=True).start()
    threading.Thread(target=self.start_websocket, daemon=True).start()

    for camera in self.cameras:
      threading.Thread(target=camera.begin_capture, daemon=True).start()

    threading.Thread(target=self.start_artnet, daemon=True).start()

    # coords = [
    #   (0, 0),
    #   (640, 0),
    #   (640, 480),
    #   (0, 480),
    #   (320, 240)
    # ]

    # for coord in coords:
    #   real_coord = self.cameras[0].calculate_real_world_coordinate(coord)
    #   print(coord, 'is at', real_coord.x, real_coord.y, real_coord.z)
    # exit()

    last_poi = None

    while 1:
      self.update_pois()

      # live_pois = [p for p in self.pois if p.weight > 2.5]
      live_pois = self.pois

      self.current_state['cameras'] = {}
      for camera in self.cameras:
        self.current_state['cameras'][camera.cam_id] = [poi.position.as_vector().tolist() for poi in camera.points_of_interest]

      self.current_state['subjects'] = {}
      for poi in live_pois:
        self.current_state['subjects'][id(poi)] = poi.position.as_dict()

      if len(live_pois) > 0:
        # if last_poi is None:
        #   last_poi = pois[0]
        #   point = pois[0]
        # else:
        #   next_poi = None
        #   shortest_distance = 1000
        #   for poi in pois:
        #     diff_x = (last_poi.x - poi.x) ** 2
        #     diff_y = (last_poi.y - poi.y) ** 2
        #     diff_z = (last_poi.z - poi.z) ** 2
        #     distance = math.sqrt(diff_x + diff_y + diff_z)
        #     if distance < shortest_distance:
        #       shortest_distance = distance
        #       next_poi = poi
        #   point = next_poi


        print('There are', len(live_pois), 'points of interest')

        # point = Coordinate(0.2, 1.7, 3.0)

        self.current_state['maps'] = dict()

        fixture_count = len(self.universes.universes[0].fixtures)
        poi_count = len(live_pois)

        for index in range(min(poi_count, fixture_count)):
          fixture = self.universes.universes[0].fixtures[index]
          fixture.point_at(live_pois[index].position)
          fixture.open()
          self.current_state['maps'][fixture.fixture_id] = id(live_pois[index])

          # time.sleep(1/30)
      else:
        for fixture in self.universes.universes[0].fixtures:
          fixture.close()

      # out_frame = None
      # if self.cameras[0].current_frame is not None:
      #   out_frame = self.cameras[0].current_frame
      # if self.cameras[1].current_frame is not None:
      #   if out_frame is not None:
      #     out_frame = np.hstack((out_frame, self.cameras[1].current_frame))
      #   else:
      #     out_frame = self.cameras[1].current_frame
      # if out_frame is not None:
      #   cv.imshow('VIDEO', out_frame)
      #   cv.waitKey(1)
      time.sleep(1/30)
