"""
Spotted Fixture
"""

import math
import numpy as np

from spotted.personality import find_personality_by_id
from spotted.coordinate import Coordinate
from spotted.spherical_coordinate import SphericalCoordinate
from spotted.helpers import scale, create_rotation_matrix

class Fixture:
  """
  Spotted Fixture
  """

  # pylint: disable=invalid-name, too-many-instance-attributes
  def __init__(self, config):
    """
    Create fixture from given config

    Returns:
      Fixture
    """

    self.fixture_id = config['id']
    self.personality = find_personality_by_id(config['personality'], config['mode'])
    self.address = {
      'net': config['net'],
      'subnet': config['subnet'],
      'universe': config['universe'],
      'address': config['address']
    }

    self.levels = np.zeros(self.personality.channels)

    for attribute in self.personality.attributes:
      channel = attribute.offset
      self.levels[channel] = attribute.default

    pos = config['position']
    self.location = Coordinate(pos['x'], pos['y'], pos['z'])
    self.position = Coordinate(0, 0, 0)

    self.pan_offset = 0
    self.tilt_invert = False

    self.rotation_matrix = create_rotation_matrix(
      config['rotation']['x'], config['rotation']['y'], config['rotation']['z']
    )

  def pan(self, value):
    """
    Set pan of fixture

    Arguments:
      value {uint8} -- DMX value of pan channel
    """

    pan_attribute = self.personality.get_attribute('pan')
    channel = pan_attribute.offset
    self.levels[channel] = value

  def tilt(self, value):
    """
    Set tilt of fixture

    Arguments:
      value {uint8} -- DMX value of tilt channel
    """

    tilt_attribute = self.personality.get_attribute('tilt')
    channel = tilt_attribute.offset
    self.levels[channel] = value

  def open(self):
    """
    Light fixture
    """

    dimmer = self.personality.get_attribute('dimmer')
    max_val = dimmer.range
    self.levels[dimmer.offset] += 1

    if self.levels[dimmer.offset] > max_val:
      self.levels[dimmer.offset] = max_val

  def close(self):
    """
    Blackout fixture
    """

    dimmer = self.personality.get_attribute('dimmer')
    # self.levels[dimmer.offset] -= 2
    self.levels[dimmer.offset] = 0

    # if self.levels[dimmer.offset] < 0:
    #   self.levels[dimmer.offset] = 0

  def point_at(self, position):
    """
    Point at a position

    Arguments:
      position {Coordinate} -- Position to point at, real world
    """

    print('Pointing at', position.x, position.y, position.z)

    pos_from_fixture = position.diff(self.location).as_vector()
    pos_from_fixture[1] = -pos_from_fixture[1]

    coordinate = SphericalCoordinate.from_cartesian(*pos_from_fixture)

    pan_range = math.radians(self.personality.get_attribute('pan').range)
    pan_angle = scale(coordinate.azimuth + math.radians(180), 0, pan_range, 0, 255)

    tilt_range = math.radians(self.personality.get_attribute('tilt').range)
    tilt_extension = (tilt_range - math.pi) / 2
    tilt_angle = scale(coordinate.elevation + tilt_extension, 0, tilt_range, 255, 0)

    self.pan(pan_angle)
    self.tilt(tilt_angle)

  def calibrate(self, room):
    """
    Aligns a fixtures' 0deg point to be away from the center of the room
    Sets instance attributes pan_offset and tilt_invert

    Arguments:
      room {Room} -- Room to align to
    """

    # offset_angle = self.location.pan_angle(room.center())
    # if offset_angle >= 180.0:
    #   self.pan_offset = offset_angle - 180.0
    #   self.tilt_invert = True
    # else:
    #   self.pan_offset = offset_angle
