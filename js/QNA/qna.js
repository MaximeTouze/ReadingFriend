const LIEN_QNA = "http://lst-demo.univ-lemans.fr:8083/translate";

function changeLienQNA(url){
  LIEN_QNA = url;
}

function trad(texte){
	console.log("TRAD "+texte);
	//texte = texte.replace(/'([^ ]+)/g, " '$1");
	//console.log("TRAD ENV : "+texte);
	currentTrad++;
	var numTrad=currentTrad;
	tabTrad.push("not ready");

	var tradarea=document.getElementsByName("trad")[0];
	var ajaxRequest; // The variable that makes Ajax possible!

	try{
		// Opera 8.0+, Firefox, Safari
		ajaxRequest = new XMLHttpRequest();
	} catch (e){
		// Internet Explorer Browsers
		try{
			ajaxRequest = new ActiveXObject("Msxml2.XMLHTTP");
		} catch (e) {
			try{
				ajaxRequest = new ActiveXObject("Microsoft.XMLHTTP");
			} catch (e){
				// Something went wrong
				alert("Your browser broke!");
				return false;
			}
		}
	}

	ajaxRequest.onreadystatechange = function(){
		if(ajaxRequest.readyState == 4){
			var res = JSON.parse(ajaxRequest.responseText);
			console.log("RESULT TRAD "+res.data.translations[0].translatedText)
			//tradarea.innerHTML += res.data.translations[0].translatedText+"\n";
			//attenteSynth.push(texte);
			//synthese( res.data.translations[0].translatedText);
			tabTrad[numTrad]=res.data.translations[0].translatedText;
		}
	}
	//var parameters="text="+texte;
	var url=LIEN_QNA + "?q="+encodeURIComponent(texte)+"&source=en&target=fr&key=bla";
	ajaxRequest.open("GET", url, true);
	ajaxRequest.send(null);
}
