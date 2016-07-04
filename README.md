# Hark Visualizer
A web app written with the Tornado framework for visualizing audio. The web app processes 8-channel flac and wav files to detect direction of sound, duration of sounds, and a transcription using speech recognition.

# Specifications
## Internal Specifications
###Placeholder
## External Specifications
###Placeholder

# Thirdy-Party Services

##[Tornado](http://www.tornadoweb.org/en/stable/)
Used as the webserver for hosting the webapp and delivering data to the browser via websockets.

##[Hark SaaS](https://api.hark.jp/docs/en/)
Used for analyzing the audio files.

##[Speech Recognition](https://github.com/Uberi/speech_recognition/)
Used for transcribing the audio file via a wrapper around the Bing Speech API, as Google Speech API is not available anymore.

##[Microsoft Cognitive Services](https://www.microsoft.com/cognitive-services/en-us/speech-api)
Used for hosting the Bing Speech API server instance.

##[d3.js](https://d3js.org/)
Used for creating visualizations.

##[crossfilter.js](http://square.github.io/crossfilter/)
Used for n-dimensional filtering of multivariate datasets across D3 charts.

##[c3.js](http://c3js.org/)
A wrapper around D3.js for building charts quickly.
