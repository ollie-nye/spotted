from spotted.spherical_coordinate import SphericalCoordinate
from spotted.coordinate import Coordinate

def test_init_r(spherical_coordinate):
  assert spherical_coordinate.r == 0.1
  assert spherical_coordinate.a == 0.2
  assert spherical_coordinate.i == 0.3

def test_from_cartesian():
  coord = Coordinate(1, 1, 1)
  spherical = SphericalCoordinate.from_cartesian(coord)

  assert spherical.r == 1.7320508075688772
  assert spherical.a == 0.7853981633974483
  assert spherical.i == 0.9553166181245093
