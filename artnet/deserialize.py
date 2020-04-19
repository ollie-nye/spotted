"""

"""

from artnet.opcode import Opcode
from artnet.poll import Poll
from artnet.poll_reply import PollReply

def identify_header(incoming):
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
