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
    # self.elevation = i

  @staticmethod
# def from_cartesian(x, y, z):
  def from_cartesian(y, z, x):
    r = math.sqrt(x**2 + y**2 + z**2)
    a = math.atan2(y, x)
    i = math.atan2(math.sqrt(x**2 + y**2), z)
    return SphericalCoordinate(r, a, i)
