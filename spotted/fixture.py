import numpy as np

from spotted.personality import personalities
from spotted.coordinate import Coordinate

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

  def pan(self, value):
    pan_attribute = self.personality.get_attribute('pan')
    channel = pan_attribute.offset

    if value < self.pan_offset:
      value += 360.0

    channel_value = pan_angle_to_dmx(value)

    if pan_attribute.invert:
      channel_value = 255 - channel_value

    self.levels[channel] = channel_value

  def tilt(self, value):
    tilt_attribute = self.personality.get_attribute('tilt')
    channel = tilt_attribute.offset

    channel_value = tilt_angle_to_dmx(tilt_attribute.range, value)
    if tilt_attribute.invert:
      channel_value = 255 - channel_value
    if self.tilt_invert:
      channel_value = 255 - channel_value

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
    pan_angle = self.location.pan_angle(position) + 180
    tilt_angle = self.location.tilt_angle(position)

    self.pan(pan_angle)
    self.tilt(tilt_angle)

  def calibrate(self, room):
    offset_angle = self.location.pan_angle(room.center())
    if offset_angle >= 180.0:
      self.pan_offset = offset_angle - 180.0
      self.tilt_invert = True
    else:
      self.pan_offset = offset_angle
