import asyncio
import websockets
import json

class Websocket:
  def __init__(self, config, state):
    self.config = config
    self.state = state
    self.clients = set()

  def state_event(self):
    return json.dumps(self.state)

  async def notify_state(self):
    if self.clients:
      message = self.state_event()
      await asyncio.wait([client.send(message) for client in self.clients])

  async def register(self, websocket):
    self.clients.add(websocket)
    await websocket.send("init      " + json.dumps(self.config))

  async def unregister(self, websocket):
    self.clients.remove(websocket)

  async def broadcast_state(self, sleep_time):
    while True:
      for ws in self.clients:
        await ws.send("state     " + self.state_event())
      await asyncio.sleep(sleep_time)

  async def push_state(self, websocket, path):
    await self.register(websocket)
    # self.state = current_state
    try:
      async for msg in websocket:
        pass
    finally:
      await self.unregister(websocket)
