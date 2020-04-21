from spotted.error import ErrorCode

def test_missing_config():
  assert ErrorCode.MissingConfig.value == 2

def test_missing_key():
  assert ErrorCode.MissingKey.value == 3

def test_empty_key():
  assert ErrorCode.EmptyKey.value == 4

def test_camera_connect():
  assert ErrorCode.CameraConnect.value == 5
