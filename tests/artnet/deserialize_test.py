from artnet.deserialize import identify_header
from artnet.header import Header
from artnet.opcode import Opcode
from artnet.poll import Poll
from artnet.poll_reply import PollReply

def test_artnet_poll():
  packet = Poll()

  status, opcode, verify_packet = identify_header(packet.serialize())

  assert status is True
  assert opcode is Opcode.OpPoll
  assert packet.vlc_disable == verify_packet.vlc_disable
  assert packet.diag_enable == verify_packet.diag_enable
  assert packet.diag_priority == verify_packet.diag_priority
  assert packet.reply_on_change == verify_packet.reply_on_change

def test_artnet_poll_reply():
  packet = PollReply(0, 0, '10.0.0.1', [0x50, 0x1A, 0xC5, 0xE7, 0xD6, 0x8F])

  status, opcode, verify_packet = identify_header(packet.serialize())

  assert status is True
  assert opcode is Opcode.OpPollReply
  assert verify_packet is None

def test_unknown_artnet_packet(capsys):
  packet = bytearray('Art-Net\0', 'ascii')
  packet.extend([0xff, 0xff, 0x00, 0x00])
  status, opcode, verify_packet = identify_header(packet)
  captured = capsys.readouterr()

  assert captured.out == 'Unknown Art-Net packet received. Opcode 65535\n'
  assert status is False
  assert opcode == 0xffff
  assert verify_packet is None

def test_unknown_packet():
  packet = bytearray('not_an_artnet_packet', 'ascii')

  status, opcode, verify_packet = identify_header(packet)

  assert status is False
  assert opcode == 0
  assert verify_packet is None
