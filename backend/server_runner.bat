@ECHO OFF
cd C:/Users/chama/Desktop/maw 
venv\scripts\activate && cd src/backend/maw && waitress-serve --listen=127.0.0.1:8000 --threads=10 maw.wsgi:application