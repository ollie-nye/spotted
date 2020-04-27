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

def test_str(coordinate):
  assert str(coordinate) == "(0.1, 0.2, 0.3)"

def test_repr(coordinate):
  assert repr(coordinate) == "(0.1, 0.2, 0.3)"

def test_add(coordinate):
  displaced = coordinate + coordinate

  assert displaced.x == 0.2
  assert displaced.y == 0.4
  assert displaced.z == 0.6

def test_sub(coordinate):
  secondary = Coordinate(0.2, 0.4, 0.6)

  diff = secondary - coordinate

  assert diff.x == 0.1
  assert diff.y == 0.2
  assert diff.z == 0.3

def test_truediv(coordinate):
  div = coordinate / 2

  assert div.x == 0.05
  assert div.y == 0.1
  assert div.z == 0.15

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
