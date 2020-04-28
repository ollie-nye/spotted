"""
ArtNet DMX packet
"""

from spotted.artnet.header import Header
from spotted.artnet.opcode import Opcode

class Dmx:
  """
  ArtNet DMX packet
  """

  def __init__(self, sequence, universe):
    """
    Creates a packet

    Arguments:
      sequence {int8} -- Packet sequence, to define order on receiving node
      universe {Universe} -- Universe object to define address parameters
      data {array of int8} -- Data to send to universe output

    Returns:
      Dmx -- Created packet structure, ready for serializing
    """

    self.header = Header(Opcode.OpDmx)
    self.sequence = sequence
    self.physical = 0x00
    self.sub_universe = universe.sub_universe
    self.net = universe.net
    self.length = 0x0200
    self.data = universe.get_levels()

  def serialize(self):
    """
    Serializes a packet into a byte array, ready for transmission

    Returns:
      byte array -- The packet packed in order for transmission
    """

    output = self.header.serialize()
    output.append(self.sequence)
    output.append(self.physical)
    output.append(self.sub_universe)
    output.append(self.net)
    output.extend(self.length.to_bytes(2, 'big'))
    output.extend(self.data)
    return output
