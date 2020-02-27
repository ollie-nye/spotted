import cv2 as cv
import numpy as np

class SpottedCamera:
  def __init__(self, json):
    self.url = json['url']

    self.position = {
      'x': json['position']['x'],
      'y': json['position']['y'],
      'z': json['position']['z']
    }

    self.rotation = {
      'x': json['rotation']['x'],
      'y': json['rotation']['y'],
      'z': json['rotation']['z']
    }

    self.viewing_angle = {
      'vertical': json['viewing_angle']['vertical'],
      'horizontal': json['viewing_angle']['horizontal']
    }

    self.resolution = {
      'vertical': 1080,
      'horizontal': 1920
    }

    self.capture = cv.VideoCapture(self.url)

    self.background_frames = []
    self.background_frame_length = 30.0
    self.background_frames_populated = False
    self.current_background = None
    self.current_background_frame = 0

  def average_background(self):
    # self.current_background = [sum(pixel)/len(pixel) for pixel in zip(*self.background_frames)]
    # self.current_background = np.mean([i for i in self.background_frames if i is not None], axis=0)
    self.current_background = np.mean(self.background_frames, axis=0)

    # cv.accumulateWeighted()


    # avg = np.array(self.background_frames[0], dtype=np.float)
    # for frame in self.background_frames:
    #   avg = cv.accumulate(frame, avg)
    # self.current_background = avg

    # avg_frame = self.background_frames[0]

    # for row in range(self.resolution['vertical']):
    #   for col in range(self.resolution['horizontal']):
    #     pixel_sum = 0
    #     for frame in self.background_frames:
    #       pixel_sum += frame[row, col]
    #     avg_frame[row, col] = pixel_sum / len(self.background_frames)
    
    # self.current_background = avg_frame


  def update_background(self, new_frame):
    if self.current_background is None:
      self.current_background = np.array(new_frame, dtype=np.float)
    else:
      cv.accumulateWeighted(new_frame, self.current_background, 1.0 / self.background_frame_length)
      # cv.accumulate(new_frame, self.current_background)
    # if self.background_frames_populated == False:
    #   self.background_frames.append(new_frame)
    # else:
    #   self.background_frames[self.current_background_frame] = new_frame
    # self.average_background()


    # self.current_background_frame = (self.current_background_frame + 1) % self.background_frame_length
    # if self.current_background_frame == 0:
    #   self.background_frames_populated = True

    # cv.imshow('VIDEO', np.array(self.current_background, dtype=np.uint8))
    # cv.waitKey(1)
