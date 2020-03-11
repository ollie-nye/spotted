import cv2 as cv
from datetime import datetime
import sys

vcap = cv.VideoCapture('rtsp://192.168.0.62/11')

# text_file = open("Output.txt", "w")

count = 0

start = datetime.now()

while(1):
  if count > 240:
    break
  read_start = datetime.now()
  ret, frame = vcap.read()
  read_finish = datetime.now()
  print("frame cap took ", (read_finish - read_start).total_seconds())
  frame = frame[0]
  frame = [sum(pixel)/len(pixel) for pixel in frame]
  process_finish = datetime.now()
  print("processing took ", (process_finish - read_finish).total_seconds())
  print('Frame ', count)
  # print(frame, file=text_file)
  count += 1

# text_file.close()

finish = datetime.now()

duration = finish - start

print("processed ", count, " frames in ", duration.total_seconds(), " for a rate of ", count / duration.total_seconds())
