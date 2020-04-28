"""
Spotted Camera
"""

import math

import numpy as np
import cv2 as cv

from spotted.spotted.contour import Contour
from spotted.spotted.coordinate import Coordinate
from spotted.spotted.point_of_interest import PointOfInterest
from spotted.spotted.helpers import scale, create_rotation_matrix, pythagoras

def contour_center(contour):
  """
  Calculates the center of a given contour

  Arguments:
    contour {list} -- Contour to calculate center of

  Returns:
    (x, y)
  """

  moments = cv.moments(contour)
  return (int(moments["m10"] / moments["m00"]), int(moments["m01"] / moments["m00"]))

def find_neighbours(groups, center_x, center_y, threshold):
  """
  Finds surrounding groups of contours that are within a set distance

  Arguments:
    groups {list} -- list of existing groups
    center_x {float} -- x position of new contour
    center_y {float} -- y position of new contour
    threshold {float} -- value to determine if a contour is close enough

  Returns:
    set of close group indexes
  """

  close_groups = set()
  for i, group in enumerate(groups):
    for neighbour in group:
      diff_x = (neighbour['center'][0] - center_x)**2
      diff_y = (neighbour['center'][1] - center_y)**2
      distance = math.sqrt(diff_x + diff_y)
      if distance < threshold:
        close_groups.add(i)
  return close_groups

def contour_closeness(pair):
  """
  Returns the edge-to-edge difference between a pair of contours
  """

  one, two = pair

  spread = pythagoras(one.center_x, one.center_y, two.center_x, two.center_y)

  return spread - one.radius - two.radius

# pylint: disable=too-many-instance-attributes
class Camera:
  """
  Spotted Camera
  """

  def __init__(self, json, camera_id, calibration, stop_flags):
    """
    Create Camera object
      Also creates a camera capture object, so initialisation takes a second or so

    Arguments:
      json {JSON} -- Config for camera
      calibration {list} -- Calibration data for frame restore

    Returns:
      Camera
    """

    self.stop_flags = stop_flags
    self.cam_id = camera_id
    self.url = json['url']

    self.position = Coordinate(json['position']['x'], json['position']['y'], json['position']['z'])

    self.rotation = Coordinate(json['rotation']['x'], json['rotation']['y'], json['rotation']['z'])

    self.viewing_angle = {
      'vertical': json['viewing_angle']['vertical'],
      'horizontal': json['viewing_angle']['horizontal']
    }

    self.resolution = {
      'vertical': json['resolution']['vertical'],
      'horizontal': json['resolution']['horizontal'],
    }

    self.virtual_resolution = {
      'horizontal': 960,
      'vertical': 720
    }

    self.angular_horiz_midpoint = self.viewing_angle['horizontal'] / 2
    self.angular_vert_midpoint = self.viewing_angle['vertical'] / 2
    self.horiz_midpoint = self.virtual_resolution['horizontal'] / 2
    self.vert_midpoint = self.virtual_resolution['vertical'] / 2

    self.calibration = calibration

    self.capture = cv.VideoCapture(self.url)

    self.resolution_yx = (
      self.virtual_resolution['vertical'],
      self.virtual_resolution['horizontal']
    )
    self.resolution_xy = (
      self.virtual_resolution['horizontal'],
      self.virtual_resolution['vertical']
    )

    self.current_background = np.zeros(self.resolution_yx, dtype=np.uint8)
    self.current_frame = None

    self.kernel = np.ones((4, 4), np.uint8)
    self.big_kernel = np.ones((10, 10), np.uint8)
    self.blur_kernel = np.ones((4, 4), np.uint8) / (4**2)

    self.points_of_interest = []

    self.rotation_matrix = create_rotation_matrix(
      self.rotation.x, self.rotation.y, self.rotation.z
    )

    midpoint = (self.horiz_midpoint, self.vert_midpoint)
    self.initial_point = self.calculate_real_world_coordinate(midpoint)

  def create_initial_frame(self):
    """
    Create the initial background model

    Returns:
      np.array
    """

    init_frame = np.zeros(self.resolution_yx, dtype=np.float)

    initial_frames = 30
    skip_frames = 60

    for i in range(initial_frames + skip_frames):
      ret, frame = self.capture.read()
      if i < skip_frames:
        continue

      if ret:
        frame = self.preprocess_frame(frame)
        cv.accumulateWeighted(frame, init_frame, 0.1)

    return init_frame

  def preprocess_frame(self, frame):
    """
    Apply standard operations to every frame: Undistorts, resizes, blurs and
    resizes to a standard size

    Arguments:
      frame {np.array} -- Frame to process

    Returns:
      np.array
    """

    frame = self.calibration.restore(frame)
    frame = cv.resize(frame, self.resolution_xy)
    frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    frame = cv.filter2D(frame, -1, self.blur_kernel)
    return frame

  def process_frame(self, frame, background):
    """
    Extracts contours from a frame by segmenting against the given background

    Arguments:
      frame {np.array} -- Frame to use in comparison
      background {np.array} -- Background model

    Returns:
      list of contours, diff, masked frame
    """

    diff = abs(np.subtract(frame, background)).astype(np.uint8)

    _, mask = cv.threshold(frame, 240, 255, cv.THRESH_TOZERO_INV, frame)
    mask = mask.astype(bool)
    _, diff = cv.threshold(diff, 45, 255, cv.THRESH_BINARY)
    diff = (diff * mask).astype(np.uint8)

    diff = cv.morphologyEx(diff, cv.MORPH_CLOSE, self.kernel)
    diff = cv.morphologyEx(diff, cv.MORPH_OPEN, self.kernel)
    diff = cv.erode(diff, self.kernel)

    contours, _ = cv.findContours(diff, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    return contours, diff, frame

  def group_contours(self, contours):
    """
    Groups nearby contours together by appending
    Does not change any contours until all have been assigned to stop possible random bias

    Arguments:
      contours {list} -- Original list of individual contours

    Returns:
      list -- New list of joined contours
    """

    blank = np.zeros(self.resolution_yx, dtype=np.uint8)

    grouped_contours = set()
    contour_objects = [Contour(points) for points in contours]
    for contour in [contour for contour in contour_objects if contour.area > 1200]:
      grouped_contours.add(contour)

    filtered_contours = [contour.np_points for contour in grouped_contours]

    blank = cv.drawContours(blank, filtered_contours, -1, 255, -1)
    for _ in range(10):
      blank = cv.dilate(blank, self.big_kernel)
    for _ in range(5):
      blank = cv.erode(blank, self.big_kernel)

    contours, _ = cv.findContours(blank, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    contour_objects = [Contour(points) for points in contours]

    return [contour.np_points for contour in contour_objects if contour.area > 2000], blank

  def begin_capture(self):
    """
    Starts an infinite loop of frame captures.
    Sets self.current_frame to the overdrawn frame for possible output
    """

    avg_frame = np.zeros(self.resolution_yx, dtype=np.float)
    init_frame = self.create_initial_frame()

    while True:
      if self.stop_flags['camera']:
        break

      ret, frame = self.capture.read()

      if ret:
        frame = self.preprocess_frame(frame)

        if avg_frame is None:
          avg_frame = frame
        cv.accumulateWeighted(frame, avg_frame, 0.2)
        contours, diff, frame = self.process_frame(frame, init_frame)

        diff = np.zeros_like(diff)
        contours, grouping_output = self.group_contours(contours)
        self.update_pois(contours, diff)
        self.points_of_interest = [x for x in self.points_of_interest if x.count != 1]
        diff = self.draw_pois(diff)

        out_frame = cv.resize(frame, (300, 225))
        for frm in [grouping_output, diff, self.current_background]:
        # for frm in [self.current_background]:
          if frm is not None:
            frm = cv.resize(frm, (300, 225))
            out_frame = np.hstack((out_frame, frm))
        self.current_frame = out_frame

  def draw_pois(self, frame):
    """
    Draws all pois on the given frame with the highest weight drawn at 255 and
    all others at 150 intensity.

    Arguments:
      frame {np.array} -- Frame to draw on

    Returns:
      np.array drawn over with location of pois
    """

    highest_weight = 0
    significant_poi = None
    for poi in self.points_of_interest:
      if poi.weight > highest_weight:
        highest_weight = poi.weight
        significant_poi = poi

    for poi in self.points_of_interest:
      if poi is significant_poi:
        cv.circle(frame, poi.location, 15, 255, -1)
      else:
        cv.circle(frame, poi.location, 15, 150, -1)

    return frame

  def calculate_real_world_coordinate(self, location):
    """
    Calculates a real world coordinate from the camera's physical properties
    Takes into account viewing angle, camera rotation in space and position

    Arguments:
      location (x, y) -- Relative pixel coordinates of a point

    Returns:
      Coordinate
    """

    center_x, center_y = location

    displacement_horizontal = center_x - self.horiz_midpoint
    displacement_vertical = -(center_y - self.vert_midpoint)

    angular_displacement_horizontal = math.radians(
      scale(displacement_horizontal, 0, self.horiz_midpoint, 0, self.angular_horiz_midpoint)
    )
    angular_displacement_vertical = math.radians(
      scale(displacement_vertical, 0, self.vert_midpoint, 0, self.angular_vert_midpoint)
    )

    identity_x = 1.0
    identity_y = identity_x * math.tan(angular_displacement_vertical)
    identity_z = identity_x * math.tan(angular_displacement_horizontal)

    identity_position = [identity_x, identity_y, identity_z]

    rotated_position = self.rotation_matrix[2].dot(identity_position)
    rotated_position = self.rotation_matrix[1].dot(rotated_position)
    rotated_position = self.rotation_matrix[0].dot(rotated_position)

    rotated_position = Coordinate(*rotated_position)

    return rotated_position + self.position

  def update_pois(self, contours, frame):
    """
    Updates instance points_of_interest with moved points, creating new ones if
    none are close enough
    Draws the contours on the frame

    Arguments:
      contours {list} -- list of contours
      frame {list} -- current camera frame
    """

    updated_pois = []

    for contour in contours:
      if cv.contourArea(contour) < 20:
        continue
      (center_x, center_y), radius = cv.minEnclosingCircle(contour)
      center_x, center_y, radius = int(center_x), int(center_y), int(radius)
      cv.circle(frame, (center_x, center_y), radius, 180, 1)
      cv.drawContours(frame, [contour], -1, 100, 2)

      displaced_position = self.calculate_real_world_coordinate((center_x, center_y))

      # keep it within the bounds of the world
      if (displaced_position.x < 0) or (displaced_position.y < 0) or (displaced_position.z < 0):
        continue

      made_update = False
      for poi in self.points_of_interest:
        diff_from_pos = poi.diff_from_position(displaced_position)
        if diff_from_pos < 0.1:
          poi.update_position(displaced_position, (center_x, center_y))
          poi.increment_count()
          updated_pois.append(poi)
          made_update = True
          break

      if not made_update:
        poi = PointOfInterest(displaced_position, (center_x, center_y), self.position)
        updated_pois.append(poi)
        self.points_of_interest.append(poi)

    missing_pois = set(self.points_of_interest) - set(updated_pois)
    for missing_poi in missing_pois:
      missing_poi.decrement_count()
