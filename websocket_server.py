import sys
import time
import random
import json
import datetime
import os
import pyhark.saas
from tornado import websocket, web, ioloop, httpserver
from werkzeug.utils import secure_filename
from datetime import timedelta
from random import randint

UPLOAD_FOLDER = '/tmp/'
ALLOWED_EXTENSIONS = set(['flac', 'wav', 'ogg'])
STATIC_PATH = "static"
TEMPLATE_PATH = "templates"
listen_port=80

settings = {
    "static_path": os.path.join(os.path.dirname(__file__), STATIC_PATH),
    "template_path": os.path.join(os.path.dirname(__file__), TEMPLATE_PATH),
}

paymentTypes = ["cash", "tab", "visa","mastercard","bitcoin"]
namesArray = ['Ben', 'Jarrod', 'Vijay', 'Aziz']
metadata = {   
        "processType": "batch",
        "params": {
            "numSounds": 2,
            "roomName": "sample room",
            "micName": "dome",
            "thresh": 21
        },
        "sources": [
            {"from": -180, "to": 0},
            {"from": 0, "to": 180},
        ]
    }

class Index(web.RequestHandler):
    def get(self):
        self.render("index.html")
    def post(self):
        if 'file' not in self.request.files:
            self.render("index.html")
        file = self.request.files['file'][0]
        if file and allowed_file(file['filename']):
            filename = secure_filename(file['filename'])
            writehandle = open(UPLOAD_FOLDER + filename, 'w')
            writehandle.write(file['body'])
            readhandle = open(UPLOAD_FOLDER + filename, 'rb')
            harkclient.uploadFile(readhandle)
        self.render("visualize.html")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

class HarkSaas:

  def authenticate(self):
    auth = json.load(open("harkauth.json"))
    client = pyhark.saas.PyHarkSaaS(auth["apikey"], auth["apisec"]) 
    client.login()
    client.createSession(metadata)
    return client

  def upload(metadata, client, filename):
    client.createSession(metadata)
    client.uploadFile(open(filename, 'rb'))

  def getLatestResults(client):
    return client.getResults()

class WebSocketHandler(websocket.WebSocketHandler):

  #override the default cross-origin check
  def check_origin(self, origin):
    return True

  #on open of this socket
  def open(self):
    print 'Connection established.'
    #ioloop to wait for 3 seconds before starting to send data
    ioloop.IOLoop.instance().add_timeout(datetime.
    timedelta(seconds=3), self.send_data)

 #close connection
  def on_close(self):
    print 'Connection closed.'

  # Our function to send new (random) data for charts
  def send_data(self):
    print "Sending Data"

    #create a bunch of random data for various dimensions we want
    #instead, pull data from hark here
    qty = random.randrange(1,4)
    total = random.randrange(30,1000)
    tip = random.randrange(10, 100)
    payType = paymentTypes[random.randrange(0,4)]
    name = namesArray[random.randrange(0,4)]
    spent = random.randrange(1,150);
    year = random.randrange(2012,2016)
    #create a new data point
    point_data = {
        'quantity': qty,
        'total' : total,
        'tip': tip,
        'payType': payType,
        'Name': name,
        'Spent': spent,
        'Year' : year,
        'x': time.time()
    }

    #write the json object to the socket
    self.write_message(json.dumps(point_data))

    #create new ioloop instance to intermittently publish data
    ioloop.IOLoop.instance().add_timeout(datetime.timedelta(seconds=1), self.send_data)

if __name__ == "__main__":
  print "Starting main..."
  HarkSaas = HarkSaas()
  harkclient = HarkSaas.authenticate()
  application = web.Application([
    (r'/', Index),
    (r'/websocket', WebSocketHandler),
    (r"/(apple-touch-icon\.png)", web.StaticFileHandler,
     dict(path=settings['static_path'])),
    ], **settings)

  application.listen(listen_port)
  ioloop.IOLoop.instance().start()
