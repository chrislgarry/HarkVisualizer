## Hark Visualizer
A web app written with the Tornado framework for visualizing audio. The web app only processes 8-channel flac and wav files (for the time being) to detect direction of sound, duration of sounds, and a transcription using speech recognition. Try it out using the test.wav file. It **only supports Japanese at the moment**.

[Read more](https://github.com/chrislgarry/HarkVisualizer/wiki)

## Thirdy-Party Services

### [Amazon AWS](http://aws.amazon.com/)
Used for hosting the web server in Japan.

### [Tornado](http://www.tornadoweb.org/en/stable/)
Used as the web server for serving the webapp and delivering data to the browser via websockets.

### [Microsoft Cognitive Services/Azure](https://www.microsoft.com/cognitive-services/en-us/speech-api)
Used for hosting the Bing Speech API server instance.

### [Hark SaaS](https://api.hark.jp/docs/en/)
Used for analyzing the audio files.

### [Speech Recognition](https://github.com/Uberi/speech_recognition/)
Used for transcribing the audio file via a wrapper around the Bing Speech API, as Google Speech API is not available anymore.

### [d3.js](https://d3js.org/)
Used for creating real-time data visualizations in the browser.

### [crossfilter.js](http://square.github.io/crossfilter/)
Used for n-dimensional filtering of multivariate datasets across D3 charts.

### [c3.js](http://c3js.org/)
A wrapper around D3.js for building charts quickly.
