import numpy as np
import threading

class SpottedUniverse:
  def __init__(self, net, subnet, universe):
    self.net = net
    self.subnet = subnet
    self.universe = universe
    self.levels = np.zeros(512, dtype=np.uint8)
    self.fixtures = []

    # race condition?

  def add_fixture(self, fixture):
    self.fixtures.append(fixture)

  def get_levels(self):
    for fixture in self.fixtures:
      start_addr = fixture.address - 1
      for index, level in enumerate(fixture.levels):
        self.levels[start_addr + index] = level
    return self.levels