from artnet.diag_code import DiagCode

def test_disabled():
  assert DiagCode.DpDisabled.value == 0x00

def test_low():
  assert DiagCode.DpLow.value == 0x10

def test_med():
  assert DiagCode.DpMed.value == 0x40

def test_high():
  assert DiagCode.DpHigh.value == 0x80

def test_critical():
  assert DiagCode.DpCritical.value == 0xe0

def test_volatile():
  assert DiagCode.DpVolatile.value == 0xf0
