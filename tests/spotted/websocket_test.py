from spotted.websocket import Websocket

def test_init():
  spotted = {'value': True}
  websocket = Websocket(spotted)

  assert websocket.spotted == spotted
  assert websocket.clients == set()

def test_state_event():
  class Spotted:
    def __init__(self):
      self.current_state = {'current_state': True}

  websocket = Websocket(Spotted())
  assert websocket.state_event() == '{"current_state": true}'
