from spotted.artnet.dmx import Dmx
from spotted.spotted.universe import Universe
import numpy as np

universe = Universe(0x12, 0x3, 0x4)

data = np.zeros(512, dtype=np.uint8)
init_packet = Dmx(0x00, universe)

def test_correct_header():
  assert init_packet.header.opcode == 0x5000

def test_correct_sequence():
  assert init_packet.sequence == 0x00

def test_correct_physical():
  assert init_packet.physical == 0x00

def test_correct_universe():
  assert init_packet.sub_universe == universe.sub_universe

def test_correct_net():
  assert init_packet.net == universe.net

def test_correct_length():
  assert init_packet.length == 0x0200

def test_correct_payload():
  assert all([a == b for a, b in zip(init_packet.data, data)])

def test_serialize():
  output = init_packet.header.serialize()
  output.append(0x00)
  output.append(0x00)
  output.append(0x34)
  output.append(0x12)
  output.append(0x02)
  output.append(0x00)
  output.extend(data)

  assert all([a == b for a, b in zip(init_packet.serialize(), output)])



# output = self.header.serialize()
#     output.append(self.sequence)
#     output.append(self.physical)
#     output.append(self.sub_universe)
#     output.append(self.net)
#     output.extend(self.length.to_bytes(2, 'big'))
#     output.extend(self.data)
#     return output
