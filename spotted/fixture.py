import numpy as np
import math

from spotted.personality import personalities
from spotted.coordinate import Coordinate
from spotted.spherical_coordinate import SphericalCoordinate

def find_personality_by_id(id):
  for personality in personalities:
    if personality.id == id:
      return personality
  return None

def pan_angle_to_dmx(angle):
  return ((angle * 255.0) / 540.0)

def tilt_angle_to_dmx(range, angle):
  return (((angle + ((range - 180.0) / 2.0)) * 255.0) / range)

class Fixture:
  def __init__(self, json):
    self.fixture_id = json['id']
    self.personality = find_personality_by_id(json['personality'])
    self.net = json['net']
    self.subnet = json['subnet']
    self.universe = json['universe']
    self.address = json['address']
    self.levels = np.zeros(self.personality.channels)

    for attribute in self.personality.attributes:
      channel = attribute.offset
      self.levels[channel] = attribute.default

    pos = json['position']
    self.location = Coordinate(pos['x'], pos['y'], pos['z'])
    self.position = Coordinate(0, 0, 0)

    self.pan_offset = 0
    self.tilt_invert = False

    a = math.radians(0)
    b = math.radians(0)
    c = math.radians(90)

    self.rotation_matrix = np.array([
      [math.cos(a) * math.cos(b), (math.cos(a) * math.sin(b) * math.sin(c)) - (math.sin(a) * math.cos(c)), (math.cos(a) * math.sin(b) * math.cos(c)) + (math.sin(a) * math.sin(c))],
      [math.sin(a) * math.cos(b), (math.sin(a) * math.sin(b) * math.sin(c)) + (math.cos(a) * math.cos(c)), (math.sin(a) * math.sin(b) * math.cos(c)) - (math.cos(a) * math.sin(c))],
      [-math.sin(b), math.cos(b) * math.sin(c), math.cos(b) * math.cos(c)]
    ])

  def pan(self, value):
    pan_attribute = self.personality.get_attribute('pan')
    channel = pan_attribute.offset

    # print('Pan offset:', self.pan_offset)

    # if value < self.pan_offset:
    #  value += 360.0

    # channel_value = pan_angle_to_dmx(540, value)
    channel_value = value
    # if pan_attribute.invert:
    #   channel_value = 255 - channel_value

    self.levels[channel] = channel_value
    
  def tilt(self, value):
    tilt_attribute = self.personality.get_attribute('tilt')
    channel = tilt_attribute.offset

    # channel_value = tilt_angle_to_dmx(tilt_attribute.range, value)
    channel_value = value
    # if tilt_attribute.invert:
    #   channel_value = 255 - channel_value
    # if self.tilt_invert:
    #   channel_value = 255 - channel_value

    self.levels[channel] = channel_value

  def open(self):
    dimmer = self.personality.get_attribute('dimmer')
    self.levels[dimmer.offset] = dimmer.default

  def close(self):
    dimmer = self.personality.get_attribute('dimmer')
    self.levels[dimmer.offset] = 0

  def point_at(self, position):
    # TODO: Why 180?
    # print('Pointing at', position.x, position.y, position.z)

    pos_from_fixture = position.diff(self.location).as_vector()
    print('pos_from_fixture:', pos_from_fixture)

    rotated = rotation_matrix.dot(pos_from_fixture)
    print('rotated:', rotated)

    coordinate = SpottedSphericalCoordinate.from_cartesian(*rotated)

    print('azimuth:', coordinate.azimuth, 'elevation:', coordinate.elevation, 'inclination:', coordinate.inclination)

    pan_range = math.radians(self.personality.get_attribute('pan').range)
    pan_angle = scale(coordinate.azimuth, -(pan_range / 2), (pan_range / 2), 0, 255)

    tilt_range = math.radians(self.personality.get_attribute('tilt').range)
    tilt_angle = scale(coordinate.inclination, -(tilt_range / 2), (tilt_range / 2), 0, 255)

    # print(coordinate.r, coordinate.a, coordinate.i)

    # pan_angle = self.location.pan_angle(position)
    # tilt_angle = self.location.tilt_angle(position)

    print('Pan:', pan_angle, '. Tilt:', tilt_angle)

    self.pan(pan_angle)
    self.tilt(tilt_angle)

  def calibrate(self, room):
    offset_angle = self.location.pan_angle(room.center())
    if offset_angle >= 180.0:
      self.pan_offset = offset_angle - 180.0
      self.tilt_invert = True
    else:
      self.pan_offset = offset_angle
