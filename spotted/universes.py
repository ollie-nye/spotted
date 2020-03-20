"""
Collection of universes to transmit data for
"""

import threading

from spotted.universe import Universe

class Universes:
  """
  Collection of universes to transmit data for
  """

  def __init__(self):
    self.universes = []
    self._lock = threading.Lock()

  def add_universe(self, universe):
    """
    Adds a universe to the collection

    Arguments:
      universe {Universe} -- The universe to add

    Raises:
      'Supplied universe is not an instance of Universe'
    """
    if isinstance(universe, Universe):
      self.universes.append(universe)
      return True
    return False, 'Supplied universe is not an instance of Universe'

  def get_universe(self, uni_net, uni_subnet, uni_universe):
    """
    Gets a universe by address properties

    Arguments:
      net {int} -- Universe net
      subnet {int} -- Universe subnet
      universe {int} -- Universe universe

    Returns:
      Universe -- if a universe is found with all three properties matching
      None -- if no such universe is found
    """

    for universe in self.universes:
      if universe.net == uni_net:
        if universe.subnet == uni_subnet:
          if universe.universe == uni_universe:
            return universe
    return None
