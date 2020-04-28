"""
Spotted Websocket
"""

import asyncio
import json

class Websocket:
  """
  Spotted Websocket
  """

  def __init__(self, spotted):
    """
    Creates new websocket collection instance
    """

    self.spotted = spotted
    self.clients = set()

  def state_event(self):
    """
    Returns:
      JSON string representation of self.state
    """

    return json.dumps(self.spotted.current_state)

  async def register(self, websocket):
    """
    Adds client to clients set and sends the initial config out

    Arguments:
      websocket {Websocket} -- connection to add to clients
    """

    self.clients.add(websocket)
    await websocket.send("init      " + json.dumps(self.spotted.config))

  async def unregister(self, websocket):
    """
    Removes a client from the set

    Arguments:
      websocket {Websocket} -- client to remove
    """

    self.clients.remove(websocket)

  async def broadcast_state(self, sleep_time):
    """
    Broadcast infinite loop
    Sends current state to every connected client in the interval defined by
    sleep_time

    Arguments:
      sleep_time {float} -- inverval to wait between sending updates
    """

    while True:
      for websocket in self.clients:
        await websocket.send("state     " + self.state_event())
      await asyncio.sleep(sleep_time)

  async def push_state(self, websocket, _):
    """
    Main handler method, maintains connections to and from websockets

    Arguments:
      websocket {Websocket} -- websocket connection to manage
    """

    await self.register(websocket)
    # self.state = current_state
    try:
      async for msg in websocket:
        print('Received', msg, 'on websocket')
    finally:
      await self.unregister(websocket)
