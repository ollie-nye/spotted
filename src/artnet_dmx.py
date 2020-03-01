from artnet_header import ArtnetHeader

class ArtnetDmx:
  def __init__(self, data):
    self.header = ArtnetHeader(0x0050)
    self.sequence = 0x01
    self.physical = 0x00
    self.sub_universe = 0x00
    self.net = 0x00
    self.length = 0x0200
    self.data = data

  def serialize(self):
    output = self.header.serialize()
    output.append(self.sequence)
    output.append(self.physical)
    output.append(self.sub_universe)
    output.append(self.net)
    output.extend(self.length.to_bytes(2, 'big'))
    output.extend(self.data)
    return output
