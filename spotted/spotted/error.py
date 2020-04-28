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
  MissingInterface = 6
  InterfaceAddress = 7

def exit_with_error(error_code, details=None):
  """
  Exits the application after printing an error corresponding to the code
  supplied

  Arguments:
    error_code {int} -- Error code to exit with
    details {object} -- Additional details to print in the error message
  """

  if error_code is ErrorCode.MissingConfig:
    print('A required config file could not be found:', details)
  elif error_code is ErrorCode.MissingKey:
    print(f"'{details}' key does not exist in the config")
  elif error_code is ErrorCode.EmptyKey:
    print(f"'{details}' key must contain at least one item")
  elif error_code is ErrorCode.CameraConnect:
    print(f"Camera '{details}' could not be opened.")
  elif error_code is ErrorCode.MissingInterface:
    print(f"Configured interface '{details[0]}' was not found on this host.")
    print(f"Available interfaces are: {', '.join(details[1])}.")
  elif error_code is ErrorCode.InterfaceAddress:
    print(f"Configured interface '{details}' does not have an IPv4 address")

  print('Exiting')
  sys.exit(error_code.value)
