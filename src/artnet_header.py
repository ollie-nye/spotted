class ArtnetHeader:
  def __init__(self, opcode):
    self.id = 'Art-Net\0'
    self.opcode = opcode
    self.protocol_version = 0x000e

  def serialize(self):
    output = bytearray(self.id, 'ascii')
    output.extend(self.opcode.to_bytes(2, 'big'))
    output.extend(self.protocol_version.to_bytes(2, 'big'))
    return output
