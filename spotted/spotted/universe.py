"""
Holds single universe data and fixtures
"""

import numpy as np

from spotted.spotted.fixture import Fixture

class Universe:
  """
  Holds single universe data and fixtures
  """

  def __init__(self, net, subnet, universe):
    """
    Creates an instance of a universe

    Arguments:
      net {int} -- Universe net
      subnet {int} -- Universe subnet
      universe {int} -- Universe universe

    Returns:
      Universe -- Instance of universe, configured as supplied with a blank levels and fixtures list
    """

    self.net = net
    self.subnet = subnet
    self.universe = universe
    self.sub_universe = universe + (subnet << 4)
    self.levels = np.zeros(512, dtype=np.uint8)
    self.occupied_channels = np.zeros(512, dtype=bool)
    self.fixtures = []

  def add_fixture(self, fixture):
    """
    Adds a fixture to the universe list, checking for overlaps

    Arguments:
      fixture {Fixture} -- Fixture to add

    Returns:
      True -- If the fixture was added
      'Supplied fixture is not an instance of Fixture'
      'Supplied fixture clashes with an existing fixture'
    """

    if not isinstance(fixture, Fixture):
      return False, 'Supplied fixture is not an instance of Fixture'

    overlap = False
    for channel in range(fixture.address['address'], fixture.personality.channels):
      if self.occupied_channels[channel - 1]:
        overlap = True

    if overlap:
      return False, 'Supplied fixture clashes with an existing fixture'

    self.fixtures.append(fixture)
    for channel in range(fixture.address['address'], fixture.personality.channels):
      self.occupied_channels[channel - 1] = True

    return True, ''

  def get_levels(self):
    """
    Collect the DMX universe data for all fixtures in this universe

    Returns:
      512 length uint8 array with applicable values set for fixture states
    """

    for fixture in self.fixtures:
      start_addr = fixture.address['address'] - 1
      for index, level in enumerate(fixture.levels):
        self.levels[start_addr + index] = level
    return self.levels
