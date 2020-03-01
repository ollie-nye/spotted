import threading

class SpottedUniverses:
  def __init__(self):
    self.universes = []
    self._lock = threading.Lock()

    # race condition?

  def add_universe(self, universe):
    self.universes.append(universe)

  def get_universe(self, net, subnet, universe):
    for universe in self.universes:
      if universe.net == net:
        if universe.subnet == subnet:
          if universe.universe == universe:
            return universe
    return None
