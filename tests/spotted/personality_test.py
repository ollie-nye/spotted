from spotted.spotted.personality import find_personality_by_id

def test_init(personality):
  assert personality.personality_id == 0
  assert personality.manufacturer == 'hex'
  assert personality.model == '150w beam'
  assert len(personality.modes) == 1

def test_find_personality_by_id(personality):
  pers = find_personality_by_id(personality.personality_id, 0)

  assert pers.channels == 16

def test_find_personality_by_id_not_exist():
  pers = find_personality_by_id(100, 1)

  assert pers is None
