import cv2 as cv
import numpy as np
import math
from datetime import datetime

from spotted.coordinate import Coordinate
from spotted.point_of_interest import PointOfInterest



class Camera:
  def __init__(self, json):
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
      'vertical': 480,
      'horizontal': 640
    }

    self.capture = cv.VideoCapture(self.url)

    self.background_frame_length = 90.0
    self.current_background = None
    self.current_frame = None

    self.points_of_interest = []

    a = math.radians(self.rotation.z)
    b = math.radians(self.rotation.y)
    c = math.radians(self.rotation.x)

    self.rotation_matrix = np.array([
      [
        math.cos(a) * math.cos(b),
        (math.cos(a) * math.sin(b) * math.sin(c)) - (math.sin(a) * math.cos(c)),
        (math.cos(a) * math.sin(b) * math.cos(c)) + (math.sin(a) * math.sin(c))
      ],
      [
        math.sin(a) * math.cos(b),
        (math.sin(a) * math.sin(b) * math.sin(c)) + (math.cos(a) * math.cos(c)),
        (math.sin(a) * math.sin(b) * math.cos(c)) - (math.cos(a) * math.sin(c))
      ],
      [
        -math.sin(b),
        math.cos(b) * math.sin(c),
        math.cos(b) * math.cos(c)
      ]
    ])

  @staticmethod
  def imfill(frame):
    im_flood_fill = frame.copy()
    height, width = frame.shape[:2]
    mask = np.zeros((height + 2, width + 2), np.uint8)
    im_flood_fill = im_flood_fill.astype('uint8')
    cv.floodFill(im_flood_fill, mask, (0, 0), 255)
    im_flood_fill_inv = cv.bitwise_not(im_flood_fill)
    frame = frame.astype('uint8')
    return frame | im_flood_fill_inv

  @staticmethod
  def scale(value, old_min, old_max, new_min, new_max):
    old_range = (old_max - old_min)
    new_range = (new_max - new_min)
    return (((value - old_min) * new_range) / old_range) + new_min

  def y_offset(self, distance):
    return math.tan(self.rotation.z) * distance

  def update_background(self, new_frame):
    if self.current_background is None:
      self.current_background = np.array(new_frame, dtype=np.float)
    else:
      cv.accumulateWeighted(new_frame, self.current_background, 1.0 / self.background_frame_length)

  def begin_capture(self, calibration):
    count = 0
    start = datetime.now()
    kernel = np.ones((8, 8), np.uint8)
    while(1):
      # print('Processing frame', count, ' with framerate', (count / (datetime.now() - start).total_seconds()))
      count += 1
      ret, frame = self.capture.read()
      if frame is not None:
        frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        frame = calibration.restore(frame)
        frame = cv.resize(frame, (self.virtual_resolution['horizontal'], self.virtual_resolution['vertical']))


        # cv.threshold(frame, 120, 255, cv.THRESH_TOZERO, frame)
        self.update_background(frame)

        # frame[500:540, :] = 255

        # cv.imshow('VIDEO', frame)

        frame = np.subtract(frame, self.current_background)

        # print(diff[0,0])

        # ret, diff = cv.threshold(diff, 80, 255, cv.THRESH_TOZERO)
        # ret, diff = cv.threshold(diff, 180, 255, cv.THRESH_TOZERO_INV)
        ret, frame = cv.threshold(frame, 30, 255, cv.THRESH_BINARY)
        # cv.normalize(diff, diff, 0, 255, cv.NORM_MINMAX)


        # diff = float_to_int(diff)
        # ret, diff = cv.threshold(float_to_int(diff), 200, 255, cv.THRESH_TOZERO)
        # cv.imshow('VIDEO', float_to_int(camera.current_background))

        # diff = float_to_int(camera.current_background)

        # self.current_frame = imfill(diff)

        # self.current_frame = cv.morphologyEx(diff, cv.MORPH_CLOSE, kernel)




        frame = self.imfill(frame)
        frame = cv.morphologyEx(frame, cv.MORPH_OPEN, kernel)

        frame = np.array(frame, dtype=np.uint8)
        # print(type(frame))
        contours, hierarchy = cv.findContours(frame, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

        # self.points_of_interest = []

        # largest_contour = None
        # largest_area = 0
        # for contour in contours:
        #   area = cv.contourArea(contour)
        #   if area > largest_area:
        #     largest_area = area
        #     largest_contour = contour

        # if largest_contour is not None:
        cv.normalize(frame, frame, 0, 30, cv.NORM_MINMAX)

        updated_pois = []


        for contour in contours:
          area = cv.contourArea(contour)
          if area < 500:
            continue

          cv.drawContours(frame, [contour], -1, 100, 2)
          M = cv.moments(contour)
          cX = int(M["m10"] / M["m00"])
          cY = int(M["m01"] / M["m00"])
          # draw the contour and center of the shape on the image

          # Calculate distance along origin axis
          #   horizontal displacement
          #   vertical displacement
          # Translate by camera position
          # Translate by camera rotation matrix


          # identity position is a fixed 1m distance from the camera
          # Multiply the difference by actual depth value to get absolute positions

          # cX = 1024
          # cY = 768

          angular_horiz_midpoint = self.viewing_angle['horizontal'] / 2
          angular_vert_midpoint = self.viewing_angle['vertical'] / 2
          horiz_midpoint = self.virtual_resolution['horizontal'] / 2
          vert_midpoint = self.virtual_resolution['vertical'] / 2

          displacement_horizontal = cX - horiz_midpoint
          displacement_vertical = -(cY - vert_midpoint)

          # print('Displacement distance', displacement_horizontal, displacement_vertical)

          # angular_displacement_horizontal = math.radians((360 - scale(displacement_horizontal, 0, horiz_midpoint, 0, angular_horiz_midpoint)) % 360)
          # angular_displacement_vertical = math.radians((360 - scale(displacement_vertical, 0, vert_midpoint, 0, angular_vert_midpoint)) % 360)

          angular_displacement_horizontal = math.radians(scale(displacement_horizontal, 0, horiz_midpoint, 0, angular_horiz_midpoint))
          angular_displacement_vertical = math.radians(scale(displacement_vertical, 0, vert_midpoint, 0, angular_vert_midpoint))

          # print('Displacement angle', angular_displacement_horizontal, angular_displacement_vertical)

          identity_x = 1.0
          identity_y = identity_x * math.tan(angular_displacement_vertical)
          identity_z = identity_x * math.tan(angular_displacement_horizontal)

          identity_position = [identity_x, identity_y, identity_z]

          # print('Identity', identity_position[0], identity_position[1], identity_position[2])

          # rotated_position = identity_position.dot(self.rotation_matrix)
          rotated_position = self.rotation_matrix.dot(identity_position)

          # print('Rotated', rotated_position[0], rotated_position[1], rotated_position[2])

          rotated_position = Coordinate(rotated_position[0], rotated_position[1], rotated_position[2])

          displaced_position = rotated_position.displace_by(self.position)

          # print('Displaced', displaced_position.x, displaced_position.y, displaced_position.z)




          point_of_interest = None
          made_update = False
          for poi in self.points_of_interest:
            diff_from_pos = poi.diff_from_position(displaced_position)
            # print('Diff is ', diff_from_pos)
            if diff_from_pos < 0.05:
              poi.update_position(displaced_position, (cX, cY))
              poi.increment_count()
              point_of_interest = poi
              updated_pois.append(poi)
              made_update = True
              break

          if not made_update:
            poi = PointOfInterest(self.position, displaced_position, (cX, cY))
            point_of_interest = poi
            updated_pois.append(poi)
            self.points_of_interest.append(poi)

          # weight = point_of_interest.weight * 30
          # if weight > 255:
          #   weight = 255

          # print('Display weight is', weight)

          # cv.circle(frame, (cX, cY), 15, weight, -1)

        missing_pois = set(self.points_of_interest) - set(updated_pois)
        for missing_poi in missing_pois:
          missing_poi.decrement_count()

        self.points_of_interest = [x for x in self.points_of_interest if x.count != 1]

        highest_weight = 0
        significant_poi = None
        for poi in self.points_of_interest:
          if poi.weight > highest_weight:
            highest_weight = poi.weight
            significant_poi = poi

        for poi in self.points_of_interest:
          # print('Position', poi.position.as_vector(), 'and direction vector', poi.direction_vector)
          if poi is significant_poi:
            cv.circle(frame, poi.location, 15, 255, -1)
          else:
            cv.circle(frame, poi.location, 15, 150, -1)













          # horiz_midpoint = self.viewing_angle['horizontal'] / 2
          # vert_midpoint = self.viewing_angle['vertical'] / 2

          # angle_horizontal = scale(cX, 0, self.resolution['horizontal'], 0, self.viewing_angle['horizontal'])
          # angle_vertical = scale(cY, 0, self.resolution['vertical'], 0, self.viewing_angle['vertical'])

          # horiz_from_camera = (self.rotation['y'] - (self.viewing_angle['horizontal'] / 2) + angle_horizontal) % 360
          # vert_from_camera = (self.rotation['z'] - (self.viewing_angle['vertical'] / 2) + angle_vertical) % 360

          # # print((cX, cY), ' gave absolute angle ', horiz_from_camera, ', ', vert_from_camera)

          # # tan angle * 2m gives difference in real space from cameras location

          # horizontal_direction = 1
          # vertical_direction = 1

          # absolute_horiz = angle_horizontal
          # if absolute_horiz > horiz_midpoint:
          #   absolute_horiz -= horiz_midpoint
          # else:
          #   absolute_horiz = horiz_midpoint - absolute_horiz
          #   horizontal_direction = -1

          # absolute_vert = angle_vertical
          # if absolute_vert > vert_midpoint:
          #   absolute_vert -= vert_midpoint
          # else:
          #   absolute_vert = vert_midpoint - absolute_vert
          #   vertical_direction = -1

          # horiz_distance = math.tan(math.radians(absolute_horiz)) * 2
          # vert_distance = math.tan(math.radians(absolute_vert)) * 2

          # point = SpottedCoordinate(
          #   #TODO: Fix these static values
          #   4 - (self.position['x'] + (horiz_distance * horizontal_direction)),
          #   self.position['y'] + self.y_offset(2) + (vert_distance * vertical_direction),
          #   2
          # )

          # self.points_of_interest = [point]
        # else:
        #   self.points_of_interest = []
          # print(self.points_of_interest)

          # x_position = math.tan(math.radians(vert_from_camera)) * self.position['y']
          # print(x_position)

          # ox = self.position['x']
          # oz = 0
          # px = x_position
          # pz = 0

          # angle = math.radians(horiz_from_camera)

          # qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (pz - oz)
          # qz = oz + math.sin(angle) * (px - ox) + math.cos(angle) * (pz - oz)
          # print('x:', qx, 'y: 0 z:', qz)



          # self.points_of_interest = [(cX, cY)]
          # print(self.points_of_interest)

        self.current_frame = frame
        # self.current_frame = cv.dilate(diff, kernel)

        # diff = cv.resize(diff, ( 1024, 768 ))
        # # cv.imshow('VIDEO', float_to_int(camera.current_background))
        # cv.imshow('VIDEO', diff/255)
        # # cv.imshow('VIDEO', frame)
        # cv.waitKey(1)

  def process_frame(self, room):
    # Cameras must be flat in the horizontal plane, no x rotation
    # pois = [
    #   { 'x': 0, 'y': 0 },
    #   { 'x': 1920, 'y': 1080 },
    #   { 'x': 1920, 'y': 0 },
    #   { 'x': 0, 'y': 1080 },
    #   { 'x': 960, 'y': 540 }
    # ]

    # midpoint_vertical = self.resolution['vertical'] / 2
    # midpoint_horizontal = self.resolution['horizontal'] / 2

    print(self.position)

    for poi in self.points_of_interest:
      angle_horizontal = scale(poi['x'], 0, self.resolution['horizontal'], 0, self.viewing_angle['horizontal'])
      angle_vertical = scale(poi['y'], 0, self.resolution['vertical'], 0, self.viewing_angle['vertical'])

      horiz_from_camera = (self.rotation['y'] - (self.viewing_angle['horizontal'] / 2) + angle_horizontal) % 360
      vert_from_camera = (self.rotation['z'] - (self.viewing_angle['vertical'] / 2) + angle_vertical) % 360

      print(poi, ' gave absolute angle ', horiz_from_camera, ', ', vert_from_camera)

      x_position = math.tan(math.radians(vert_from_camera)) * self.position['y']
      print(x_position)

      ox = self.position['x']
      oz = 0
      px = x_position
      pz = 0

      angle = math.radians(horiz_from_camera)

      qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (pz - oz)
      qz = oz + math.sin(angle) * (px - ox) + math.cos(angle) * (pz - oz)
      print('x:', qx, 'y: 0 z:', qz)
