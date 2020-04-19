"""
ArtPoll/ArtPollReply node report codes
"""

from enum import Enum

class NodeReport(Enum):
  """
  ArtPoll/ArtPollReply node report codes
  """

  RcDebug = 0x0000
  RcPowerOk = 0x0001
  RcPowerFail = 0x0002
  RcSocketWr1 = 0x0003
  RcParseFail = 0x0004
  RcUdpFail = 0x0005
  RcShNameOk = 0x0006
  RcLoNameOk = 0x0007
  RcDmxError = 0x0008
  RcDmxUdpFull = 0x0009
  RcDmxRxFull = 0x000a
  RcSwitchErr = 0x000b
  RcConfigErr = 0x000c
  RcDmxShort = 0x000d
  RcFirmwareFail = 0x000e
  RcUserFail = 0x000f
  RcFactoryRes = 0x0010
