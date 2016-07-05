import atexit
from datetime import timedelta
import logging as log
import os
from random import choice
import simplejson as json
from string import ascii_uppercase
from concurrent.futures import ProcessPoolExecutor

import pyhark.saas
import speech_recognition

import tornado.ioloop
import tornado.web
import tornado.websocket

from werkzeug.utils import secure_filename

STAGING_AREA = '/tmp/'
STATIC_PATH = 'static'
HTML_TEMPLATE_PATH = 'templates'
LISTEN_PORT = 80
LANGUAGE = 'ja-JP'

log.basicConfig(
    level=log.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

settings = {
'static_path': os.path.join(os.path.dirname(__file__), STATIC_PATH),
'template_path': os.path.join(os.path.dirname(__file__), HTML_TEMPLATE_PATH)
}

default_hark_config = {
    'processType': 'batch',
    'params': {
        'numSounds': 2,
        'roomName': 'sample room',
        'micName': 'dome',
        'thresh': 21
    },
    'sources': [
        {'from': 0, 'to': 180},
        {'from': -180, 'to': 0},
    ]
}


class HttpRequestHandler(tornado.web.RequestHandler):

    @asynchronous
    def get(self):
        self.render('index.html')

    @gen.coroutine
    def post(self):
        log.info("Uploading asynchrounously")
        pool = ProcessPoolExecutor(max_workers=2)
        future = pool.submit(async_upload)
        yield future
        pool.shutdown()
        log.info("Rendering visualization page")
        self.render('visualize.html')

    def async_upload(self):
        file = self.request.files['file'][0]
        file_name = secure_filename(file['filename'])
        # Best effort to ensure same file name is unique per post
        random_string = ''.join(choice(ascii_uppercase) for i in range(10))
        audio_file = '{0}{1}_{2}'.format(STAGING_AREA, random_string, file_name)
        write_handle = open(audio_file, 'w')
        write_handle.write(file['body'])
        read_handle = open(audio_file, 'rb')
        # Attempt llogin in the event that hark session logged out
        hark.client.login()
        hark.client.createSession(default_hark_config)
        hark.upload_file(read_handle)
        log.info("Asynchronous upload complete")

# Wrapper around some PyHarkSaas methods
class Hark:


    def __init__(self):
        log.info('Initializing hark client')
        auth = json.load(open('harkauth.json'))
        client = pyhark.saas.PyHarkSaaS(auth['apikey'], auth['apisec'])
        client.login()
        self.client = client

    def get_audio(self, srcID, file_name):
        log.info('Retrieving separated audio %d from hark', srcID)
        with open(file_name, 'w') as write_handle:
            self.client.getSeparatedAudio(handle=write_handle,
                                          srcID=srcID)

    def delete_session(self):
        log.info('Deleting hark session %s', self.client.getSessionID())
        self.client.deleteSession()

    def upload_file(self, file_handle):
        log.info('Uploading file %s to hark', file_handle.name)
        self.client.uploadFile(file_handle)


# Wrapper around SpeechRecognition
class Speech:


    def __init__(self):
        log.info('Initializing speech client')
        self.auth = str(json.load(open('bingauth.json'))['apikey'])
        self.client = speech_recognition.Recognizer()

    def translate(self, file_name):
        transcription = 'Inaudible'
        with speech_recognition.AudioFile(os.path.join(os.path.dirname(
            os.path.realpath(__file__)), file_name)) as source:
            audio = self.client.record(source)
        log.info('Sending separated audio file to speech api')
        try:
            transcription = self.client.recognize_bing(audio,
                key=self.auth,
                language=LANGUAGE)
        # This exception should pass if there is no transcription.
        except speech_recognition.UnknownValueError:
            pass
        log.info('Transcription: %s', transcription)
        return transcription


class WebSocketHandler(tornado.websocket.SocketHandler):


    # Allow cross-origin web socket connections
    def check_origin(self, origin):
        return True

    # Invoked when socket closed by either end
    def on_connection_close(self):
        log.info('Web socket connection closed')
        clean_staging()

    # Invoked when socket is opened
    def open(self):
        log.info('Web socket connection established')
        # Do not hold packets for bandwidth optimization
        self.set_nodelay(True)
        # ioloop to wait before attempting to sending data 
        tornado.ioloop.IOLoop.instance().add_timeout(timedelta(seconds=0),
                                             self.send_data)

    def send_data(self, utterances_memo = []):
        if hark.client.getSessionID():
            results = hark.client.getResults()
            utterances = results['context']
        # If result contains more utterances than memo
        if len(utterances) > len(utterances_memo):
            # Must iterate since new utterances
            # could be anywhere in the result
            for utterance in utterances:
                utterance_id = utterance['srcID']
                # If utterance is new
                if utterance_id not in utterances_memo:
                    # Memoize the srcID
                    utterances_memo.append(utterance_id)
                    self.write_message(json.dumps(utterance))
                    log.info("Utterance %d written to socket", utterance_id)

        if hark.client.isFinished():
            # If we have all the utterances, transcribe, then close the socket
            if sum(results['scene']['numSounds'].values()) == len(utterances_memo):
                for srcID in range(len(utterances_memo)):
                    random_string = ''.join(choice(ascii_uppercase) for i in range(10))
                    file_name = '{0}{1}_part{2}.flac'.format(STAGING_AREA, random_string, srcID)
                    hark.get_audio(srcID, file_name)
                    transcription = speech.translate(file_name)
                    utterance = utterances[srcID]
                    seconds, milliseconds = divmod(utterance['startTimeMs'], 1000)
                    minutes, seconds = divmod(seconds, 60)
                    self.write_message(json.dumps(
                      '{0} at ({1}:{2}:{3}):'.format(utterance['guid'], minutes, seconds, milliseconds)))
                    self.write_message(json.dumps(transcription, ensure_ascii=False))
                del utterances_memo[:]
                self.close()
        else:
            tornado.ioloop.IOLoop.instance().add_timeout(timedelta(seconds=1), self.send_data)


def clean_staging():
   remove_all(STAGING_AREA)
   if hark.client.getSessionID():
       hark.delete_session()

def get_app():
    application = tornado.web.Application([
        (r'/', HttpRequestHandler),
        (r'/websocket', WebSocketHandler),
        (r'/favicon.ico', tornado.web.StaticFileHandler,
            dict(path=settings['static_path'])),
        ], **settings)
    return application

def remove_all(dir):
    log.info('Deleting contents of %s', dir)
    files = os.listdir(dir)
    for file in files:
        os.remove(dir + file)


if __name__ == '__main__':
    hark = Hark()
    speech = Speech()
    atexit.register(clean_staging)
    log.info('Initializing web application')
    app = get_app()
    app.listen(LISTEN_PORT)
    tornado.ioloop.IOLoop.instance().start()
