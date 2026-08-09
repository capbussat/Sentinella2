# Sentinella 
Versió de Sentinella en Python amb Threads i Websockets.

sentinella.py s'executa en els ordinadors d'alumnes.
controller.py s'executa en l'ordinador dels profes.

Funcionen els threads, websockets i la GUI del controlador.
No s'executa, encara, cap de les restriccions des de Sentinella.

## Crea entorn virtual Python
python3 -m venv .venv

## Inicia l'entorn virtual
cd ~/Sentinella/sentinella  
source .env/bin/activate  

## Websockets
pip install websockets  
pip install ttkbootstrap  
pip install PyYAML  
