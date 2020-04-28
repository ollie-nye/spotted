"""
Simple static file server
"""

from http.server import BaseHTTPRequestHandler
import json

class StaticServer(BaseHTTPRequestHandler):
  """
  Simple static file server
  """

  def push_spotted_reference(self, handler_args):
    """
    Bring a reference to Spotted into the server handler

    Arguments:
      handler_args {Spotted} -- incoming spotted reference
    """

    self.spotted = handler_args

  def restart_threads(self, insurance):
    """
    Restarts all backend services

    Arguments:
      insurance {bool} -- Required to be True, stops this function running on parse
    """

    if insurance:
      spotted = self.spotted
      spotted.stop_flags['fixture'] = True
      spotted.stop_flags['camera'] = True
      spotted.stop_flags['artnet'] = True

      print('flags set')

      for thread in spotted.threads['fixtures']:
        thread.join()
      for thread in spotted.threads['cameras']:
        thread.join()
      for thread in spotted.threads['artnet']:
        thread.join()

      print('All threads stopped')

      spotted.init_config()

      spotted.start_support_threads(False)
      print('All threads started')

  # pylint: disable=invalid-name
  def do_GET(self):
    """
    Responds to file requests from the root directory
    """

    root = 'ui'
    if self.path == '/':
      filename = root + '/index.html'
    else:
      filename = root + self.path

    self.send_response(200)

    if filename[-4:] == '.css':
      self.send_header('Content-type', 'text/css')
    elif filename[-5:] == '.json':
      self.send_header('Content-type', 'application/javascript')
    elif filename[-3:] == '.js':
      self.send_header('Content-type', 'application/javascript')
    elif filename[-4:] == '.ico':
      self.send_header('Content-type', 'image/x-icon')
    else:
      self.send_header('Content-type', 'text/html')

    self.end_headers()
    if filename == 'ui/personalities.data':
      with open('spotted/config/personalities.json', 'rb') as file_handle:
        self.wfile.write(file_handle.read())
    elif filename == 'ui/config.data':
      with open('spotted/config/config.json', 'rb') as file_handle:
        self.wfile.write(file_handle.read())
    else:
      with open(filename, 'rb') as file_handle:
        self.wfile.write(file_handle.read())

  # pylint: disable=invalid-name
  def do_POST(self):
    """
    Responds to POST requests
    """

    content_length = int(self.headers['Content-Length'])
    data = self.rfile.read(content_length)

    if self.path == '/update/personalities':
      content = json.loads(data.decode('utf-8'))
      with open('spotted/config/personalities.json', 'w') as file_handle:
        json.dump(content, file_handle)
      self.send_response(201)
    elif self.path == '/update/config':
      content = json.loads(data.decode('utf-8'))
      with open('spotted/config/config.json', 'w') as file_handle:
        json.dump(content, file_handle)
      self.restart_threads(True)
      self.send_response(201)
    else:
      self.send_response(200)

    self.send_header('Content-type', 'text/html')
    self.end_headers()
