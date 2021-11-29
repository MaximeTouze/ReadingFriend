
// TEST
// Traitement

  reload();


  function reload(){
  	// Event codes
          var MSG_SEND = 5;
          var MSG_SEND_EMPTY = 6;
          var MSG_SEND_EOS = 7;
          var MSG_WEB_SOCKET = 8;
          var MSG_WEB_SOCKET_OPEN = 9;
          var MSG_WEB_SOCKET_CLOSE = 10;
          var MSG_STOP = 11;
          var MSG_SERVER_CHANGED = 12;
  	var wsServerStatus = new WebSocket("ws://lst-demo.univ-lemans.fr:8889/client/ws/status");
  	wsServerStatus.onmessage = function(evt) {
  		     var elem=document.getElementById("num_workers");
  		     var num = JSON.parse(evt.data).num_workers_available;
  		     elem.innerHTML = "Nb workers dispo : "+num;
           console.log("Nb workers dispo : "+num);
  		     if(num>0){
  			        readNext();
  		     }
          };
          wsServerStatus.onerror = function (e) {
        		var elem=document.getElementById("num_workers");
        		elem.innerHTML = "Nb workers dispo : ERROR";
            console.error("erreur lors du contact du status", e);
          }



  	 var wsServerStatusSynth = new WebSocket("ws://lst-demo.univ-lemans.fr:8081/client/ws/status");

           wsServerStatusSynth.onmessage = function(evt) {
                       numWS = JSON.parse(evt.data).num_workers_available;
                       var elem=document.getElementById("num_workers_synth");
                         elem.innerHTML="Nb workers synth dispos : "+numWS;

          }
          wsServerStatus.onerror = function (e) {

            var elem=document.getElementById("num_workers_synth");
              elem.innerHTML="Nb workers synth dispos : ERROR";
            console.error("erreur lors du contact du status de la synthèse", e);
          }

  	currentAudioPlaying=0;
  	nbRunningSpeech=0;
  	timeoutCheck = setInterval(checkAudio, 200);

  	tabSources=[];
          tabDuration=[];

          ctxs = [];
          sources = [];

  	attenteSynth=[];
  	currSynth=0;
  	synthEnCours=0;

  	timeoutCheckSynth = setInterval(checkSynth, 200);


  	currentTrad = -1;
  	tabTrad=[];
  	lastPrintTrad=-1;

  	timeoutCheckSynth = setInterval(checkQna, 200);

  	filesConte=[];
  	nbFilesConte = 0;
  	currentConte=0;
  }
