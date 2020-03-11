import numpy as np

def test_correct_init_net(universe):
  assert universe.net == 0

def test_correct_init_subnet(universe):
  assert universe.subnet == 1

def test_correct_init_universe(universe):
  assert universe.universe == 2

def test_correct_init_sub_universe(universe):
  assert universe.sub_universe == 0x12

def test_correct_init_levels(universe):
  zeros = np.zeros(512, dtype=np.uint8)
  assert all([a == b for a, b in zip(universe.levels, zeros)])

def test_correct_init_fixtures(universe):
  assert universe.fixtures == []

def test_add_fixture(universe, fixture):
  res = universe.add_fixture(fixture)
  assert fixture in universe.fixtures

  occupied_channels = np.zeros(512, dtype=bool)
  occupied_channels[0:15] = True

  assert all([a == b for a, b in zip(universe.occupied_channels, occupied_channels)])

  assert res

def test_add_fixture_incorrect_type(universe):
  res = universe.add_fixture('frog')
  assert 'not an instance of Fixture' in res

def test_add_fixture_twice(universe, fixture):
  res = universe.add_fixture(fixture)
  assert res

  res = universe.add_fixture(fixture)
  assert 'existing fixture' in res
