//import * from "js/ASR/asr.js";
//import * from "js/QNA/qna.js";
//import * from "js/TTS/tts.js";


function changeASR (text) {
  asrPart = getAsrPart();
  asrPart.innerHTML = text;
}

function changeQNA (text) {
  qnaPart = getQnaPart();
  qnaPart.innerHTML = text;
}

// retourne l'element du DOM correspondant à la partie ASR
function getAsrPart () {
  return document.getElementById('ASR-part');
}

// retourne l'élément du DOM correspondant à la partie QNA
function getQnaPart () {
  return document.getElementById('answer');
}

function changeChamps() {
  getAsrPart().innerHTML = '<input type="text" style="width:175%; height: 200%"/>';
}
