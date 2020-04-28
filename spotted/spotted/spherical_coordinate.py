"""
Spherical coordinate representation
"""

import math

class SphericalCoordinate:
  """
  Spherical coordinate representation
  """

  def __init__(self, radius, azimuth, inclination):
    """
    Creates a SphericalCoordinate from the given parameters

    Arguments:
      radius {float} -- radius component
      azimuth {float} -- azimuth component
      inclination {float} -- inclination component

    Returns:
      SphericalCoordinate -- instance configured with given parameters
    """

    self.radius = radius
    self.azimuth = azimuth
    self.inclination = inclination
    self.elevation = (math.pi / 2) - inclination

  # pylint: disable=invalid-name
  @staticmethod
  def from_cartesian(x, y, z):
    """
    Takes a cartesian coordinate in standard axis, converts it to spherical
    0deg azimuth is +ve z axis

    Arguments:
      x {float} - x component
      y {float} - y component
      z {float} - z component

    Returns:
      SphericalCoordinate -- Pointing at the same position, from world origin
    """

    radius = math.sqrt(x**2 + y**2 + z**2)
    azimuth = math.atan2(x, z)
    inclination = math.atan2(math.sqrt(x**2 + z**2), y)
    return SphericalCoordinate(radius, azimuth, inclination)
