"""
Mode holds all data about a particular fixture mode
"""

from spotted.attribute import Attribute

class Mode:
  """
  Mode holds all data about a particular fixture mode
  """

  def __init__(self, config, mode_id):
    """
    Creates a new instance of a mode

    Arguments:
      json {dict} -- dictionary to prepopulate Mode

    Returns:
      Mode
    """

    self.mode_id = mode_id
    self.name = config['name']
    self.channels = config['channels']
    self.attributes = []
    for _, attributes_config in config['attributes'].items():
      self.attributes.append(Attribute(attributes_config))

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
