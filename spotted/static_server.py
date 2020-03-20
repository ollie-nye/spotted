"""
Simple static file server
"""

from http.server import BaseHTTPRequestHandler

class StaticServer(BaseHTTPRequestHandler):
  """
  Simple static file server
  """

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
    with open(filename, 'rb') as file_handle:
      self.wfile.write(file_handle.read())
