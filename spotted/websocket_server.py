"""
Websockets handler groups

Based on https://gist.github.com/SevenW/47be2f9ab74cac26bf21
"""

import struct
import socket
import threading

from hashlib import sha1
from base64 import b64encode
from enum import Enum
from http.server import SimpleHTTPRequestHandler

class Opcode(Enum):
  """
  Standard websocket opcode values
  """

  CONTINUE = 0x0
  TEXT = 0x1
  BINARY = 0x2
  CLOSE = 0x8
  PING = 0x9
  PONG = 0xa

class WebSocketError(Exception):
  """
  Websocket error
  """

class HTTPWebSocketsHandler(SimpleHTTPRequestHandler):
  """
  Websocket handler
  """

  def __init__(self):
    """
    Set defaults for websocket connection
    """

    super().__init__()
    self.guid = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
    self.connected = False
    self.mutex = threading.Lock()
    self.close_connection = None
    self.opcode = Opcode.CONTINUE

  def on_ws_message(self, message):
    """Override this handler."""

  def on_ws_connected(self):
    """Override this handler."""

  def on_ws_closed(self):
    """Override this handler."""

  def send_message(self, message):
    """
    Sends a message with text opcode

    Arguments:
      message {string} -- Message to send
    """

    self.__send_message(Opcode.TEXT, message)

  def setup(self):
    SimpleHTTPRequestHandler.setup(self)
    self.connected = False

  def do_GET(self):
    if self.headers.get("Upgrade", None) == "websocket":
      self.__handshake()
      self.__read_messages()

  def __read_messages(self):
    while self.connected:
      try:
        self.__read_next_message()
      except (socket.error, WebSocketError) as error:
        #websocket content error, time-out or disconnect.
        self.log_message("RCV: Close connection: Socket Error %s" % str(error.args))
        self.__ws_close()
      except error:
        #unexpected error in websocket connection.
        self.log_error("RCV: Exception: in _read_messages: %s" % str(error.args))
        self.__ws_close()

  def __read_next_message(self):
    try:
      self.opcode = ord(self.rfile.read(1)) & 0x0F
      length = ord(self.rfile.read(1)) & 0x7F
      if length == 126:
        length = struct.unpack(">H", self.rfile.read(2))[0]
      elif length == 127:
        length = struct.unpack(">Q", self.rfile.read(8))[0]
      masks = self.rfile.read(4)
      decoded = ""
      for char in self.rfile.read(length):
        decoded += chr(char ^ masks[len(decoded) % 4])
      self.__on_message(decoded)
    except (struct.error, TypeError) as error:
      if self.connected:
        raise WebSocketError("Websocket read aborted while listening")
      self.log_error("RCV: _read_next_message aborted after closed connection")

  def __send_message(self, opcode, message):
    try:
      self.request.send(bytes([0x80 + opcode]))
      length = len(message)
      if length <= 125:
        self.request.send(bytes([length]))
      elif 126 <= length <= 65535:
        self.request.send(bytes([126]))
        self.request.send(struct.pack(">H", length))
      else:
        self.request.send(bytes([127]))
        self.request.send(struct.pack(">Q", length))
      if length > 0:
        self.request.send(message.encode())
    except socket.error as error:
      #websocket content error, time-out or disconnect.
      self.log_message("SND: Close connection: Socket Error %s" % str(error.args))
      self.__ws_close()
    except error:
      #unexpected error in websocket connection.
      self.log_error("SND: Exception: in _send_message: %s" % str(error.args))
      self.__ws_close()

  def __handshake(self):
    headers = self.headers
    if headers.get("Upgrade", None) != "websocket":
      return
    key = headers['Sec-WebSocket-Key']
    hashed_key = sha1((key + self.guid).encode('ascii')).digest()
    digest = b64encode(hashed_key)
    self.send_response(101, 'Switching Protocols')
    self.send_header('Upgrade', 'websocket')
    self.send_header('Connection', 'Upgrade')
    self.send_header('Sec-WebSocket-Accept', digest.decode('ascii'))
    self.end_headers()
    self.connected = True
    self.on_ws_connected()

  def __ws_close(self):
    self.mutex.acquire()
    try:
      if self.connected:
        self.connected = False
        self.close_connection = 1
        try:
          self.__send_close()
        except socket.error:
          pass
        self.on_ws_closed()
      else:
        self.log_message("Attempted to close an already closed websocket")
    finally:
      self.mutex.release()

  def __on_message(self, message):
    if self.opcode == Opcode.CLOSE:
      self.__ws_close()
    elif self.opcode == Opcode.PING:
      self.__send_message(Opcode.PONG, message)
    elif self.opcode in [Opcode.CONTINUE, Opcode.TEXT, Opcode.BINARY]:
      self.on_ws_message(message)

  def __send_close(self):
    msg = bytearray()
    msg.append(0x80 + Opcode.CLOSE)
    msg.append(0x00)
    self.request.send(msg)

class Websocket(HTTPWebSocketsHandler):
  """
  Spotted Websocket
  """

  def on_ws_message(self, message):
    pass

  def on_ws_connected(self):
    self.log_message('%s', 'websocket connected')

  def on_ws_closed(self):
    self.log_message('%s', 'websocket disconnected')
