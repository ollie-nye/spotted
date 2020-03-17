from http.server import SimpleHTTPRequestHandler
import struct
from base64 import b64encode
from hashlib import sha1
import socket #for socket exceptions
import threading

class WebSocketError(Exception):
  pass

class HTTPWebSocketsHandler(SimpleHTTPRequestHandler):
  _ws_GUID = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
  _opcode_continu = 0x0
  _opcode_text = 0x1
  _opcode_binary = 0x2
  _opcode_close = 0x8
  _opcode_ping = 0x9
  _opcode_pong = 0xa

  mutex = threading.Lock()

  def on_ws_message(self, message):
    """Override this handler to process incoming websocket messages."""
    pass

  def on_ws_connected(self):
    """Override this handler."""
    pass

  def on_ws_closed(self):
    """Override this handler."""
    pass

  def send_message(self, message):
    self._send_message(self._opcode_text, message)

  def setup(self):
    SimpleHTTPRequestHandler.setup(self)
    self.connected = False

  # def finish(self):
    # #needed when wfile is used, or when self.close_connection is not used
    # #
    # #catch errors in SimpleHTTPRequestHandler.finish() after socket disappeared
    # #due to loss of network connection
    # try:
      # SimpleHTTPRequestHandler.finish(self)
    # except (socket.error, TypeError) as err:
      # self.log_message("finish(): Exception: in SimpleHTTPRequestHandler.finish(): %s" % str(err.args))

  # def handle(self):
    # #needed when wfile is used, or when self.close_connection is not used
    # #
    # #catch errors in SimpleHTTPRequestHandler.handle() after socket disappeared
    # #due to loss of network connection
    # try:
      # SimpleHTTPRequestHandler.handle(self)
    # except (socket.error, TypeError) as err:
      # self.log_message("handle(): Exception: in SimpleHTTPRequestHandler.handle(): %s" % str(err.args))

  def do_GET(self):
    if self.headers.get("Upgrade", None) == "websocket":
      self._handshake()
      #This handler is in websocket mode now.
      #do_GET only returns after client close or socket error.
      self._read_messages()
    else:
      SimpleHTTPRequestHandler.do_GET(self)

  def _read_messages(self):
    while self.connected == True:
      try:
        self._read_next_message()
      except (socket.error, WebSocketError) as e:
        #websocket content error, time-out or disconnect.
        self.log_message("RCV: Close connection: Socket Error %s" % str(e.args))
        self._ws_close()
      except Exception as err:
        #unexpected error in websocket connection.
        self.log_error("RCV: Exception: in _read_messages: %s" % str(err.args))
        self._ws_close()

  def _read_next_message(self):
    #self.rfile.read(n) is blocking.
    #it returns however immediately when the socket is closed.
    try:
      self.opcode = ord(self.rfile.read(1)) & 0x0F
      length = ord(self.rfile.read(1)) & 0x7F
      if length == 126:
        length = struct.unpack(">H", self.rfile.read(2))[0]
      elif length == 127:
        length = struct.unpack(">Q", self.rfile.read(8))[0]
      masks = [byte for byte in self.rfile.read(4)]
      decoded = ""
      for char in self.rfile.read(length):
        decoded += chr(ord(chr(char)) ^ masks[len(decoded) % 4])
      self._on_message(decoded)
    except (struct.error, TypeError) as e:
      #catch exceptions from ord() and struct.unpack()
      if self.connected:
        raise WebSocketError("Websocket read aborted while listening")
      else:
        #the socket was closed while waiting for input
        self.log_error("RCV: _read_next_message aborted after closed connection")

  def _send_message(self, opcode, message):
    try:
      #use of self.wfile.write gives socket exception after socket is closed. Avoid.
      self.request.send(bytes([0x80 + opcode]))
      length = len(message)
      if length <= 125:
        self.request.send(bytes([length]))
      elif length >= 126 and length <= 65535:
        self.request.send(bytes([126]))
        self.request.send(struct.pack(">H", length))
      else:
        self.request.send(bytes([127]))
        self.request.send(struct.pack(">Q", length))
      if length > 0:
        self.request.send(message.encode())
    except socket.error as e:
      #websocket content error, time-out or disconnect.
      self.log_message("SND: Close connection: Socket Error %s" % str(e.args))
      self._ws_close()
    except Exception as err:
      #unexpected error in websocket connection.
      self.log_error("SND: Exception: in _send_message: %s" % str(err.args))
      self._ws_close()

  def _handshake(self):
    headers = self.headers
    if headers.get("Upgrade", None) != "websocket":
      return
    key = headers['Sec-WebSocket-Key']
    hashed_key = sha1((key + self._ws_GUID).encode('ascii')).digest()
    digest = b64encode(hashed_key)
    self.send_response(101, 'Switching Protocols')
    self.send_header('Upgrade', 'websocket')
    self.send_header('Connection', 'Upgrade')
    self.send_header('Sec-WebSocket-Accept', digest.decode('ascii'))
    self.end_headers()
    self.connected = True
    #self.close_connection = 0
    self.on_ws_connected()

  def _ws_close(self):
    #avoid closing a single socket two time for send and receive.
    self.mutex.acquire()
    try:
      if self.connected:
        self.connected = False
        #Terminate BaseHTTPRequestHandler.handle() loop:
        self.close_connection = 1
        #send close and ignore exceptions. An error may already have occurred.
        try:
          self._send_close()
        except:
          pass
        self.on_ws_closed()
      else:
        self.log_message("_ws_close websocket in closed state. Ignore.")
        pass
    finally:
      self.mutex.release()

  def _on_message(self, message):
    #self.log_message("_on_message: opcode: %02X msg: %s" % (self.opcode, message))

    # close
    if self.opcode == self._opcode_close:
      self.connected = False
      #Terminate BaseHTTPRequestHandler.handle() loop:
      self.close_connection = 1
      try:
        self._send_close()
      except:
        pass
      self.on_ws_closed()
    # ping
    elif self.opcode == self._opcode_ping:
      self._send_message(self._opcode_pong, message)
    # pong
    elif self.opcode == self._opcode_pong:
      pass
    # data
    elif (self.opcode == self._opcode_continu or
        self.opcode == self._opcode_text or
        self.opcode == self._opcode_binary):
      self.on_ws_message(message)

  def _send_close(self):
    #Dedicated _send_close allows for catch all exception handling
    msg = bytearray()
    msg.append(0x80 + self._opcode_close)
    msg.append(0x00)
    self.request.send(msg)

class Websocket(HTTPWebSocketsHandler):
  def __init__(self):
    self.state_json = dict()

  def setup_state(self, state_json):
    self.state_json = state_json

  def on_ws_message(self, message):
    pass
    # if message is None:
    #   message = ''
    # # echo message back to client
    # print('sending message:', message)
    # self.send_message('init      {"room":{"x":4.2,"y":2.2,"z":4.0}}')
    # self.log_message('websocket received "%s"', message)

  def on_ws_connected(self):
    self.log_message('%s', 'websocket connected')
    self.send_message("init      " + str(self.state_json))

  def on_ws_closed(self):
    self.log_message('%s', 'websocket closed')
