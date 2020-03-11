from artnet.header import Header

opcode = 0x0123
init_header = Header(opcode)

def test_correct_id():
  assert init_header.packet_id == 'Art-Net\0'

def test_correct_opcode():
  assert init_header.opcode == opcode

def test_correct_protocol_version():
  assert init_header.protocol_version == 0x000e

def test_serialize():
  output = init_header.serialize()
  expected_output = bytearray(b'Art-Net\x00\x23\x01\x00\x0e')
  assert output == expected_output
