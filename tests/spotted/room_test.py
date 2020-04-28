from spotted.spotted.coordinate import Coordinate

def test_init_width(room):
  assert room.width == 3

def test_init_height(room):
  assert room.height == 4

def test_init_depth(room):
  assert room.depth == 5

def test_center(room):
  center = Coordinate(1.5, 2, 2.5)
  assert room.center().x == center.x
  assert room.center().y == center.y
  assert room.center().z == center.z
