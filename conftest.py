import json
import pytest
import numpy as np

from spotted.spotted.attribute import Attribute
from spotted.spotted.calibration import Calibration
from spotted.spotted.camera import Camera
from spotted.spotted.coordinate import Coordinate
from spotted.spotted.contour import Contour
from spotted.spotted.fixture import Fixture
from spotted.spotted.personality import Personality, load_personalities, PERSONALITIES
from spotted.spotted.point_of_interest import PointOfInterest
from spotted.spotted.room import Room
from spotted.spotted.spherical_coordinate import SphericalCoordinate
from spotted.spotted.universe import Universe
from spotted.spotted.universes import Universes

CONFIG = json.load(open('tests/config.json'))
load_personalities('tests/personalities.json')

@pytest.fixture
def calibration():
  return Calibration(CONFIG['calibration'])

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
  return PERSONALITIES[0]

@pytest.fixture
def personality():
  return create_personality()

@pytest.fixture
def fixture():
  return Fixture(CONFIG['fixtures']['0'], 0, {'fixture': False})

@pytest.fixture
def spherical_coordinate():
  return SphericalCoordinate(0.1, 0.2, 0.3)

@pytest.fixture
def coordinate():
  return Coordinate(0.1, 0.2, 0.3)

@pytest.fixture
def point_of_interest():
  camera_position = Coordinate(1, 2, 3)
  position = Coordinate(2, 4, 6)
  location = (200, 100)
  return PointOfInterest(position, location, camera_position)

@pytest.fixture
def contour_list():
  points = [(1, 1), (1, 2), (2, 2), (2, 1)]
  return Contour(points)

@pytest.fixture
def contour_array():
  points = np.array([(1, 1), (1, 2), (2, 2), (2, 1)])
  return Contour(points)
