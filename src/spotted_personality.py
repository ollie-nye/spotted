import json
from spotted_attribute import SpottedAttribute

class SpottedPersonality:
  def __init__(self, json):
    self.id = json['id']
    self.manufacturer = json['manufacturer']
    self.model = json['model']
    self.channels = json['channels']
    
    self.attributes = []
    for attribute_json in json['attributes']:
      self.attributes.append(SpottedAttribute(attribute_json))

  def get_attribute(self, name):
    for attribute in self.attributes:
      if attribute.name == name:
        return attribute
    return None

personalities_json = json.load(open('config/personalities.json'))

personalities = []

for pers in personalities_json:
  personalities.append(SpottedPersonality(pers))
