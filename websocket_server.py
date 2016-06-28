import sys
import time
import random
import json
import datetime
import os
import pyhark.saas
import speech_recognition
from os import path
from tornado import websocket, web, ioloop, httpserver
from werkzeug.utils import secure_filename
from datetime import timedelta
from random import randint

UPLOAD_FOLDER = '/tmp/'
ALLOWED_EXTENSIONS = set(['flac', 'wav', 'ogg'])
STATIC_PATH = "static"
TEMPLATE_PATH = "templates"
listen_port=80
BING_KEY = ''
AUDIO_FILE= ''

settings = {
    "static_path": os.path.join(os.path.dirname(__file__), STATIC_PATH),
    "template_path": os.path.join(os.path.dirname(__file__), TEMPLATE_PATH),
}

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
            AUDIO_FILE = UPLOAD_FOLDER + filename
            writehandle = open(AUDIO_FILE, 'w')
            writehandle.write(file['body'])
            readhandle = open(AUDIO_FILE, 'rb')
            harkclient.createSession(metadata)
            harkclient.uploadFile(readhandle)
        self.render("visualize.html")

def allowed_file(filename):
  return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

class HarkSaas:
  def client(self):
    auth = json.load(open("harkauth.json"))
    client = pyhark.saas.PyHarkSaaS(auth["apikey"], auth["apisec"]) 
    client.login()
    return client

class SpeechRecognition:
  def client(self):
    BING_KEY = json.load(open("bingauth.json"))["apikey"];
    return  speech_recognition.Recognizer();

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
    #delete hark session, wipe UPLOAD_PATH, and close/reset anything else 
    print 'Connection closed.'

  # Our function to send new (random) data for charts
  def send_data(self):
    print "Sending Data"
    
    data = harkclient.getResults()
    harkclient.wait()
    if data['context']:
        for entry in data['context']:
               filename = 'part' + str(entry['srcID']) + '.flac'
	       with open(filename, 'w') as filehandle:
	         harkclient.getSeparatedAudio(handle=filehandle, srcID=entry['srcID'])
               print(path.join(path.dirname(path.realpath(__file__)), filename))
	       with speech_recognition.AudioFile(path.join(path.dirname(path.realpath(__file__)), filename)) as source:
	         audio = speechclient.record(source)
	       utterance = speechclient.recognize_bing(audio, key=BING_KEY, language="ja-JP")
               #self.write_message(filelocation)
	       #write the json object to the socket
	       #self.write_message(json.dumps(data['scene']))
	       self.write_message(utterance)

    #create new ioloop instance to intermittently publish data
    ioloop.IOLoop.instance().add_timeout(datetime.timedelta(seconds=1), self.send_data)

if __name__ == "__main__":
  print "Starting main..."
  HarkSaas = HarkSaas()
  SpeechRecognition = SpeechRecognition()
  harkclient = HarkSaas.client()
  speechclient = SpeechRecognition.client()
  application = web.Application([
    (r'/', Index),
    (r'/websocket', WebSocketHandler),
    (r"/(apple-touch-icon\.png)", web.StaticFileHandler,
     dict(path=settings['static_path'])),
    ], **settings)

  application.listen(listen_port)
  ioloop.IOLoop.instance().start()
