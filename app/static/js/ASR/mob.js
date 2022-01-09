// Global UI elements:
//  - log: event log
//  - trans: transcription window

// Global objects:
//  - isConnected: true iff we are connected to a worker
//  - tt: simple structure for managing the list of hypotheses
//  - dictate: dictate object with control methods 'init', 'startListening', ...
//       and event callbacks onResults, onError, ...
var isConnected = false;

var tt = new Transcription();

var startPosition = 0;
var endPosition = 0;
var doUpper = false;
var doPrependSpace = true;

function capitaliseFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

function prettyfyHyp(text, doCapFirst, doPrependSpace) {
	if (doCapFirst) {
		text = capitaliseFirstLetter(text);
	}
	tokens = text.split(" ");
	text = "";
	if (doPrependSpace) {
		text = " ";
	}
	doCapitalizeNext = false;
	tokens.map(function(token) {
		if (text.trim().length > 0) {
			text = text + " ";
		}
		if (doCapitalizeNext) {
			text = text + capitaliseFirstLetter(token);
		} else {
			text = text + token;
		}
		if (token == "." ||  /\n$/.test(token)) {
			doCapitalizeNext = true;
		} else {
			doCapitalizeNext = false;
		}
	});

	text = text.replace(/ ([,.!?:;])/g,  "\$1");
	text = text.replace(/ ?\n ?/g,  "\n");
	return text;
}


var dictate = new Dictate({
		server : $("#servers").val().split('|')[0],
		serverStatus : $("#servers").val().split('|')[1],
		recorderWorkerPath : '../lib/recorderWorker.js',
		onReadyForSpeech : function() {
			isConnected = true;
			__message("READY FOR SPEECH");
			$("#buttonToggleListening").html('Mute');
			$("#buttonToggleListening").addClass('highlight');
			$("#buttonToggleListening").prop("disabled", false);
			$("#buttonCancel").prop("disabled", false);
			startPosition = $("#trans").prop("selectionStart");
			endPosition = startPosition;
			var textBeforeCaret = $("#trans").val().slice(0, startPosition);
			if ((textBeforeCaret.length == 0) || /\. *$/.test(textBeforeCaret) ||  /\n *$/.test(textBeforeCaret)) {
				doUpper = true;
			} else {
				doUpper = false;
			}
			doPrependSpace = (textBeforeCaret.length > 0) && !(/\n *$/.test(textBeforeCaret));
		},
		onEndOfSpeech : function() {
			__message("END OF SPEECH");

			$("#buttonToggleListening").html('Muting...');
			$("#buttonToggleListening").prop("disabled", true);
		},
		onEndOfSession : function() {
			isConnected = false;
			__message("END OF SESSION");
			$("#buttonToggleListening").html('Unmute');
			$("#buttonToggleListening").removeClass('highlight');
			$("#buttonToggleListening").prop("disabled", false);
			$("#buttonCancel").prop("disabled", true);
		},
		onServerStatus : function(json) {
			__serverStatus(json.num_workers_available);
			$("#serverStatusBar").toggleClass("highlight", json.num_workers_available == 0);
			// If there are no workers and we are currently not connected
			// then disable the Start/Stop button.
			if (json.num_workers_available == 0 && ! isConnected) {
				$("#buttonToggleListening").prop("disabled", true);
			} else {
				$("#buttonToggleListening").prop("disabled", false);
			}
		},
		onPartialResults : function(hypos) {
      console.warn("n'a ça mébon", hypos[0].transcript);
      if(hasQuote(hypos[0].transcript)) {
        quote = getQuote(hypos[0].transcript);
        clearTranscription();
        hypText = prettyfyHyp(quote, doUpper, doPrependSpace);
  			val = $("#trans").val();
  			$("#trans").val(/*val.slice(0, startPosition) +*/ hypText /*+ val.slice(endPosition)*/ + '?');
  			endPosition = startPosition + hypText.length;
  			$("#trans").prop("selectionStart", endPosition);
      }
		},
		onResults : function(hypos) {
      if(hasQuote(hypos[0].transcript)) {
        quote = getQuote(hypos[0].transcript);
        console.log(quote);
        clearTranscription();
  			hypText = prettyfyHyp(quote, doUpper, doPrependSpace);
  			val = $("#trans").val();
  			$("#trans").val(/*val.slice(0, startPosition) +*/ hypText /*+ val.slice(endPosition)*/ + '?');
  			startPosition = startPosition + hypText.length;
  			endPosition = startPosition;
  			$("#trans").prop("selectionStart", endPosition);
  			if (/\. *$/.test(hypText) ||  /\n *$/.test(hypText)) {
  				doUpper = true;
  			} else {
  				doUpper = false;
  			}
  			doPrependSpace = (hypText.length > 0) && !(/\n *$/.test(hypText));
      }
      console.log( "==================>>>>>>>", "TODO => brancher le qna");
		},
		onError : function(code, data) {
			dictate.cancel();
			__error(code, data);
			// TODO: show error in the GUI
		},
		onEvent : function(code, data) {
			__message(code, data);
		}
	});

// Private methods (called from the callbacks)
function __message(code, data) {
	console.log("msg: " + code + ": " + (data || ''));
}

function __error(code, data) {
	console.error("ERR: " + code + ": " + (data || '') + "\n" + log.innerHTML);
}

function __serverStatus(msg) {
	serverStatusBar.innerHTML = msg;
}

function __updateTranscript(text) {
	$("#trans").val(text);
}

// Public methods (called from the GUI)
function toggleListening() {
	if (isConnected) {
		dictate.stopListening();
	} else {
		dictate.startListening();
	}
}

function cancel() {
	dictate.cancel();
}

function clearTranscription() {
	$("#trans").val("");
	// needed, otherwise selectionStart will retain its old value
	$("#trans").prop("selectionStart", 0);
	$("#trans").prop("selectionEnd", 0);
}

$(document).ready(function() {
	dictate.init();

	$("#servers").change(function() {
		dictate.cancel();
		var servers = $("#servers").val().split('|');
		dictate.setServer(servers[0]);
		dictate.setServerStatus(servers[1]);
	});

});



const START_MESSAGE = ["Compagnon", "compagnon"];
const END_MESSAGE = ["Merci", "merci"];


// returns the question: without the beginning and the end tokens
	function getQuote (text) {
    console.log(text);
    if(hasQuote(text)){
  		const start_index = getStartIndex(text);
  		const end_index = getEndIndex(text);
      console.warn(text.substring(start_index + getLocQuoteStart(text, start_index), end_index-1));
  		return text.substring(getLocQuoteStart(text, start_index), end_index-1);
    }
	}

  // retourne l indice du début de la question
  function getLocQuoteStart(text, index) {
		for (message in START_MESSAGE){
      memory = text.lastIndexOf(START_MESSAGE[message]);
      if(memory !== -1 && memory == index) {
    		// On décale le début du texe à apres le message de début. on enleve aussi l espace
        return index + START_MESSAGE[message].length +1;
      }
    }
  }

  // retourne l indice du début de la question
  function getLocQuoteEnd(text, index) {
		for (message in END_MESSAGE){
      memory = text.lastIndexOf(END_MESSAGE[message]);
      if(memory !== -1 && memory == index) {
    		// On décale le début du texe à apres le message de début. on enleve aussi l espace
        return index -1;
      }
    }
  }

	function hasQuote (text) {
    console.error("quote test", text, getStartIndex(text) !== -1, getEndIndex(text) !== -1);
		return (getStartIndex(text) !== -1 && getEndIndex(text) !== -1);
	}

// methode adaptable
	function getStartIndex (text) {
    result = text.length;
		// On décale le début du texe à apres le message de début. on enleve aussi l espace
		for (message in START_MESSAGE){
      memory = text.lastIndexOf(START_MESSAGE[message]);
      if(memory !== -1 && memory < result) {
        result = memory;
      }
    }
    if(result !== text.length) {
      return result;
    }
    return -1;
	}

// méthode adaptable
function getEndIndex (text) {
	// le message se finit avant l'espace placé devant le message de fin
  result = -1;
  // On décale le début du texe à apres le message de début. on enleve aussi l espace
  for (message in END_MESSAGE){
    memory = text.lastIndexOf(END_MESSAGE[message]);
    console.log("msg", END_MESSAGE[message], "res", result, "memory", memory, "texte", text);
    if(memory !== -1 && memory > result) {
      result = memory;
    }
  }
  return result;
}
