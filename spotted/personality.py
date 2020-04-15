"""
Spotted Personality
"""

import json
from spotted.mode import Mode

# pylint: disable=too-few-public-methods
class Personality:
  """
  Spotted Personality
  """

  def __init__(self, config):
    """
    Creates an instance of a personality from the given config
    Creates an attribute array

    Arguments:
      config {dict} -- json object to configure personality with
    """

    self.personality_id = config['id']
    self.manufacturer = config['manufacturer']
    self.model = config['model']

    self.modes = []
    for mode_config in config['modes']:
      self.modes.append(Mode(mode_config))

PERSONALITIES = []

def load_personalities(path):
  """
  Populate the static PERSONALITIES list with all personalitiles loaded from
  path

  Arguments:
    path {string} -- file to load personalities from
  """

  personalities_json = json.load(open(path))
  for pers in personalities_json:
    PERSONALITIES.append(Personality(pers))

def find_personality_by_id(personality_id, mode_id):
  """
  Finds a loaded personality and mode by id

  Arguments:
    personality_id {int} -- id of personality to find
    mode_id {int} -- id of mode to find

  Returns:
    Mode if found
    None if not
  """

  for personality in PERSONALITIES:
    if personality.personality_id == personality_id:
      for mode in personality.modes:
        if mode.mode_id == mode_id:
          return mode
  return None
