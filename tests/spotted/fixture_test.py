import math
from spotted.spotted.personality import find_personality_by_id
from spotted.spotted.coordinate import Coordinate

def test_init(fixture):
  assert fixture.stop_flags == {'fixture': False}
  assert fixture.fixture_id == 0
  assert fixture.personality == find_personality_by_id(0, 0)
  assert fixture.address == {
    'net': 0,
    'subnet': 0,
    'universe': 0,
    'address': 1
  }
  assert len(fixture.levels) == 16

  assert str(fixture.location) == str(Coordinate(1, 2, 3))
  assert str(fixture.position) == str(Coordinate(0, 0, 0))
  assert fixture.last_position is None
  assert fixture.current_aim is None
  assert fixture.position_step is None
  assert fixture.steps_taken == 0

  assert fixture.pan_offset == math.radians(180)
  assert fixture.tilt_invert is False

def test_open(fixture):
  offset = fixture.personality.get_attribute('dimmer').offset
  previous = fixture.levels[offset]
  fixture.open()

  assert fixture.levels[offset] == previous + 1

def test_open_limit(fixture):
  offset = fixture.personality.get_attribute('dimmer').offset
  for _ in range(260):
    fixture.open()

  assert fixture.levels[offset] == 255

def test_close(fixture):
  offset = fixture.personality.get_attribute('dimmer').offset
  fixture.levels[offset] = 10
  fixture.close()

  assert fixture.levels[offset] == 6

def test_close_limit(fixture):
  offset = fixture.personality.get_attribute('dimmer').offset
  fixture.levels[offset] = 255
  for _ in range(70):
    fixture.close()

  assert fixture.levels[offset] == 0

def test_pan_wide_low(fixture):
  pan_attribute = fixture.personality.get_attribute('pan')
  value = 0
  fixture.pan(value)

  assert fixture.levels[pan_attribute.offset] == 0
  assert fixture.levels[pan_attribute.offset + 1] == 0

def test_pan_wide_mid(fixture):
  pan_attribute = fixture.personality.get_attribute('pan')
  value = 32512
  fixture.pan(value)

  assert fixture.levels[pan_attribute.offset] == 127
  assert fixture.levels[pan_attribute.offset + 1] == 127

def test_pan_wide_high(fixture):
  pan_attribute = fixture.personality.get_attribute('pan')
  value = 65025
  fixture.pan(value)

  assert fixture.levels[pan_attribute.offset] == 255
  assert fixture.levels[pan_attribute.offset + 1] == 0

def test_pan_low(fixture):
  pan_attribute = fixture.personality.get_attribute('pan')
  pan_attribute.multiplier_type = 'normal'
  value = 0
  fixture.pan(value)

  assert fixture.levels[pan_attribute.offset] == 0

def test_pan_mid(fixture):
  pan_attribute = fixture.personality.get_attribute('pan')
  pan_attribute.multiplier_type = 'normal'
  value = 32512
  fixture.pan(value)

  assert fixture.levels[pan_attribute.offset] == 127

def test_pan_high(fixture):
  pan_attribute = fixture.personality.get_attribute('pan')
  pan_attribute.multiplier_type = 'normal'
  value = 65025
  fixture.pan(value)

  assert fixture.levels[pan_attribute.offset] == 255

def test_tilt_wide_low(fixture):
  tilt_attribute = fixture.personality.get_attribute('tilt')
  value = 0
  fixture.tilt(value)

  assert fixture.levels[tilt_attribute.offset] == 0
  assert fixture.levels[tilt_attribute.offset + 1] == 0

def test_tilt_wide_mid(fixture):
  tilt_attribute = fixture.personality.get_attribute('tilt')
  value = 32512
  fixture.tilt(value)

  assert fixture.levels[tilt_attribute.offset] == 127
  assert fixture.levels[tilt_attribute.offset + 1] == 127

def test_tilt_wide_high(fixture):
  tilt_attribute = fixture.personality.get_attribute('tilt')
  value = 65025
  fixture.tilt(value)

  assert fixture.levels[tilt_attribute.offset] == 255
  assert fixture.levels[tilt_attribute.offset + 1] == 0

def test_tilt_low(fixture):
  tilt_attribute = fixture.personality.get_attribute('tilt')
  tilt_attribute.multiplier_type = 'normal'
  value = 0
  fixture.tilt(value)

  assert fixture.levels[tilt_attribute.offset] == 0

def test_tilt_mid(fixture):
  tilt_attribute = fixture.personality.get_attribute('tilt')
  tilt_attribute.multiplier_type = 'normal'
  value = 32512
  fixture.tilt(value)

  assert fixture.levels[tilt_attribute.offset] == 127

def test_tilt_high(fixture):
  tilt_attribute = fixture.personality.get_attribute('tilt')
  tilt_attribute.multiplier_type = 'normal'
  value = 65025
  fixture.tilt(value)

  assert fixture.levels[tilt_attribute.offset] == 255

def test_point_at_initial_point(fixture):
  position = Coordinate(2, 1, 2)

  fixture.point_at(position)

  assert str(fixture.current_aim) == str(position)
  assert str(fixture.position_step) == str(Coordinate(0.0, 0.0, 0.0))
  assert fixture.steps_taken == 0

def test_point_at_existing_point(fixture):
  position = Coordinate(2, 1, 2)
  fixture.point_at(position)
  position = Coordinate(3, 1, 3)
  fixture.point_at(position)

  assert str(fixture.current_aim) == str(position)
  assert str(fixture.position_step) == str(Coordinate(0.1, 0.0, 0.1))
  assert fixture.steps_taken == 0
