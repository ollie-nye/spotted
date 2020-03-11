import pytest

def test_universes_init(universes):
  assert universes.universes == []

def test_add_universe_correct_type(universes, universe):
  universes.add_universe(universe)
  assert universe in universes.universes

def test_add_universe_incorrect_type(universes):
  with pytest.raises(Exception) as excinfo:
    universes.add_universe(5)
    assert 'not an instance' in str(excinfo.value)

def test_get_universe_exists(universes, universe):
  universes.add_universe(universe)
  assert universes.get_universe(0, 1, 2) == universe

def test_get_universe_doesnt_exist(universes):
  assert universes.get_universe(0, 1, 2) is None
