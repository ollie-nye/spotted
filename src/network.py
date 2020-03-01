from artnet_dmx import ArtnetDmx
import time

import sys, socket

data = []
for i in range(512):
  data.append(0x00)

data[0] = 0
data[2] = 0

data[16] = 0
data[18] = 0

packet = ArtnetDmx(data)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while(1):
  sock.sendto(packet.serialize(), ('10.0.0.50', 6454))
  time.sleep(1/50)