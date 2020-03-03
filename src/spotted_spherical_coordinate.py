import math
import numpy as np

def pythagoras(ax, ay, bx, by):
  return math.sqrt(math.pow((ax - bx), 2) + math.pow((ay - by), 2))

class SpottedSphericalCoordinate:
  def __init__(self, r, a, i):
    self.r = r
    self.a = a
    self.i = i

  @staticmethod
  def from_cartesian(coordinate):
    r = math.sqrt(coordinate.x**2 + coordinate.y**2 + coordinate.z**2)
    a = math.atan2(coordinate.y, coordinate.x)
    i = math.atan2(math.sqrt(coordinate.x**2 + coordinate.y**2), coordinate.z)
    return SpottedSphericalCoordinate(r, a, i)
