"""
ArtNet Header
"""

class Header:
  """
  ArtNet Header
  """

  def __init__(self, opcode):
    """
    Creates a Header with the given opcode

    Arguments:
      opcode {Opcode} -- Opcode to send in header

    Returns:
      Header -- Instance of header
    """

    self.packet_id = 'Art-Net\0'
    self.opcode = opcode.value
    self.protocol_version = 0x000e

  def serialize(self):
    """
    Serializes the Header into a correctly spaced byte array

    Returns:
      bytearray -- Header packed into byte array
    """

    output = bytearray(self.packet_id, 'ascii')
    output.extend(self.opcode.to_bytes(2, 'little'))
    output.extend(self.protocol_version.to_bytes(2, 'big'))
    return output
