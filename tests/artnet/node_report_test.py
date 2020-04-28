from spotted.artnet.node_report import NodeReport

def test_RcDebug():
  assert NodeReport.RcDebug.value == 0x0000

def test_RcPowerOk():
  assert NodeReport.RcPowerOk.value == 0x0001

def test_RcPowerFail():
  assert NodeReport.RcPowerFail.value == 0x0002

def test_RcSocketWr1():
  assert NodeReport.RcSocketWr1.value == 0x0003

def test_RcParseFail():
  assert NodeReport.RcParseFail.value == 0x0004

def test_RcUdpFail():
  assert NodeReport.RcUdpFail.value == 0x0005

def test_RcShNameOk():
  assert NodeReport.RcShNameOk.value == 0x0006

def test_RcLoNameOk():
  assert NodeReport.RcLoNameOk.value == 0x0007

def test_RcDmxError():
  assert NodeReport.RcDmxError.value == 0x0008

def test_RcDmxUdpFull():
  assert NodeReport.RcDmxUdpFull.value == 0x0009

def test_RcDmxRxFull():
  assert NodeReport.RcDmxRxFull.value == 0x000a

def test_RcSwitchErr():
  assert NodeReport.RcSwitchErr.value == 0x000b

def test_RcConfigErr():
  assert NodeReport.RcConfigErr.value == 0x000c

def test_RcDmxShort():
  assert NodeReport.RcDmxShort.value == 0x000d

def test_RcFirmwareFail():
  assert NodeReport.RcFirmwareFail.value == 0x000e

def test_RcUserFail():
  assert NodeReport.RcUserFail.value == 0x000f

def test_RcFactoryRes():
  assert NodeReport.RcFactoryRes.value == 0x0010
