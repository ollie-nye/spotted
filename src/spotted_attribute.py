class SpottedAttribute:
  def __init__(self, json):
    self.name = json['name']
    self.offset = json['offset']
    self.attribute_type = json['attribute_type']

    self.range = 255
    if 'range' in json:
      self.range = json['range']
    
    self.default = 255
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
