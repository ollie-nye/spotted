from spotted.coordinate import Coordinate

def test_init(coordinate):
  assert coordinate.x == 0.1
  assert coordinate.y == 0.2
  assert coordinate.z == 0.3

# def test_from_cartesian():
#   spherical = SphericalCoordinate.from_cartesian(1, 1, 1)

#   assert spherical.radius == 1.7320508075688772
#   assert spherical.azimuth == 0.7853981633974483
#   assert spherical.inclination == 0.9553166181245093

def test_diff(coordinate):
  secondary = Coordinate(0.2, 0.4, 0.6)

  diff = secondary.diff(coordinate)

  assert diff.x == 0.1
  assert diff.y == 0.2
  assert diff.z == 0.3

def test_displace_by(coordinate):
  displaced = coordinate.displace_by(coordinate)

  assert displaced.x == 0.2
  assert displaced.y == 0.4
  assert displaced.z == 0.6

def test_as_vector(coordinate):
  vec = coordinate.as_vector()

  assert vec[0] == coordinate.x
  assert vec[1] == coordinate.y
  assert vec[2] == coordinate.z

def test_as_dict(coordinate):
  dictionary = coordinate.as_dict()

  assert dictionary['x'] == coordinate.x
  assert dictionary['y'] == coordinate.y
  assert dictionary['z'] == coordinate.z
