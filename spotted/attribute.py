"""
Attribute holds all data about a particular fixture channel
"""

# pylint: disable=too-many-instance-attributes, too-few-public-methods
class Attribute:
  """
  Attribute holds all data about a particular fixture channel
  """

  def __init__(self, json):
    """
    Creates a new instance of an attribute

    Arguments:
      json {dict} -- dictionary to prepopulate Attribute

    Returns:
      Attribute -- The populated attribute instance. Default values are: [
        range: 255,
        default: 255,
        multiplier_type: normal,
        multiplier_length: 1,
        invert: false
      ]
    """

    self.name = json['name']
    self.offset = json['offset']
    self.attribute_type = json['attribute_type']

    self.range = 255
    if 'range' in json:
      self.range = json['range']

    self.default = 0
    if 'default' in json:
      self.default = json['default']

    self.multiplier_type = 'normal'
    if 'multiplier_type' in json:
      self.multiplier_type = json['multiplier_type']

    self.multiplier_length = 1
    if 'multiplier_length' in json:
      self.multiplier_length = json['multiplier_length']

    self.invert = False
    if 'invert' in json:
      if json['invert'] == "true":
        self.invert = True
