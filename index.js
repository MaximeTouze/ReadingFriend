
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
