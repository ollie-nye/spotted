"""
ArtPoll diagnostics codes
"""

from enum import Enum

class DiagCode(Enum):
  """
  ArtPoll diagnostics codes
  """

  DpDisabled = 0x00
  DpLow = 0x10
  DpMed = 0x40
  DpHigh = 0x80
  DpCritical = 0xe0
  DpVolatile = 0xf0
