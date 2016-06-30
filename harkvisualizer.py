from datetime import timedelta 
import json 
import logging as log 
from os import path, remove, listdir 
from time import sleep 
 
import pyhark.saas 
import speech_recognition 
 
from tornado import web, ioloop, websocket 
from werkzeug.utils import secure_filename 
 
UPLOAD_PATH = '/tmp/' 
ALLOWED_EXTENSIONS = set(['flac', 'wav', 'ogg']) 
STATIC_PATH = 'static' 
HTML_TEMPLATE_PATH = 'templates' 
LISTEN_PORT = 80 
LANGUAGE = 'ja-JP' 
 
log.basicConfig( 
    level=log.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s' 
) 
 
settings = { 
'static_path': path.join(path.dirname(__file__), STATIC_PATH), 
'template_path': path.join(path.dirname(__file__), HTML_TEMPLATE_PATH) 
} 
 
metadata = { 
    'processType': 'batch', 
    'params': { 
        'numSounds': 2, 
        'roomName': 'sample room', 
        'micName': 'dome', 
        'thresh': 21 
    }, 
    'sources': [ 
        {'from': -180, 'to': 0}, 
        {'from': 0, 'to': 180}, 
    ] 
} 
 
 
class HttpRequestHandler(web.RequestHandler): 
 
 
    def get(self): 
        self.render('index.html') 
 
    def post(self): 
        if 'file' not in self.request.files: 
            self.render('index.html') 
        file = self.request.files['file'][0] 
        if file and allowed_file(file['filename']): 
            file_name = secure_filename(file['filename']) 
            audio_file = UPLOAD_PATH + file_name 
            write_handle = open(audio_file, 'w') 
            write_handle.write(file['body']) 
            read_handle = open(audio_file, 'rb') 
            hark_client.createSession(metadata) 
            hark_client.uploadFile(read_handle) 
            self.render('visualize.html') 
 
 
class HarkSaas: 
 
 
    def client(self): 
        auth = json.load(open('harkauth.json')) 
        client = pyhark.saas.PyHarkSaaS(auth['apikey'], auth['apisec']) 
        client.login() 
        return client 
 
 
class WebSocketHandler(websocket.WebSocketHandler): 
 
 
    #allow cross-origin web socket connection 
    def check_origin(self, origin): 
        return True 

    def clean_staging(self):
        uploads = listdir(UPLOAD_PATH)
        for file in uploads:
            remove(UPLOAD_PATH + file)
        log.info('Deleted contents of upload path')
        hark_client.deleteSession()
        log.info('Deleted hark session')

    # Invoked when anyone closes the socket
    def on_connection_close(self):
        self.clean_staging()

    # Called upon open of this socket 
    def open(self): 
        log.info('Connection established') 
        # ioloop to wait for 2 seconds before sending data 
        ioloop.IOLoop.instance().add_timeout(timedelta(seconds=2),  
                                             self.send_data) 
 
    def send_data(self): 
        speech_client = speech_recognition.Recognizer(); 
        auth = json.load(open('bingauth.json'))
        log.info('Hark is processing the file') 
        hark_client.wait() 
        data = hark_client.getResults() 
        log.info('Hark processing complete') 
        log.info(str(data['context'])) 
        if data['context']: 
            for entry in data['context']: 
 
                utterance = 'Inaudible' 
                file_name = UPLOAD_PATH + 'part' + str(entry['srcID']) + '.flac' 
                log.info('Creating separated audio file handle %s', file_name) 
                with open(file_name, 'w') as write_handle: 
                    hark_client.getSeparatedAudio(handle=write_handle,  
                                                 srcID=entry['srcID']) 
                log.info('Retrieved and saved separated audio %d from hark', entry['srcID']) 
                with speech_recognition.AudioFile(path.join(path.dirname( 
                    path.realpath(__file__)), file_name)) as source: 
                    audio = speech_client.record(source) 
                log.info('Sending separated audio file to speech api') 
 
                try: 
                    utterance = speech_client.recognize_bing(audio,  
                        key=str(auth['apikey']),  
                        language=LANGUAGE) 
                    log.info('Transcription for part %d: %s', entry['srcID'], utterance) 
                # Thrown if utterance cannot be translated to text. 
                # It is acceptable to pass this exception and proceed. 
                except speech_recognition.UnknownValueError: 
                    log.info('Transcription unavailable for %d', entry['srcID']) 
                    pass 
                remove(file_name) 
                log.info('Removed separated audio file %s', file_name)
                self.write_message(utterance) 
                #create new ioloop instance to intermittently publish data 
                #ioloop.IOLoop.instance().add_timeout(timedelta(seconds=1), self.send_data) 


# Helper functions 
def allowed_file(file_name): 
    extension = file_name.rsplit('.', 1)[1] 
    return '.' in file_name and extension in ALLOWED_EXTENSIONS 
 
if __name__ == '__main__': 
 
 
    log.info('Initializing third-party clients') 
    hark_saas = HarkSaas() 
    hark_client = hark_saas.client() 
    log.info('Initializing web application') 
    application = web.Application([ 
        (r'/', HttpRequestHandler), 
        (r'/websocket', WebSocketHandler), 
        (r'/(apple-touch-icon\.png)', web.StaticFileHandler, 
            dict(path=settings['static_path'])), 
        ], **settings) 
    application.listen(LISTEN_PORT) 
    ioloop.IOLoop.instance().start() 

