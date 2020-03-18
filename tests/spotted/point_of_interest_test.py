import math
from spotted.point_of_interest import PointOfInterest
from spotted.coordinate import Coordinate

def test_init(point_of_interest):
  assert point_of_interest.camera_position.x == 1
  assert point_of_interest.camera_position.y == 2
  assert point_of_interest.camera_position.z == 3
  assert point_of_interest.position.x == 2
  assert point_of_interest.position.y == 4
  assert point_of_interest.position.z == 6
  assert point_of_interest.location == (200, 100)
  assert point_of_interest.count == 100
  assert point_of_interest.weight == 1
  assert all([a == b for a, b in zip(point_of_interest.direction_vector, [1, 2, 3])])

def test_pythagoras():
  assert PointOfInterest.pythagoras(2, 2, 2, 1, 1, 1) == 1.7320508075688772

def test_increment_count(point_of_interest):
  point_of_interest.increment_count()
  assert point_of_interest.count == 102
  assert point_of_interest.weight == 2.0086001717619175

def test_decrement_count(point_of_interest):
  point_of_interest.decrement_count()
  assert point_of_interest.count == 70

  point_of_interest.count = 10
  point_of_interest.decrement_count()
  assert point_of_interest.count == 1

def test_recalculate_weight(point_of_interest):
  point_of_interest.recalculate_weight()
  assert point_of_interest.count == 100
  assert point_of_interest.weight == 2

  point_of_interest.count = 10 ** 255
  point_of_interest.recalculate_weight()
  assert point_of_interest.weight == 255

  point_of_interest.count = 10 ** 256
  point_of_interest.recalculate_weight()
  assert point_of_interest.weight == 255

def test_update_position(point_of_interest):
  position = Coordinate(11, 12, 13)
  location = (100, 50)
  point_of_interest.update_position(position, location)

  assert point_of_interest.position == position
  assert point_of_interest.location == location
  assert all([a == b for a, b in zip(point_of_interest.direction_vector, [10, 10, 10])])

def test_diff_from_position(point_of_interest):
  position = Coordinate(1, 3, 5)
  assert point_of_interest.diff_from_position(position) == 1.7320508075688772
