import json
from spotted.attribute import Attribute

class Personality:
  def __init__(self, json):
    self.id = json['id']
    self.manufacturer = json['manufacturer']
    self.model = json['model']
    self.channels = json['channels']

    self.attributes = []
    for attribute_json in json['attributes']:
      self.attributes.append(Attribute(attribute_json))

  def get_attribute(self, name):
    for attribute in self.attributes:
      if attribute.name == name:
        return attribute
    return None

personalities = []

def load_personalities(path):
  personalities_json = json.load(open(path))
  for pers in personalities_json:
    personalities.append(Personality(pers))

def find_personality_by_id(personality_id):
  for personality in personalities:
    if personality.id == personality_id:
      return personality
  return None
