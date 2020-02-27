class SpottedAttribute:
  def __init__(self, json):
    self.name = json['name']
    self.offset = json['offset']
    self.attribute_type = json['attribute_type']
    self.range = json['range']
    self.default = json['default']
    self.multiplier_type = json['multiplier_type']
    self.multiplier_length = json['multiplier_length']
