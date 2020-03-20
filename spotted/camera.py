import cv2 as cv
import numpy as np
import math
from datetime import datetime

from spotted.coordinate import Coordinate
from spotted.point_of_interest import PointOfInterest
from spotted.helpers import imfill, scale, create_rotation_matrix


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

    # self.background_frame_length = 90.0
    self.background_frame_length = 5.0
    self.current_background = None
    self.current_frame = None

    self.points_of_interest = []

    self.rotation_matrix = create_rotation_matrix(
      self.rotation.x, self.rotation.y, self.rotation.z
    )

    # a = math.radians(self.rotation.z)
    # b = math.radians(self.rotation.y)
    # c = math.radians(self.rotation.x)

    # self.rotation_matrix = np.array([
    #   [
    #     math.cos(a) * math.cos(b),
    #     (math.cos(a) * math.sin(b) * math.sin(c)) - (math.sin(a) * math.cos(c)),
    #     (math.cos(a) * math.sin(b) * math.cos(c)) + (math.sin(a) * math.sin(c))
    #   ],
    #   [
    #     math.sin(a) * math.cos(b),
    #     (math.sin(a) * math.sin(b) * math.sin(c)) + (math.cos(a) * math.cos(c)),
    #     (math.sin(a) * math.sin(b) * math.cos(c)) - (math.cos(a) * math.sin(c))
    #   ],
    #   [
    #     -math.sin(b),
    #     math.cos(b) * math.sin(c),
    #     math.cos(b) * math.cos(c)
    #   ]
    # ])

  def y_offset(self, distance):
    return math.tan(self.rotation.z) * distance

  def update_background(self, new_frame):
    if self.current_background is None:
      self.current_background = np.array(new_frame, dtype=np.float)
    else:
      cv.accumulateWeighted(new_frame, self.current_background, 1.0 / self.background_frame_length)

  def proc_frame(self, kernel, frame):
    frame = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    # frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    # # grey = np.zeros((len(frame), len(frame[0])), dtype=np.uint8)
    start = datetime.now()
    # frame = np.array(np.array([[col[0] for col in row] for row in frame]) * (255 / 360), dtype=np.uint8)
    components = np.array(cv.split(frame))
    saturation = np.full(components[0].shape, 127, dtype=np.uint8)
    value = np.full(components[0].shape, 255, dtype=np.uint8)
    # print(components[0].dtype, components[1].dtype, components[2].dtype)
    # print(len(frame))
    # frame = np.array(list(zip(components[0], components[1], components[2])), dtype=np.uint8)
    # print(len(frame))
    frame = cv.merge([components[0], saturation, value])
    frame = cv.cvtColor(frame, cv.COLOR_HSV2BGR)
    # self.current_frame = frame
    frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    # for row_index, row in enumerate(frame):
    #   for col_index, col in enumerate(row):
    #     # col[2] = 127
    #     # h = scale(col[0], 0, 360, 0, 255)
    #     grey[row_index][col_index] = scale(col[0], 0, 360, 0, 255)
    print('calibrated in', (datetime.now() - start).total_seconds())
    # print('restored calibration')





    # self.current_frame = frame

    # rgb = cv.cvtColor(hsv, cv.COLOR_HSV2BGR)
    # grey = cv.cvtColor(cv.cvtColor(hsv, cv.COLOR_HSV2BGR), cv.COLOR_BGR2GRAY)

    print(frame.dtype)

    # cv.threshold(frame, 120, 255, cv.THRESH_TOZERO, frame)
    cv.normalize(frame, frame, 0, 255, cv.NORM_MINMAX)

    # self.current_frame = frame

    self.update_background(frame)

    # frame[500:540, :] = 255

    # cv.imshow('VIDEO', frame)

    frame = np.subtract(frame, self.current_background)

    # threshold = frame[np.nonzero(frame)].min()

    # print('threshold:', threshold)

    # self.current_frame = frame

    # print(diff[0,0])

    # ret, diff = cv.threshold(diff, 80, 255, cv.THRESH_TOZERO)
    # ret, diff = cv.threshold(diff, 180, 255, cv.THRESH_TOZERO_INV)

    ret, frame = cv.threshold(frame, 30, 255, cv.THRESH_BINARY)



    # diff = float_to_int(diff)
    # ret, diff = cv.threshold(float_to_int(diff), 200, 255, cv.THRESH_TOZERO)
    # cv.imshow('VIDEO', float_to_int(camera.current_background))

    # diff = float_to_int(camera.current_background)

    # self.current_frame = frame

    # self.current_frame = cv.morphologyEx(diff, cv.MORPH_CLOSE, kernel)




    frame = imfill(frame)
    frame = cv.morphologyEx(frame, cv.MORPH_OPEN, kernel)

    # self.current_frame = frame

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
      if area < 250:
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

  def begin_capture(self, calibration):
    count = 0
    start = datetime.now()
    kernel = np.ones((8, 8), np.uint8)
    blur_kernel = np.ones((8, 8), np.uint8) / (8**2)

    last_frame = None

    while(1):
      # print('Processing frame', count, ' with framerate', (count / (datetime.now() - start).total_seconds()))
      count += 1
      ret, frame = self.capture.read()
      if frame is not None:
        frame = calibration.restore(frame)
        frame = cv.resize(frame, (self.virtual_resolution['horizontal'], self.virtual_resolution['vertical']))

        # self.proc_frame(kernel, frame)

        frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        frame = cv.filter2D(frame, -1, blur_kernel)

        # frame = cv.morphologyEx(frame, cv.MORPH_OPEN, kernel)
        # frame = imfill(frame.astype(np.float))


        # frame = np.zeros_like(frame)

        # frame = frame / 5

        # for contour in contours:
        #   area = cv.contourArea(contour)
        #   # if area < 50:
        #   #   continue
        #   # cv.fillPoly(frame, pts=[contour], color=(50))


        if last_frame is not None:
          diff = (np.not_equal(last_frame, frame)*255).astype(np.uint8)
          diff = cv.morphologyEx(diff, cv.MORPH_OPEN, kernel)
          diff = cv.morphologyEx(diff, cv.MORPH_CLOSE, kernel)
          # self.current_frame = diff
          contours, hierarchy = cv.findContours(diff, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
          diff = np.zeros_like(diff)

          groups = []

          # pre_neighbourhood = np.copy(diff)

          # Group contours into neighbourhoods
          for contour in contours:
            M = cv.moments(contour)
            if cv.contourArea(contour) < 20:
              continue
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])

            # cv.drawContours(pre_neighbourhood, [contour], -1, 100, 2)

            # cv.circle(pre_neighbourhood, (cX, cY), 15, 255, -1)

            contour = {'contour': contour, 'center': (cX, cY)}

            # Do the grouping
            if len(groups) == 0:
              groups.append([contour])
            else:
              close_groups = set()
              for i, group in enumerate(groups):
                for neighbour in group:
                  x = (neighbour['center'][0] - cX)**2
                  y = (neighbour['center'][1] - cY)**2
                  distance = math.sqrt(x + y)
                  if distance < 100:
                    close_groups.add(i)
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

          updated_pois = []

          # print('contours:', len(contours))

          for contour in contours:
            area = cv.contourArea(contour)
            if area < 20:
              continue
            M = cv.moments(contour)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            # cv.drawContours(diff, [contour], -1, 100, 2)
            # print(contour)

            # cv.circle(diff, (cX, cY), 15, 255, -1)
            cv.drawContours(diff, [contour], -1, 100, 2)










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
              cv.circle(diff, poi.location, 15, 255, -1)
            else:
              cv.circle(diff, poi.location, 15, 150, -1)
          # print('Finished frame')
          self.current_frame = diff
        last_frame = frame



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

      horiz_from_camera = (self.rotation.y - (self.viewing_angle['horizontal'] / 2) + angle_horizontal) % 360
      vert_from_camera = (self.rotation.z - (self.viewing_angle['vertical'] / 2) + angle_vertical) % 360

      print(poi, ' gave absolute angle ', horiz_from_camera, ', ', vert_from_camera)

      x_position = math.tan(math.radians(vert_from_camera)) * self.position.y
      print(x_position)

      ox = self.position.x
      oz = 0
      px = x_position
      pz = 0

      angle = math.radians(horiz_from_camera)

      qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (pz - oz)
      qz = oz + math.sin(angle) * (px - ox) + math.cos(angle) * (pz - oz)
      print('x:', qx, 'y: 0 z:', qz)
