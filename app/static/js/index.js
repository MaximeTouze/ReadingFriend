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

function getAsrPart () {
  return document.getElementById('ASR-part');
}

function getQnaPart () {
  return document.getElementById('QNA-part');
}
