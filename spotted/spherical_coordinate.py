import math
import numpy as np

def pythagoras(ax, ay, bx, by):
  return math.sqrt(math.pow((ax - bx), 2) + math.pow((ay - by), 2))

class SphericalCoordinate:
  def __init__(self, r, a, i):
    self.radius = r
    self.azimuth = a
    self.inclination = i
    self.elevation = (math.pi / 2) - i

  @staticmethod
  def from_cartesian(coordinate):
    r = math.sqrt(coordinate.x**2 + coordinate.y**2 + coordinate.z**2)
    a = math.atan2(coordinate.y, coordinate.x)
    i = math.atan2(math.sqrt(coordinate.x**2 + coordinate.y**2), coordinate.z)
    return SphericalCoordinate(r, a, i)
