"""
Generic Art-Net helpers
"""

def get_bit(value, position):
  """
  Returns the single bit at the given position in the bytearray

  Arguments:
    value {bytearray} -- value to extract bit from
    position {int} -- position of bit to extract, 0 index

  Returns:
    {bool} -- bit at position
  """

  return (value & (1 << position)) >> position
