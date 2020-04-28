"""
Spotted Fixture
"""

import math
import time
import numpy as np

from spotted.spotted.personality import find_personality_by_id
from spotted.spotted.coordinate import Coordinate
from spotted.spotted.spherical_coordinate import SphericalCoordinate
from spotted.spotted.helpers import scale, create_rotation_matrix

class Fixture:
  """
  Spotted Fixture
  """

  # pylint: disable=invalid-name, too-many-instance-attributes
  def __init__(self, config, fixture_id, stop_flags):
    """
    Create fixture from given config

    Returns:
      Fixture
    """

    self.stop_flags = stop_flags
    self.fixture_id = fixture_id
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
      if attribute.multiplier_type == 'wide':
        self.levels[channel] = attribute.default # Course channel
        self.levels[channel + 1] = attribute.default # Fine channel
      else:
        self.levels[channel] = attribute.default

    pos = config['position']
    self.location = Coordinate(pos['x'], pos['y'], pos['z'])
    self.position = Coordinate(0, 0, 0)

    self.last_position = None
    self.current_aim = None
    self.position_step = None
    self.steps_taken = 0

    self.pan_offset = math.radians(config['rotation']['y'])
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

    if pan_attribute.multiplier_type == 'wide':
      self.levels[channel] = value // 255 # Course channel
      self.levels[channel + 1] = value % 255 # Fine channel
    else:
      self.levels[channel] = value // 255

  def tilt(self, value):
    """
    Set tilt of fixture

    Arguments:
      value {uint8} -- DMX value of tilt channel
    """

    tilt_attribute = self.personality.get_attribute('tilt')
    channel = tilt_attribute.offset

    if tilt_attribute.multiplier_type == 'wide':
      self.levels[channel] = value // 255 # Course channel
      self.levels[channel + 1] = value % 255 # Fine channel
    else:
      self.levels[channel] = value // 255

  def open(self):
    """
    Strike fixture
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
    self.levels[dimmer.offset] -= 4
    # self.levels[dimmer.offset] = 0

    if self.levels[dimmer.offset] < 0:
      self.levels[dimmer.offset] = 0

  def point_at(self, position):
    """
    Point at a position

    Arguments:
      position {Coordinate} -- Position to point at, real world
    """

    if self.current_aim is None:
      self.last_position = position

    self.current_aim = position
    self.position_step = (self.current_aim - self.last_position) / 10
    self.steps_taken = 0

  def follow(self):
    """
    Infinite loop that decelerates towards a configured point
    """

    while True:
      if self.stop_flags['fixture']:
        break

      time.sleep(1/50)

      if self.current_aim is None:
        continue

      if self.steps_taken >= 10:
        continue

      new_step = self.last_position + self.position_step
      self.last_position = new_step
      self.steps_taken += 1

      pos_from_fixture = (new_step - self.location).as_vector()
      pos_from_fixture[1] = -pos_from_fixture[1]

      coordinate = SphericalCoordinate.from_cartesian(*pos_from_fixture)

      pan_range = math.radians(self.personality.get_attribute('pan').range)

      pan_val = coordinate.azimuth + self.pan_offset

      pan_angle = scale(pan_val, 0, pan_range, 0, 65025)

      tilt_range = math.radians(self.personality.get_attribute('tilt').range)
      tilt_extension = (tilt_range - math.pi) / 2

      if pan_val < 0: # pan is inverted, invert tilt to match
        tilt_val = -(coordinate.elevation + tilt_extension)
      else:
        tilt_val = coordinate.elevation + tilt_extension

      tilt_angle = scale(tilt_val, 0, tilt_range, 65025, 0)

      self.pan(pan_angle)
      self.tilt(tilt_angle)
