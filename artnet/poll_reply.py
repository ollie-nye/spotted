"""
Art-Net ArtPollReply packet
"""

from enum import Enum

from config.system import SystemConfig

from artnet.diag_code import DiagCode
from artnet.style_code import StyleCode
from artnet.opcode import Opcode

class PortProtocol(Enum):
  DMX = 0b000000
  MIDI = 0b000001
  Avab = 0b000010
  ColortranCMX = 0b000011
  ADB625 = 0b000100
  ArtNet = 0b00101

def port_type(can_output=False, can_input=False, protocol=PortProtocol.DMX):
  value = 0
  value |= (can_output << 7)
  value |= (can_input << 6)
  value |= protocol
  return value

def input_status(
    data_received=True,
    dmx_test=False,
    dmx_sip=False,
    dmx_text=False,
    disabled=False,
    receive_errors=False
):
  value = 0
  value |= data_received << 7
  value |= dmx_test << 6
  value |= dmx_sip << 5
  value |= dmx_text << 4
  value |= disabled << 3
  value |= receive_errors << 2
  return value

def output_status(
    data_transmitted=True,
    dmx_test=False,
    dmx_sip=False,
    dmx_text=False,
    merging=False,
    output_short=False,
    merge_ltp=False,
    output_sacn=False
):
  value = 0
  value |= data_transmitted << 7
  value |= dmx_test << 6
  value |= dmx_sip << 5
  value |= dmx_text << 4
  value |= merging << 3
  value |= output_short << 2
  value |= merge_ltp << 1
  value |= output_sacn
  return value

class PollReply:
  """
  Art-Net ArtPollReply packet
  """

  def __init__(
      self,
      net_switch,
      sub_switch,
      ip_address, # and bind_ip
      mac_address,
      port_types=[0, 0, 0, 0],
      good_input=[0, 0, 0, 0],
      good_output=[0, 0, 0, 0],
      version_info=0x0000,
      status_indicator=0b11,
      status_address_authority=0b01,
      status_boot_mode=0b0,
      status_rdm=0b0,
      status_ubea=0b0,
      short_name="SpottedController\0",
      long_name="Spotted Controller                                             \0",
      style=StyleCode.StController,
      status_squawking=False,
      status_artnet_sacn_switch=False,
      status_artnet34=True,
      status_dhcp_capable=True,
      status_dhcp_configured=False,
      status_web_browser=True,
      bind_index=1
  ):
    """
    Creates a packet

    Arguments:
      vlc_disable {bool} -- False: transmits VLC
      diag_transmission {bool} -- False: diagnostics are broadcast, True: diagnostics are unicast
      diag_enable {bool} -- False: do not request diags, True: request diags
      diag_priority {DiagCode} -- Lowest priority diagnostic message that should be sent
    """

    self.packet_id = 'Art-Net\0'
    self.opcode = Opcode.OpPollReply.value
    self.ip_address = [int(octet) for octet in ip_address.split('.')]
    self.port = 0x1936
    self.version_info = version_info
    self.net_switch = net_switch
    self.sub_switch = sub_switch
    self.oem = SystemConfig.oem_code
    self.ubea_version = 0

    self.status1 = 0
    self.status1 |= status_indicator << 6
    self.status1 |= status_address_authority << 4
    self.status1 |= status_boot_mode << 2
    self.status1 |= status_rdm << 1
    self.status1 |= status_ubea

    self.esta_manufacturer = SystemConfig.esta_code
    self.short_name = short_name
    self.long_name = long_name
    self.node_report = (' ' * 63) + '\0'
    self.num_ports = 0
    self.port_types = port_types # Consoles or controllers do not implement input or output ports
    self.good_input = good_input
    self.good_output = good_output
    self.sw_in = [0, 0, 0, 0]
    self.sw_out = [0, 0, 0, 0]
    self.sw_video = 0
    self.sw_macro = 0
    self.sw_remote = 0
    self.style = style.value
    self.mac_address = mac_address
    self.bind_ip = self.ip_address
    self.bind_index = bind_index

    self.status2 = 0
    self.status2 |= status_squawking << 5
    self.status2 |= status_artnet_sacn_switch << 4
    self.status2 |= status_artnet34 << 3
    self.status2 |= status_dhcp_capable << 2
    self.status2 |= status_dhcp_configured << 1
    self.status2 |= status_web_browser

  def serialize(self):
    """
    Serializes a packet into a byte array, ready for transmission

    Returns:
      byte array -- The packet packed in order for transmission
    """

    output = bytearray(self.packet_id, 'ascii')
    output.extend(self.opcode.to_bytes(2, 'little'))
    output.extend(self.ip_address)
    output.extend(self.port.to_bytes(2, 'little'))
    output.extend(self.version_info.to_bytes(2, 'big'))
    output.append(self.net_switch)
    output.append(self.sub_switch)
    output.extend(self.oem.to_bytes(2, 'big'))
    output.append(self.ubea_version)
    output.append(self.status1)
    output.extend(self.esta_manufacturer.to_bytes(2, 'little'))
    output.extend(bytearray(self.short_name, 'ascii'))
    output.extend(bytearray(self.long_name, 'ascii'))
    output.extend(bytearray(self.node_report, 'ascii'))
    output.extend(self.num_ports.to_bytes(2, 'big'))
    output.extend(self.port_types)
    output.extend(self.good_input)
    output.extend(self.good_output)
    output.extend(self.sw_in)
    output.extend(self.sw_out)
    output.append(self.sw_video)
    output.append(self.sw_macro)
    # output.append(self.sw_remote)
    output.append(0x01)
    output.extend([0, 0, 0]) # filler
    output.append(self.style)
    output.extend(self.mac_address)
    output.extend(self.bind_ip)
    output.append(self.bind_index)
    output.append(self.status2)
    output.extend([0]*26) # filler

    return output
