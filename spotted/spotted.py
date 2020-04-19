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
import netifaces
import queue

from http.server import HTTPServer
import websockets
from datetime import datetime

import numpy as np
import cv2 as cv

from artnet.dmx import Dmx
from artnet.poll import Poll
from artnet.poll_reply import PollReply
from artnet.deserialize import identify_header
from artnet.opcode import Opcode
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
from spotted.helpers import scale
from spotted.error import ErrorCode, exit_with_error
from config.system import SystemConfig

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

  def __init__(self, skip_cameras=False):
    """
    Create spotted instance
    Sets up state, calibration, personalities, cameras, room, fixtures and universes
    """

    try:
      self.config = json.load(open('config/config.json'))
      load_personalities('config/personalities.json')
    except FileNotFoundError as error:
      exit_with_error(ErrorCode.MissingConfig, error)

    self.current_state = dict()
    self.pois = []

    self.setup_interface()

    self.setup_calibration()
    self.cameras = []
    if not skip_cameras:
      self.setup_cameras()
    self.setup_room()
    self.setup_fixtures()
    self.setup_max_subjects()

  def setup_interface(self):
    """
    Validates configured interfaces against available system interfaces and
    returns the first IPv4 address of the given interface
    """

    host_interfaces = netifaces.interfaces()

    if 'network_interface' in self.config:
      if self.config['network_interface'] in host_interfaces:
        addresses = netifaces.ifaddresses(self.config['network_interface'])
        if netifaces.AF_INET in addresses:
          address = addresses[netifaces.AF_INET][0]
          self.ip_address = address['addr']
          self.broadcast_address = address['broadcast']
        else:
          exit_with_error(ErrorCode.InterfaceAddress, self.config['network_interface'])
      else:
        details = (self.config['network_interface'], host_interfaces)
        exit_with_error(ErrorCode.MissingInterface, details)
    else:
      exit_with_error(ErrorCode.MissingKey, 'network_interface')

  def setup_calibration(self):
    """
    Creates the calibration object from config
    """

    if 'calibration' in self.config:
      self.calibration = Calibration(self.config['calibration'])
    else:
      exit_with_error(ErrorCode.MissingKey, 'calibration')

  def setup_cameras(self):
    """
    Defines the cameras from config
    """

    self.cameras = []
    if 'cameras' in self.config:
      if len(self.config['cameras']) < 1:
        exit_with_error(ErrorCode.EmptyKey, 'cameras')

      for index, camera in enumerate(self.config['cameras']):
        cam = Camera(camera, self.calibration)
        self.cameras.append(cam)
        self.config['cameras'][index]['initial_point'] = cam.initial_point.as_dict()
    else:
      exit_with_error(ErrorCode.MissingKey, 'cameras')

    for camera in self.cameras:
      if not camera.capture.isOpened():
        exit_with_error(ErrorCode.CameraConnect, camera.cam_id)

  def setup_room(self):
    """
    Defines the room from config
    """

    if 'room' in self.config:
      room_json = self.config['room']
      self.room = Room(room_json['x'], room_json['y'], room_json['z'])
    else:
      exit_with_error(ErrorCode.MissingKey, 'room')

  def setup_max_subjects(self):
    """
    Defines the maximum tracked subjects from config
    """

    if 'max_subjects' in self.config:
      self.max_subjects = self.config['max_subjects']
    else:
      exit_with_error(ErrorCode.MissingKey, 'max_subjects')

  def setup_fixtures(self):
    """
    Creates the fixture structure from config
    """

    self.universes = Universes()
    if 'fixtures' in self.config:
      if len(self.config['fixtures']) < 1:
        exit_with_error(ErrorCode.EmptyKey, 'fixtures')

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
      exit_with_error(ErrorCode.MissingKey, 'fixtures')

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

    print('distance:', euclid_distance)

    if euclid_distance > 1:
      close_enough = False
    else:
      ps = np.add(poi1.position.as_vector(), s)
      qt = np.add(poi2.position.as_vector(), t)
      abs_point = np.add(qt, ps) / 2
      if not(
          (0 <= abs_point[0] <= self.room.width) and
          (0 <= abs_point[1] <= self.room.height) and
          (0 <= abs_point[2] <= self.room.depth)
      ):
        close_enough = False
      else:
        points.append(abs_point)

    return (close_enough, points)

  def update_pois(self):
    """
    Update 3D points of interest from all camera pois
    """
    current_pois = self.combine_points()

    updated_pois = []

    # print('There are', len(current_pois), 'pois coming in')

    for incoming_poi in current_pois:
      new_position = incoming_poi.position
      made_update = False
      if len(self.pois) > 0:
        poi = sorted(self.pois, key=lambda p, np=new_position: p.diff_from_position(np))[0]
        diff_from_pos = poi.diff_from_position(new_position)
        if diff_from_pos < 0.50:
          # print('Updated position')
          poi.update_position(new_position)
          poi.increment_count()
          updated_pois.append(poi)
          made_update = True
          break

        if not made_update:
          poi = PointOfInterest(new_position, decrement_step=2)
          updated_pois.append(poi)
          self.pois.append(poi)
      else:
        poi = PointOfInterest(new_position, decrement_step=2)
        updated_pois.append(poi)
        self.pois.append(poi)


    missing_pois = set(self.pois) - set(updated_pois)
    for poi in missing_pois:
      poi.decrement_count()

    self.pois = [p for p in self.pois if p.count != 1]
    self.pois = sorted(self.pois, key=lambda p: p.weight, reverse=True)

  def combine_points(self):
    """
    Intersects all points from all cameras to find possible 3d world points of
    interest
    """

    fixture_positions = []
    for universe in self.universes.universes:
      for fixture in universe.fixtures:
        if fixture.last_position is not None:
          fixture_positions.append(fixture.last_position)

    threshold = 25

    pois = []
    for camera in self.cameras:
      fixture_camera_coordinates = []
      inverse_rotation = np.linalg.inv(camera.rotation_matrix)
      for fixt_pos in fixture_positions:
        displaced = (fixt_pos - camera.position).as_vector()

        # print('displaced:', displaced)

        # print('inverse_rotation:', inverse_rotation)

        identity = inverse_rotation[0].dot(displaced)
        identity = inverse_rotation[1].dot(identity)
        identity = inverse_rotation[2].dot(identity)

        # identity = identity

        print('identity:', identity)

        angular_displacement_horizontal = math.degrees(math.atan2(identity[2], identity[0]))
        angular_displacement_vertical = -math.degrees(math.atan2(identity[1], identity[0]))

        print('angular_displacement_horizontal:', angular_displacement_horizontal)
        print('angular_displacement_vertical:', angular_displacement_vertical)

        displacement_horizontal = round(
          scale(
            angular_displacement_horizontal,
            0, camera.angular_horiz_midpoint,
            0, camera.horiz_midpoint
          ) + camera.horiz_midpoint
        )
        displacement_vertical = round(
          scale(
            angular_displacement_vertical,
            0, camera.angular_vert_midpoint,
            0, camera.vert_midpoint
          ) + camera.vert_midpoint
        )

        print('predicted camera coordinates are', displacement_horizontal, displacement_vertical)

        fixture_camera_coordinates.append((displacement_horizontal, displacement_vertical))

        camera.current_background = np.zeros(camera.resolution_yx, dtype=np.uint8)

        camera_fixture_position = (displacement_vertical, displacement_horizontal)
        cv.circle(camera.current_background, camera_fixture_position, 15, 255, 2)

      possible_camera_pois = camera.points_of_interest
      camera_pois = []
      for poi in possible_camera_pois:
        collision = False
        for fixt_pos in fixture_camera_coordinates:
          lx, ly = poi.location
          fx, fy = fixt_pos

          if abs(lx - fx) < threshold and abs(ly - fy) < threshold:
            print('poi got too close')
            # collision = True

        if not collision:
          camera_pois.append(poi)





      pois.append(camera_pois)

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

  def start_artnet(self, transmit):
    """
    ArtNet transmission thread
    """

    last_poll_transmission = datetime.now()

    delay = 1
    if SystemConfig.transmit_rate == 'continuous':
      delay = 1/50
    elif SystemConfig.transmit_rate == 'reduced':
      delay = 1/15

    while 1:
      # Send ArtPoll every 3 seconds
      if (datetime.now() - last_poll_transmission).total_seconds() > 3:
        last_poll_transmission = datetime.now()
        packet = Poll()
        transmit.put(packet)

      for universe in self.universes.universes:
        packet = Dmx(0, universe)
        transmit.put(packet)
      time.sleep(delay)

  def start_artnet_reply(self, transmit):
    """

    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind((self.broadcast_address, 6454))

    while True:
      incoming = sock.recv(1024)

      if len(incoming) > 0:
        valid, opcode, packet = identify_header(incoming)
        if valid:
          if opcode is Opcode.OpPoll:
            packet = PollReply(0, 0, self.ip_address, [0x50, 0x1A, 0xC5, 0xE7, 0xD6, 0x8F])
            transmit.put(packet)

  def artnet_transmitter(self, transmit):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind((self.ip_address, 6454))
    print('Starting artnet')

    while True:
      packet = transmit.get()
      sock.sendto(packet.serialize(), (self.broadcast_address, 6454))

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

    daemon = False

    threading.Thread(target=start_ui, daemon=daemon).start()
    threading.Thread(target=self.start_websocket, daemon=daemon).start()

    for camera in self.cameras:
      threading.Thread(target=camera.begin_capture, daemon=daemon).start()

    transmit = queue.Queue()
    threading.Thread(target=self.start_artnet, args=(transmit,), daemon=daemon).start()
    threading.Thread(target=self.start_artnet_reply, args=(transmit,), daemon=daemon).start()
    threading.Thread(target=self.artnet_transmitter, args=(transmit,), daemon=daemon).start()

    for universe in self.universes.universes:
      for fixture in universe.fixtures:
        threading.Thread(target=fixture.follow, daemon=daemon).start()

    # coords = [
    #   (0, 0),
    #   (960, 0),
    #   (960, 720),
    #   (0, 720),
    #   (480, 360)
    # ]

    # for coord in coords:
    #   real_coord = self.cameras[0].calculate_real_world_coordinate(coord)
    #   print('1:', coord, 'is at', real_coord.x, real_coord.y, real_coord.z)

    #   real_coord = self.cameras[1].calculate_real_world_coordinate(coord)
    #   print('2:', coord, 'is at', real_coord.x, real_coord.y, real_coord.z)
    # exit()

    # last_poi = None

    while 1:

      # Uncomment this block for static values
      # point = Coordinate(2.0, 0.0, 4.0)
      # for fixture in self.universes.universes[0].fixtures:
      #   fixture.point_at(self.cameras[1].initial_point)
      #   fixture.open()
      #   # self.current_state['maps'][fixture.fixture_id] = id(live_pois[index])
      # time.sleep(1/30)
      # continue

      self.update_pois()

      # live_pois = [p for p in self.pois if p.weight > 2.5]
      live_pois = self.pois

      self.current_state['cameras'] = {}
      for camera in self.cameras:
        poi_positions = [poi.position.as_vector().tolist() for poi in camera.points_of_interest]
        self.current_state['cameras'][camera.cam_id] = poi_positions

      self.current_state['subjects'] = {}
      for poi in live_pois:
        self.current_state['subjects'][id(poi)] = poi.position.as_dict()

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


        # print('There are', len(live_pois), 'points of interest')

        # point = Coordinate(0.2, 1.7, 3.0)

      self.current_state['maps'] = dict()

      # fixture_count = len(self.universes.universes[0].fixtures)
      # poi_count = len(live_pois)
      # for index in range(min(poi_count, fixture_count)):
      #   fixture = self.universes.universes[0].fixtures[index]
      #   fixture.point_at(live_pois[index].position)
      #   # fixture.open()
      #   self.current_state['maps'][fixture.fixture_id] = id(live_pois[index])

      current_poi_index = -1
      for universe in self.universes.universes:
        for fixture in universe.fixtures:
          if len(live_pois) > 0:
            current_poi_index = (current_poi_index + 1) % self.max_subjects
            if current_poi_index >= len(live_pois): # We've got less than max subjects
              current_poi_index = 0
            fixture.point_at(live_pois[current_poi_index].position)
            fixture.open()

            self.current_state['maps'][fixture.fixture_id] = id(live_pois[current_poi_index])

          else:
            fixture.close()

      #   pos = live_pois[0].position
      #   for fixture in self.universes.universes[0].fixtures:
      #     fixture.point_at(pos)
      #     fixture.open()

      #     self.current_state['maps'][fixture.fixture_id] = id(live_pois[0])

      #     # time.sleep(1/30)
      # else:
      #   for fixture in self.universes.universes[0].fixtures:
      #     fixture.close()

      if len(self.cameras) >= 2:
        out_frame = None
        if self.cameras[0].current_frame is not None:
          out_frame = self.cameras[0].current_frame
        if self.cameras[1].current_frame is not None:
          if out_frame is not None:
            out_frame = np.vstack((out_frame, self.cameras[1].current_frame))
          else:
            out_frame = self.cameras[1].current_frame
        if out_frame is not None:
          cv.imshow('VIDEO', out_frame)
          cv.waitKey(1)
      time.sleep(1/30)
