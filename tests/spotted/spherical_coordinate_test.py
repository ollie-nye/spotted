from spotted.spherical_coordinate import SphericalCoordinate
from spotted.coordinate import Coordinate

def test_init_r(spherical_coordinate):
  assert spherical_coordinate.radius == 0.1
  assert spherical_coordinate.azimuth == 0.2
  assert spherical_coordinate.inclination == 0.3

def test_from_cartesian():
  spherical = SphericalCoordinate.from_cartesian(1, 1, 1)

  assert spherical.radius == 1.7320508075688772
  assert spherical.azimuth == 0.7853981633974483
  assert spherical.inclination == 0.9553166181245093
