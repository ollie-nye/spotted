"""
Spotted Personality
"""

import json
from spotted.attribute import Attribute

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
    self.channels = config['channels']

    self.attributes = []
    for attribute_config in config['attributes']:
      self.attributes.append(Attribute(attribute_config))

  def get_attribute(self, name):
    """
    Attribute getter by name

    Arguments:
      name {string} -- name of attribute to find

    Returns:
      Attribute if found
      None if not
    """

    for attribute in self.attributes:
      if attribute.name == name:
        return attribute
    return None

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

def find_personality_by_id(personality_id):
  """
  Finds a loaded personality by id

  Arguments:
    personality_id {int} -- id of personality to find

  Returns:
    Personality if found
    None if not
  """

  for personality in PERSONALITIES:
    if personality.personality_id == personality_id:
      return personality
  return None
