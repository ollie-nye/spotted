from spotted.artnet.opcode import Opcode


def test_OpPoll():
  assert Opcode.OpPoll.value == 0x2000

def test_OpPollReply():
  assert Opcode.OpPollReply.value == 0x2100

def test_OpDiagData():
  assert Opcode.OpDiagData.value == 0x2300

def test_OpCommand():
  assert Opcode.OpCommand.value == 0x2400

def test_OpDmx():
  assert Opcode.OpDmx.value == 0x5000

def test_OpOutput():
  assert Opcode.OpOutput.value == 0x5000

def test_OpNzs():
  assert Opcode.OpNzs.value == 0x5100

def test_OpSync():
  assert Opcode.OpSync.value == 0x5200

def test_OpAddress():
  assert Opcode.OpAddress.value == 0x6000

def test_OpInput():
  assert Opcode.OpInput.value == 0x7000

def test_OpTodRequest():
  assert Opcode.OpTodRequest.value == 0x8000

def test_OpTodData():
  assert Opcode.OpTodData.value == 0x8100

def test_OpTodControl():
  assert Opcode.OpTodControl.value == 0x8200

def test_OpRdm():
  assert Opcode.OpRdm.value == 0x8300

def test_OpRdmSub():
  assert Opcode.OpRdmSub.value == 0x8400

def test_OpVideoSetup():
  assert Opcode.OpVideoSetup.value == 0xa010

def test_OpVideoPalette():
  assert Opcode.OpVideoPalette.value == 0xa020

def test_OpVideoData():
  assert Opcode.OpVideoData.value == 0xa040

def test_OpMacMaster():
  assert Opcode.OpMacMaster.value == 0xf000

def test_OpMacSlave():
  assert Opcode.OpMacSlave.value == 0xf100

def test_OpFirmwareMaster():
  assert Opcode.OpFirmwareMaster.value == 0xf200

def test_OpFirmwareReply():
  assert Opcode.OpFirmwareReply.value == 0xf300

def test_OpFileTnMaster():
  assert Opcode.OpFileTnMaster.value == 0xf400

def test_OpFileFnMaster():
  assert Opcode.OpFileFnMaster.value == 0xf500

def test_OpFileFnReply():
  assert Opcode.OpFileFnReply.value == 0xf600

def test_OpIpProg():
  assert Opcode.OpIpProg.value == 0xf800

def test_OpIpProgReply():
  assert Opcode.OpIpProgReply.value == 0xf900

def test_OpMedia():
  assert Opcode.OpMedia.value == 0x9000

def test_OpMediaPatch():
  assert Opcode.OpMediaPatch.value == 0x9100

def test_OpMediaControl():
  assert Opcode.OpMediaControl.value == 0x9200

def test_OpMediaContrlReply():
  assert Opcode.OpMediaContrlReply.value == 0x9300

def test_OpTimeCode():
  assert Opcode.OpTimeCode.value == 0x9700

def test_OpTimeSync():
  assert Opcode.OpTimeSync.value == 0x9800

def test_OpTrigger():
  assert Opcode.OpTrigger.value == 0x9900

def test_OpDirectory():
  assert Opcode.OpDirectory.value == 0x9a00

def test_OpDirectoryReply():
  assert Opcode.OpDirectoryReply.value == 0x9b00
