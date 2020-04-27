import numpy as np

def test_init_list(contour_list):
  assert isinstance(contour_list.points, list)
  assert isinstance(contour_list.np_points, np.ndarray)
  assert contour_list.center_x == 1.5
  assert contour_list.center_y == 1.5
  assert contour_list.area == 1

def test_init_array(contour_array):
  assert isinstance(contour_array.points, list)
  assert isinstance(contour_array.np_points, np.ndarray)
  assert contour_array.center_x == 1.5
  assert contour_array.center_y == 1.5
  assert contour_array.area == 1
