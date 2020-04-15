"""
Spotted error codes
"""

import sys
import enum

class ErrorCode(enum.Enum):
  """
  Provides standard exit codes for different errors
  """

  MissingConfig = 2
  MissingKey = 3
  EmptyKey = 4
  CameraConnect = 5

def exit_with_error(error_code, details=None):
  """
  Exits the application after printing an error corresponding to the code
  supplied

  Arguments:
    error_code {int} -- Error code to exit with
    details {object} -- Additional details to print in the error message
  """

  if error_code == ErrorCode.MissingConfig:
    print('A required config file could not be found:', details)
  elif error_code == ErrorCode.MissingKey:
    print(f"'{details}' key does not exist in the config")
  elif error_code == ErrorCode.EmptyKey:
    print(f"'{details}' key must contain at least one item")
  elif error_code == ErrorCode.CameraConnect:
    print(f"Camera '{details}' could not be opened.")

  print('Exiting')
  sys.exit(error_code)
