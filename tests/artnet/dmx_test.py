from artnet.dmx import Dmx
from spotted.universe import Universe

universe = Universe(0x12, 0x3, 0x4)

data = []
for i in range(512):
  data.append(i % 255)
init_packet = Dmx(0x00, universe, data)

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
  assert init_packet.data == data
