import math
import numpy as np

def pythagoras(ax, ay, az, bx, by, bz):
  return math.sqrt(math.pow((ax - bx), 2) + math.pow((ay - by), 2) + math.pow((az - bz), 2))

class SpottedPointOfInterest:
  def __init__(self, camera_position, position, location):
    self.camera_position = camera_position
    self.update_position(position, location)
    self.count = 100
    self.weight = 1

  def increment_count(self):
    self.count += 2
    self.recalculate_weight()

  def decrement_count(self):
    self.count -= 30
    if self.count < 1:
      self.count = 1
    self.recalculate_weight()

  def recalculate_weight(self):
    self.weight = math.log(self.count)
    if self.weight > 255:
      self.weight = 255

  def update_position(self, position, location):
    self.position = position
    self.location = location
    self.direction_vector = np.subtract(position.as_vector(), self.camera_position.as_vector())

  def diff_from_position(self, position):
    return pythagoras(self.position.x, self.position.y, self.position.z, position.x, position.y, position.z)