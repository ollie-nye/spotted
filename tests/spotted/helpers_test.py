from spotted.helpers import scale, pythagoras, handler_class_with_args

def test_scale():
  assert scale(0.5, 0, 1, 0, 10) == 5
  assert scale(0, -1, 1, 0, 10) == 5

def test_pythagoras():
  assert pythagoras(0, 0, 3, 4) == 5
