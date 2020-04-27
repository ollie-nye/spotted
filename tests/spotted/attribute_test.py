from spotted.attribute import Attribute

def test_init():
  config = {
    'name': 'pan',
    'offset': 0,
    'attribute_type': 'position',
    'range': 540,
    'default': 127,
    'multiplier_type': 'wide',
    'multiplier_length': 2,
    'invert': 'false'
  }

  attribute = Attribute(config)

  assert attribute.name == 'pan'
  assert attribute.offset == 0
  assert attribute.attribute_type == 'position'
  assert attribute.range == 540
  assert attribute.default == 127
  assert attribute.multiplier_type == 'wide'
  assert attribute.multiplier_length == 2
  assert attribute.invert == False
