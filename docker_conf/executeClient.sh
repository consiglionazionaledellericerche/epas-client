#!/bin/bash

# Scaricamento file da locale/ftp/sftp e inserimento nel database
echo "=== " `date +'%Y/%m/%d %H:%M:%S'` "==="
# Posiziona sulla directory dove si trova questa procedura
cd `dirname $0`
# nell'immagine python:3-slim il python e' in /usr/local/bin
PATH=$PATH:/usr/local/bin

echo "===" Esecuzione del client python per l''invio delle timbrature a epas
# Avvia il client python scaricare le timbrature da file locali/ftp/sftp, 
# effettua il parsing dei file e invia le timbrature al server di ePas.
python epas_client/client.py
exit $?