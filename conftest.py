import json
import pytest
import numpy as np

from spotted.attribute import Attribute
from spotted.calibration import Calibration
from spotted.camera import Camera
from spotted.coordinate import Coordinate
from spotted.contour import Contour
from spotted.fixture import Fixture
from spotted.personality import Personality, load_personalities, PERSONALITIES
from spotted.point_of_interest import PointOfInterest
from spotted.room import Room
from spotted.spherical_coordinate import SphericalCoordinate
from spotted.universe import Universe
from spotted.universes import Universes

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
