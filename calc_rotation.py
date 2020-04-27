import math
import numpy as np

from spotted.helpers import create_rotation_matrix
from spotted.coordinate import Coordinate

def apply_rotation(initial_position, rotation):
  identity_position = [1, 0, 0]

  rotation_matrix = create_rotation_matrix(*rotation)

  # rotated_position = rotation_matrix[1].dot(identity_position)
  # rotated_position = rotation_matrix[0].dot(rotated_position)
  # rotated_position = rotation_matrix[2].dot(rotated_position)

  rotated_position = rotation_matrix[1].dot(identity_position)
  rotated_position = rotation_matrix[0].dot(rotated_position)
  rotated_position = rotation_matrix[2].dot(rotated_position)


  rotated_position = Coordinate(*rotated_position)

  return rotated_position.displace_by(initial_position)







# "position": { "x": 2.128, "y": 2.253, "z": 0.610 },
# initial_position = Coordinate(2.128, 2.253, 0.610)
# aim = Coordinate(2.14, 1.89, 1.42)
# rotation = [-22, 90, 0]


# "position": { "x": 0.15, "y": 2.284, "z": 6.903 },
initial_position = Coordinate(0.15, 2.284, 6.903)
aim = Coordinate(0.76, 1.88, 6.222)
rotation = [30, -120, 0]



print(np.cross(aim.as_vector(), initial_position.as_vector()))





thresh = 0.2
step = 0.005

# increase in xrot increases y and z
# increase in yrot decreases x and increases z
# increase in zrot decreases x and y
made_update = False
while made_update:
  rotated = apply_rotation(initial_position, rotation)
  diff = aim.diff(rotated)

  print('Rotated', rotated.x, rotated.y, rotated.z)
  print('Diff', diff.x, diff.y, diff.z)
  print(rotation)

  made_update = False

  if abs(diff.x) > thresh:
    if diff.x < 0: #too far big
      rotation[1] += step
      rotation[2] += step
    else:
      rotation[1] -= step
      rotation[2] -= step
    made_update = True
    print('Updated x')
    # continue
  if abs(diff.y) > thresh:
    if diff.y < 0: #too far big
      rotation[0] -= step
      rotation[2] += step
    else:
      rotation[0] += step
      rotation[2] -= step
    made_update = True
    print('Updated y')
    # continue
  if abs(diff.z) > thresh:
    if diff.z < 0: #too far big
      rotation[0] -= step
      rotation[1] -= step
    else:
      rotation[0] += step
      rotation[1] += step
    made_update = True
    print('Updated z')
    # continue
