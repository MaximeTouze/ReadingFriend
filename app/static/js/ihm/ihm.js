var microphone = null;
var bufferSize = 2048;
var numberOfInputChannels = 1;
var numberOfOutputChannels = 1;

askUserAgreementForMicrophone();




//
// Ask the user for the permission to listen the microphone
//
function askUserAgreementForMicrophone() {
  navigator.getUserMedia = navigator.getUserMedia ||
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
     console.error(error);
}

function userAgreementAuthorized(micro) {
  microphone = micro;
  init_inputBuffer();
  console.log("autorisé maggle", micro);
}

//
// Read functions ::
//
function init_inputBuffer() {
  navigator.getUserMedia({ audio: true },
  function (e) {
   // creates the audio context
   window.AudioContext = window.AudioContext || window.webkitAudioContext;
   context = new AudioContext();

   // creates an audio node from the microphone incoming stream
   mediaStream = context.createMediaStreamSource(e);
   // https://developer.mozilla.org/en-US/docs/Web/API/AudioContext/createScriptProcessor
   if (context.createScriptProcessor) {
   recorder = context.createScriptProcessor(bufferSize, numberOfInputChannels, numberOfOutputChannels);
   } else {
   recorder = context.createJavaScriptNode(bufferSize, numberOfInputChannels, numberOfOutputChannels);
   }
   recorder.onaudioprocess = function (e) {
   console.log("on audio progress");
   }
   // we connect the recorder with the input stream
   mediaStream.connect(recorder);
   recorder.connect(context.destination);
  }
}




// Ref :: https://www.softfluent.fr/blog/enregistrer-du-son-via-le-microphone-en-javascript/
