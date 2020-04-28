from spotted.artnet.header import Header
from spotted.artnet.opcode import Opcode

opcode = Opcode.OpPoll
init_header = Header(opcode)

def test_correct_id():
  assert init_header.packet_id == 'Art-Net\0'

def test_correct_opcode():
  assert init_header.opcode == opcode.value

def test_correct_protocol_version():
  assert init_header.protocol_version == 0x000e

def test_serialize():
  output = init_header.serialize()
  expected_output = bytearray(b'Art-Net\x00\x00\x20\x00\x0e')
  assert output == expected_output
