def get_bit(value, position):
  return (value & (1 << position)) >> position
