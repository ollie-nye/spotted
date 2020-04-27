"""
Deserialize Art-Net packets into their original structures
"""

from artnet.opcode import Opcode
from artnet.poll import Poll

def identify_header(incoming):
  """
  Deserialize Art-Net packets into their original structures

  Arguments:
    incoming {bytearray} -- incoming packet

  Returns:
    {(status, opcode, packet)} -- status is True if packet was an Art-Net packet
                                  opcode contains the opcode enum for the packet
                                  packet contains the deserialized packet class
  """

  opcode = 0
  packet = None

  if incoming[0:8].decode('ascii') == 'Art-Net\0': # This is an art-net packet
    opcode = incoming[8] + (incoming[9] << 8)
    try:
      opcode = Opcode(opcode)
      packet_data = incoming[12:]
      if opcode is Opcode.OpPoll:
        packet = Poll.deserialize(packet_data)
      elif opcode is Opcode.OpPollReply:
        #TODO: deserialize ArtPollReply
        return True, opcode, None
      return True, opcode, packet
    except ValueError:
      print('Unknown Art-Net packet received. Opcode', opcode)
  return False, opcode, None
