// Taille du buffer
const AUDIO_BUFFER_SIZE = 1000;

// ref du micro
var microphone = null;
var bufferSize = 2048;

// Stereo ou non
var numberOfInputChannels = 1;
var numberOfOutputChannels = 1;
// Buffer Audio
var recordedAudio = [];
var microOn = false;

askUserAgreementForMicrophone();




//
// Ask the user for the permission to listen the microphone
//
function askUserAgreementForMicrophone() {
  navigator.getUserMedia = navigator.mediaDevices.getUserMedia ||
     navigator.webkitGetUserMedia ||
     navigator.mozGetUserMedia ||
     navigator.msGetUserMedia;
  navigator.getUserMedia(
  {
     audio: true
  },
  userAgreementAuthorized,
  userAgreementRefused);
}

function userAgreementRefused(error) {
    window.alert("Warning, You refused the microphone usage for this website, it may not works.");
     console.error(error);
}

function userAgreementAuthorized(micro) {
console.log("Utilisation du micro autorisée", micro);
  microphone = micro;
  microOn = true;
  init_inputBuffer(micro);
}

//
// Read functions ::
//
function init_inputBuffer(micro) {
   // creates the audio context
   window.AudioContext = window.AudioContext || window.webkitAudioContext;
   context = new AudioContext();

   // creates an audio node from the microphone incoming stream
   mediaStream = context.createMediaStreamSource(micro);
   // https://developer.mozilla.org/en-US/docs/Web/API/AudioContext/createScriptProcessor
   if (context.createScriptProcessor) {
   recorder = context.createScriptProcessor(bufferSize, numberOfInputChannels, numberOfOutputChannels);
   } else {
   recorder = context.createJavaScriptNode(bufferSize, numberOfInputChannels, numberOfOutputChannels);
   }
   recorder.onaudioprocess = function (micro) { // Pour pas que le buffer ne soit trop gros
      recordedAudio.push(new Float32Array(micro.inputBuffer.getChannelData(0)));
      if(recordedAudio.length > AUDIO_BUFFER_SIZE){
        recordedAudio.shift();
      }
      console.log("on audio progress");
   }
   // we connect the recorder with the input stream
   mediaStream.connect(recorder);
   recorder.connect(context.destination);
}




// Ref :: https://www.softfluent.fr/blog/enregistrer-du-son-via-le-microphone-en-javascript/
