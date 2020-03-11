import pytest
import json

from spotted.attribute import Attribute
from spotted.calibration import Calibration
from spotted.camera import Camera
from spotted.coordinate import Coordinate
from spotted.fixture import Fixture
from spotted.personality import Personality, personalities
from spotted.point_of_interest import PointOfInterest
from spotted.room import Room
from spotted.spherical_coordinate import SphericalCoordinate
from spotted.universe import Universe
from spotted.universes import Universes

CONFIG = json.load(open('tests/config.json'))
PERSONALITIES = json.load(open('tests/personalities.json'))

def create_universe():
  return Universe(0, 1, 2)

@pytest.fixture
def universe():
  return create_universe()

@pytest.fixture
def universes():
  return Universes()

@pytest.fixture
def room():
  conf = CONFIG['room']
  return Room(conf['x'], conf['y'], conf['z'])

def create_personality():
  # Mirrors a beam
  return Personality(PERSONALITIES[0])

@pytest.fixture
def personality():
  return create_personality()

@pytest.fixture
def fixture():
  pers = create_personality()
  personalities.append(pers)
  return Fixture(CONFIG['fixtures'][0])