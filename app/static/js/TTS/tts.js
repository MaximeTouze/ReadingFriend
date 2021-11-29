
LIENS_TTS = ["ws://lst-demo.univ-lemans.fr:8081/client/ws/synth"];
LIEN_TTS = LIENS_TTS[0];

var numWS=0;
var tabGain=[];


// Méthodes :
// change le lien pour la TTS (si besoin de changer de langue par exemple)
function changeLienTTS(url)
{
    LIEN_TTS = url;
}

function synthese(texte)
{
    if(numWS>0)
    {
    	synthEnCours=1;
    	console.log("Worker syntheses ok ...");
    	var contentType = "content-type=audio/x-raw, layout=(string)interleaved, rate=(int)%d, format=(string)S16LE, channels=(int)1";
		var url = LIEN_TTS+"?"+contentType;
		wsSynth = new WebSocket(url);
		myconvstring="";

		wsSynth.onmessage = function(e)
        {
			var data = e.data;
			var res = JSON.parse(data);

			if(res.data)
            {
				if(res.data == "EOS")
                {
					var audioCtx = new (window.AudioContext || window.webkitAudioContext)();
					var source = audioCtx.createBufferSource();
                    // .suspend()
      			    audioCtx.resume();
					ctxs.push(audioCtx);
					var byteNumbers = new Array(myconvstring.length);

					for (var i = 0; i < myconvstring.length; i++)
                    {
					    byteNumbers[i] = myconvstring.charCodeAt(i);
					}

					mybuffer = new Uint8Array(byteNumbers).buffer;
					synthEnCours=0;

					audioCtx.decodeAudioData(mybuffer,
                    function(buffer)
                    {
						source.buffer = buffer;
						totDuration = source.buffer.duration;
						var gainNode = audioCtx.createGain();
						gainNode.connect(audioCtx.destination);
						source.connect(gainNode);
						//source.connect(audioCtx.destination);
						tabGain.push(gainNode);
						tabSources.push(source);
						tabDuration.push(totDuration);
						nbRunningSpeech++;
						console.log("Synthese prete :"+texte);

						//source.start(audioCtx.currentTime+offset,0,totDuration);
						source.start();
					},
                    function(e)
                    {
                        console.log("Error with decoding audio data" + e.err);
                    });

					myconvstring="";
					audioCtx.onstatechange =
                    function()
                    {
						console.log("SATE CHANGED:"+audioCtx.state);
					}
				}
                else
                {
					data = atob(res.data);
					myconvstring += data;
				}
			}
            else
            {
				console.log(res);
			}
		}

		// Start recording only if the socket becomes open
		wsSynth.onopen = function(e)
        {
			// Start recording
			var msg =
            {
				type: "message",
				text: texte,
			};
            console.log(url);
            console.log(wsSynth);
			wsSynth.send(JSON.stringify(msg));
		};

		wsSynth.onclose = function(e)
        {

		};

    	wsSynth.onerror = function(e)
        {
    		var data = e.data;
    		console.log(data);
    	}
    }
    else
    {
        console.log("pas de worker synthese dispo ...");
    }
}


function checkSynth()
{
	if(synthEnCours == 0 && numWS > 0 && attenteSynth.length > currSynth)
    {
		console.log("GO SYNTH "+attenteSynth[currSynth]);
		synthese(attenteSynth[currSynth]);
		currSynth++;
	}
	else if(attenteSynth.length > currSynth)
    {
		console.log("(synth) HAVE TO WAIT ...");
	}
}
