from spotted.error import ErrorCode, exit_with_error
import pytest

def test_missing_config():
  assert ErrorCode.MissingConfig.value == 2

def test_missing_key():
  assert ErrorCode.MissingKey.value == 3

def test_empty_key():
  assert ErrorCode.EmptyKey.value == 4

def test_camera_connect():
  assert ErrorCode.CameraConnect.value == 5

def test_missing_interface():
  assert ErrorCode.MissingInterface.value == 6

def test_interface_address():
  assert ErrorCode.InterfaceAddress.value == 7

def test_exit_with_error_missing_config(capsys):
  with pytest.raises(SystemExit) as wrapped_error:
    exit_with_error(ErrorCode.MissingConfig, 'details')
  captured = capsys.readouterr()

  assert wrapped_error.value.code == ErrorCode.MissingConfig.value
  assert captured.out == 'A required config file could not be found: details\nExiting\n'

def test_exit_with_error_missing_key(capsys):
  with pytest.raises(SystemExit) as wrapped_error:
    exit_with_error(ErrorCode.MissingKey, 'details')
  captured = capsys.readouterr()

  assert wrapped_error.value.code == ErrorCode.MissingKey.value
  assert captured.out == '\'details\' key does not exist in the config\nExiting\n'

def test_exit_with_error_empty_key(capsys):
  with pytest.raises(SystemExit) as wrapped_error:
    exit_with_error(ErrorCode.EmptyKey, 'details')
  captured = capsys.readouterr()

  assert wrapped_error.value.code == ErrorCode.EmptyKey.value
  assert captured.out == '\'details\' key must contain at least one item\nExiting\n'

def test_exit_with_error_camera_connect(capsys):
  with pytest.raises(SystemExit) as wrapped_error:
    exit_with_error(ErrorCode.CameraConnect, 'details')
  captured = capsys.readouterr()

  assert wrapped_error.value.code == ErrorCode.CameraConnect.value
  assert captured.out == 'Camera \'details\' could not be opened.\nExiting\n'

def test_exit_with_error_missing_interface(capsys):
  with pytest.raises(SystemExit) as wrapped_error:
    exit_with_error(ErrorCode.MissingInterface, ['one', ['two']])
  captured = capsys.readouterr()

  assert wrapped_error.value.code == ErrorCode.MissingInterface.value
  assert captured.out == 'Configured interface \'one\' was not found on this host.\nAvailable interfaces are: two.\nExiting\n'

def test_exit_with_error_interface_address(capsys):
  with pytest.raises(SystemExit) as wrapped_error:
    exit_with_error(ErrorCode.InterfaceAddress, 'details')
  captured = capsys.readouterr()

  assert wrapped_error.value.code == ErrorCode.InterfaceAddress.value
  assert captured.out == 'Configured interface \'details\' does not have an IPv4 address\nExiting\n'
