import math

def pythagoras(ax, ay, bx, by):
  return math.sqrt(math.pow((ax - bx), 2) + math.pow((ay - by), 2))

class SpottedCoordinate:
  def __init__(self, x, y, z):
    self.x = x
    self.y = y
    self.z = z

  def diff(self, b):
    return SpottedCoordinate(self.x - b.x, self.y - b.y, self.z - b.z)
    
  def pan_angle(self, b):
    diff = self.diff(b)
    angle = math.atan2(diff.z, diff.x)
    return math.degrees(angle)

  def tilt_angle(self, b):
    diff = self.diff(b)
    angle = math.atan2(diff.y, pythagoras(self.x, self.y, b.x, b.y))
    return math.degrees(angle)