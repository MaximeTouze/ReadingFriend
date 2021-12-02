const LIEN_ASR = "ws://lst-demo.univ-lemans.fr:8888/client/ws/speech";

const START_MESSAGE = "Hey ready";
const END_MESSAGE = "please"


function changeLienASR(url){
	LIEN_ASR = url;
}

function envoyer(arrayBuffer){
	console.log("Envoi à l'ASR");
	var contentType = "content-type=audio/x-raw, layout=(string)interleaved, rate=(int)%d, format=(string)S16LE, channels=(int)1";
        var url = LIEN_ASR+"?"+contentType;
        ws = new WebSocket(url);

	var partial_trs=document.getElementsByName("partial_trs")[0];
	var corps=document.getElementsByName("corps")[0];
        ws.onmessage = function(e) {
								console.log('message', e);
                var data = e.data;
              	console.log('data', data);
                if (data instanceof Object && ! (data instanceof Blob)) {
                        console.log('WebSocket: onEvent: got Object that is not a Blob');
                } else if (data instanceof Blob) {
                        console.log('WebSocket: got Blob');
                } else {
                        var res = JSON.parse(data);
                        if (res.status == 0) {
                                if (res.result) {
                                        if (res.result.final) {
                                                //console.log(res.result.hypotheses);
						for(h=0; h<res.result.hypotheses.length; h++){
							trs = res.result.hypotheses[h].transcript;
							trs = trs.replace("<unk>", "");
							trs = trs.replace("ten the page", "turn the page");
							corps.innerHTML += "<div>"+trs+"</div><br/>";
							corps.scrollTop = corps.scrollHeight;
							//trad(trs);
						}
                                        } else {
						for(h=0; h<res.result.hypotheses.length; h++){
                                                	trs = res.result.hypotheses[h].transcript;
                                                        partial_trs.innerHTML = trs;
						}
						//partial_trs.innerHTML = res.result.hypotheses;
                                                //console.log(res.result.hypotheses);
                                        }
                                }
                        } else {
                                console.log('Server error: ' + res.status );
                        }
                }
        }

	// Start recording only if the socket becomes open
        ws.onopen = function(e) {
                // Start recording
                console.log("La faut envoyer l'audio ...");
		rate = 32000;
		size = arrayBuffer.byteLength;
		nbPa = Math.ceil(size/rate);
		console.log('bufferSize', size);
		console.log('nbPa', nbPa);
		if(nbPa >= 1){
			vue = new Uint8Array(arrayBuffer);
			i=0;
			timeoutvar = setInterval(envoiData, 400);
		}
		ws.send(arrayBuffer);
		console.log("Message envoyé");
	};

  	ws.onclose = function(e) {
                var code = e.code;
                var reason = e.reason;
                var wasClean = e.wasClean;
                // The server closes the connection (only?)
                // when its endpointer triggers.
								console.log(e);
                console.log('ws close : ', e.code + "/" + e.reason + "/" + e.wasClean);
        };

        ws.onerror = function(e) {
                var data = e.data;
                console.log('error', data);
        }
}




// Modifications pour le suivi de mots et l'avancée de la synth ?
  function checkAudio(){
  	if(microOn){
  		//var i = currentAudioPlaying;
  		//if(ctxs[i].state == "suspended" || ctxs[i].state == "closed"){
  			//demarrer l'audio
  			//ctxs[i].resume();
  			//muteUnmuteSynth();
  			//tabSources[i].start();
				//console.warn("called start");
  			//selectionner texte
  			// if(i>0){
  			//     prev = i-1;
  			//     elem = document.getElementsByName(prev)[0];
        //                       elem.setAttribute("style", "color:#202020");
  			// }
  			//elem = document.getElementsByName(i)[0];
  			//elem.setAttribute("style", "color:#AA1111");
  			//console.log(elem);
  		// }else{
  		// 	//audio termine ?
  		// 	duration = tabDuration[i];
  		// 	if(ctxs[i].currentTime >= duration){
  		// 		tabSources[i].stop();
  		// 		currentAudioPlaying++;
  		// 		checkAudio();
  		// 	}
  		//}
  	}
  }


	function envoiData(){
		//console.log(i);
		if(i<nbPa){
			if(i*rate<size){
				length=rate;
			}else{
				length=size-(i*rate);
			}
			var toSend = new Int8Array(length);
			for(j=i*rate,t=0; j<i*rate+length; j++, t++){
				toSend[t]=vue[j];
			}
			i++;
			ws.send(toSend);
			if (i==1){
				var sound = document.getElementById('sound');
				sound.controls = false;
	    			sound.play();
			}
		}else{
			clearInterval(timeoutvar);
		}
	}


// returns the question: without the beginning and the end tokens
	function getQuote (text) {


		const start_index = getStartIndex(text);
		const end_index = getEndIndex(text);

		return text.substring(start_index, end_index);

	}

	function hasQuote (text) {
		return (getStartIndex(text) !== -1 && getEndIndex(text) !== -1);  
	}

// methode adaptable
	function getStartIndex (text) {
		// On décale le début du texe à apres le message de début. on enleve aussi l espace
		return text.lastIndexOf(START_MESSAGE) + START_MESSAGE.length + 1;
	}
// méthode adaptable
function getEndIndex (text) {
	// le message se finit avant l'espace placé devant le message de fin
	return text.lastIndexOf(END_MESSAGE) -1;
}

console.log(getQuote("testtttt" + START_MESSAGE + " what's the Sherlock Holmes Story " + END_MESSAGE + "Tesssssstttt"));
