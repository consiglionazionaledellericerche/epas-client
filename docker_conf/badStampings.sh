#!/bin/bash

echo "=== " `date +'%Y/%m/%d %H:%M:%S'` "==="
# Posiziona sulla directory dove si trova questa procedura
cd `dirname $0`

echo "===" Esecuzione del client python per l''invio delle timbrature a ePAS
# Avvia il client python per inviare le timbrature "bad", che non sono state
# inviate precedentemente al server di ePas.
python epas_client/client.py -b
exit $?