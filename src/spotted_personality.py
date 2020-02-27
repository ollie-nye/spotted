import cv2 as cv

from spotted_attribute import SpottedAttribute

class SpottedPersonality:
  def __init__(self, json):
    self.manufacturer = json['manufacturer']
    self.model = json['model']
    
    self.attributes = []
    for attribute_json in json['attributes']:
      self.attributes.append(SpottedAttribute(attribute_json))
