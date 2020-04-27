"""
Art-Net ArtPoll packet
"""

from artnet.helpers import get_bit
from artnet.header import Header
from artnet.diag_code import DiagCode
from artnet.opcode import Opcode

class Poll:
  """
  Art-Net ArtPoll packet
  """

  # pylint: disable=too-many-arguments
  def __init__(
      self,
      vlc_disable=True,
      diag_transmission=False,
      diag_enable=False,
      reply_on_change=False,
      diag_priority=DiagCode.DpLow
  ):
    """
    Creates a packet

    Arguments:
      vlc_disable {bool} -- False: transmits VLC
      diag_transmission {bool} -- False: diagnostics are broadcast, True: diagnostics are unicast
      diag_enable {bool} -- False: do not request diags, True: request diags
      diag_priority {DiagCode} -- Lowest priority diagnostic message that should be sent
    """

    self.header = Header(Opcode.OpPoll)
    self.vlc_disable = vlc_disable
    self.diag_transmission = diag_transmission
    self.diag_enable = diag_enable
    self.reply_on_change = reply_on_change
    self.diag_priority = diag_priority.value

  def serialize(self):
    """
    Serializes a packet into a byte array, ready for transmission

    Returns:
      byte array -- The packet packed in order for transmission
    """

    talk_to_me = 0

    # This utilises Python's implicit bool to int
    talk_to_me |= (self.vlc_disable << 4)
    talk_to_me |= (self.diag_transmission << 3)
    talk_to_me |= (self.diag_enable << 2)
    talk_to_me |= (self.reply_on_change << 1)

    output = self.header.serialize()
    output.append(talk_to_me)
    output.append(self.diag_priority)
    return output

  @staticmethod
  def deserialize(incoming):
    """
    Deserializes a received packet into the original sent packet

    Arguments:
      incoming {bytearray} -- Incoming packet

    Returns:
      Poll
    """

    talk_to_me = incoming[0]

    vlc_disable = get_bit(talk_to_me, 4)
    diag_transmission = get_bit(talk_to_me, 3)
    diag_enable = get_bit(talk_to_me, 2)
    reply_on_change = get_bit(talk_to_me, 1)
    diag_priority = DiagCode(incoming[1])

    return Poll(vlc_disable, diag_transmission, diag_enable, reply_on_change, diag_priority)
