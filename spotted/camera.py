"""
Spotted Camera
"""

import math
import itertools

import numpy as np
import cv2 as cv

from datetime import datetime

from spotted.contour import Contour
from spotted.coordinate import Coordinate
from spotted.point_of_interest import PointOfInterest
from spotted.helpers import scale, create_rotation_matrix, pythagoras

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

def group_contours(contours):
  """
  Groups nearby contours together by appending
  Does not change any contours until all have been assigned to stop possible random bias

  Arguments:
    contours {list} -- Original list of individual contours

  Returns:
    list -- New list of joined contours
  """

  groups = []

  # Group contours into neighbourhoods
  for contour in contours:
    if cv.contourArea(contour) < 20:
      continue
    center_x, center_y = contour_center(contour)
    contour = {'contour': contour, 'center': (center_x, center_y)}

    # Do the grouping
    if len(groups) == 0:
      groups.append([contour])
    else:
      close_groups = find_neighbours(groups, center_x, center_y, 100)
      if len(close_groups) > 1:
        new_groups = []
        for i, group in enumerate(groups):
          if i not in close_groups:
            new_groups.append(group)
        neighbourhood = []
        for i in close_groups:
          neighbourhood.extend(groups[i])
        neighbourhood.append(contour)
        new_groups.append(neighbourhood)
        groups = new_groups
      elif len(close_groups) == 1:
        groups[list(close_groups)[0]].append(contour)
      else:
        groups.append([contour])

  # Create the singular neighbourhoods in place of multiple contours
  contours = []
  for group in groups:
    neighbourhood = []
    for contour in group:
      neighbourhood.extend(contour['contour'])
    contours.append(np.array(neighbourhood))

  return contours

def contour_closeness(pair):
  """

  """

  one, two = pair

  return pythagoras(one.center_x, one.center_y, two.center_x, two.center_y) - one.radius - two.radius


# pylint: disable=too-many-instance-attributes
class Camera:
  """
  Spotted Camera
  """

  def __init__(self, json, calibration):
    """
    Create Camera object
      Also creates a camera capture object, so initialisation takes a second or so

    Arguments:
      json {JSON} -- Config for camera
      calibration {list} -- Calibration data for frame restore

    Returns:
      Camera
    """

    self.cam_id = json['id']
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
      'horizontal': 640,
      'vertical': 480
    }

    self.angular_horiz_midpoint = self.viewing_angle['horizontal'] / 2
    self.angular_vert_midpoint = self.viewing_angle['vertical'] / 2
    self.horiz_midpoint = self.virtual_resolution['horizontal'] / 2
    self.vert_midpoint = self.virtual_resolution['vertical'] / 2

    self.calibration = calibration

    self.capture = cv.VideoCapture(self.url)

    self.current_background = None
    self.current_frame = None

    self.points_of_interest = []

    self.rotation_matrix = create_rotation_matrix(
      self.rotation.x, self.rotation.y, self.rotation.z
    )

    self.initial_point = self.calculate_real_world_coordinate((self.horiz_midpoint, self.vert_midpoint))

  def begin_capture(self):
    """
    Starts an infinite loop of frame captures.
    Sets self.current_frame to the overdrawn frame for possible output
    """

    kernel = np.ones((9, 9), np.uint8)
    blur_kernel = np.ones((9, 9), np.uint8) / (9**2)
    resolution = (self.virtual_resolution['horizontal'], self.virtual_resolution['vertical'])

    last_frame = None
    avg_frame = np.zeros((480, 640), dtype=np.float)

    while 1:
      ret, frame = self.capture.read()

      if ret:

        frame = self.calibration.restore(frame)
        frame = cv.resize(frame, resolution)
        frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        # frame = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        # hsv = cv.split(frame)
        # saturation = np.full_like(hsv[1], 180)
        # value = np.full_like(hsv[2], 127)
        # normalized = cv.merge([hsv[0], saturation, value])
        # frame = cv.cvtColor(normalized, cv.COLOR_HSV2BGR)
        # frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        frame = cv.filter2D(frame, -1, blur_kernel)

        # rgb = cv.split(frame)
        # for index, channel in enumerate(rgb):
        #   _, channel = cv.threshold(channel, 150, 255, cv.THRESH_TOZERO_INV)
        #   rgb[index] = channel
        # frame = cv.merge(rgb)

        if avg_frame is None:
          avg_frame = frame
        cv.accumulateWeighted(frame, avg_frame, 0.2)

        # average_frame_intensity = np.mean(frame)
        # average_frame = np.full_like(frame, average_frame_intensity)

        # frame = np.subtract(average_frame, frame)


        # if last_frame is not None:

        # print(frame)


        # diff = (np.not_equal(last_frame, frame)*255).astype(np.uint8)
        diff = (np.subtract(frame, avg_frame)).astype(np.uint8)
        # diff = (np.subtract(np.full_like(frame, 127), frame))
        # cv.normalize(diff, diff, 0, 255, cv.NORM_MINMAX)
        _, diff = cv.threshold(diff, 20, 255, cv.THRESH_BINARY)
        diff = cv.erode(diff, kernel)
        diff = cv.erode(diff, kernel)
        diff = cv.dilate(diff, kernel)
        # self.current_frame = diff
        # continue
        # diff = cv.morphologyEx(diff, cv.MORPH_OPEN, kernel)
        # diff = cv.morphologyEx(diff, cv.MORPH_CLOSE, kernel)


        contours, _ = cv.findContours(diff, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        diff = np.zeros_like(diff)

        grouped_contours = [Contour(points) for points in contours]
        made_update = True
        while made_update:
          made_update = False
          added_contours = set()

          contour_pairs = sorted(itertools.combinations(grouped_contours, 2), key=contour_closeness)
          grouped_contours = []
          for pair in contour_pairs:
            one, two = pair
            closeness = contour_closeness(pair)
            if closeness < 25:
              if (not one in added_contours) and (not two in added_contours):
                points = []
                points.extend(one.points)
                points.extend(two.points)
                grouped_contours.append(Contour(points))
                made_update = True
            else:
              if not one in added_contours:
                grouped_contours.append(one)
              if not two in added_contours:
                grouped_contours.append(two)
            added_contours.add(one)
            added_contours.add(two)

        # contours = [contour.np_points for contour in grouped_contours if contour.area > 100]
        contours = [contour.np_points for contour in grouped_contours]
        # contours = group_contours(contours)

        self.update_pois(contours, diff)

        self.points_of_interest = [x for x in self.points_of_interest if x.count != 1]

        highest_weight = 0
        significant_poi = None
        for poi in self.points_of_interest:
          if poi.weight > highest_weight:
            highest_weight = poi.weight
            significant_poi = poi

        for poi in self.points_of_interest:
          if poi is significant_poi:
            cv.circle(diff, poi.location, 15, 255, -1)
          else:
            cv.circle(diff, poi.location, 15, 150, -1)
        self.current_frame = np.vstack((frame, diff))

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

    rotated_position = self.rotation_matrix[1].dot(identity_position)
    rotated_position = self.rotation_matrix[0].dot(rotated_position)
    rotated_position = self.rotation_matrix[2].dot(rotated_position)

    rotated_position = Coordinate(*rotated_position)

    return rotated_position.displace_by(self.position)

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

      if (displaced_position.x < 0) or (displaced_position.y < 0) or (displaced_position.z < 0):
        continue

      made_update = False
      for poi in self.points_of_interest:
        diff_from_pos = poi.diff_from_position(displaced_position)
        if diff_from_pos < 0.05:
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
