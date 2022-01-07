# ReadingFriend
Projet de M2

# Installation
pip install -r requirements.txt

# Lancement du serveur flask
1. Se placer dans le dossier contenant le fichier server.py situé à ReadingFriend/app/
2. export FLASK_APP=server.py
3. flask run
4. Se connecter au site à l'adresse 127.0.0.1:5000 (ou le port indiqué si celui-ci ne fonctionne pas)

# Rediriger le localhost de la machine compagnon@lecturefriend sur sa machine
ssh -NL 8080:localhost:5000 compagnon@lecturefriend
Se connecter au site à l'adresse 127.0.0.1:8080 (utiliser le port spécifié dans la commande)

# sudo apt-get install libcairo2-dev libjpeg-dev libgif-dev
