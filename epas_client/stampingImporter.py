#!/usr/bin/python3
# -*- coding: utf-8 -*-

###############################################################################
#         Copyright (C) 2020  Consiglio Nazionale delle Ricerche              #
#                                                                             #
#   This program is free software: you can redistribute it and/or modify      #
#   it under the terms of the GNU Affero General Public License as            #
#   published by the Free Software Foundation, either version 3 of the        #
#   License, or (at your option) any later version.                           #
#                                                                             #
#   This program is distributed in the hope that it will be useful,           #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#   GNU Affero General Public License for more details.                       #
#                                                                             #
#   You should have received a copy of the GNU Affero General Public License  #
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.    #
#                                                                             #
###############################################################################

###############################################################################
# File: stampingImporter.py                                                   #
# Description: classe per effettuare il parsing di un file con le timbrature  #
# ed inviarlo all'applicazione "Epas".                                        #
#                                                                             #
# Author: Cristian Lucchesi <cristian.lucchesi@iit.cnr.it>                    #
# Last Modified: 2020-11-17 19:32                                             #
#                                                                             #
# La REGEX_STAMPING rappresenta il formato della timbratura                   #
#                                                                             #
# es.                                                                         #
#                                                                             #
# E/U                                                                         #
# |Tipo                                                                       #
# ||g.sett                                                                    #
# |||num. badge                                                               #
# ||||        causale                                                         #
# ||||        |   ora                                                         #
# ||||        |   | minuti                                                    #
# ||||        |   | | secondi                                                 #
# ||||        |   | | | giorno                                                #
# ||||        |   | | | | mese                                                #
# ||||        |   | | | | | anno                                              #
# ||||        |   | | | | | | id                                              #
# ||||        |   | | | | | | |                                               #
# E11000092852000015271417011100                                              #
# U11000025542000015103317011100                                              #
#                                                                             #
#                                                                             #
# Senso Tipo g.sett Num.badge Causale Ore Min Sec Giorno Mese Anno Id         #
# S      T     D    BBBBBBBBB  CCCC   HH  MM  SS   dd     mm   yy  II         #
#                                                                             #
# Senso                                                                       #
# 0 Transito nullo                                                            #
# E Transito in entrata                                                       #
# U Transito in uscita                                                        #
# T Transito per accesso                                                      #
#                                                                             #
# Tipo                                                                        #
# 1 Transito locale di presenze / accessi                                     #
# 2 Transito accessi remoto                                                   #
# 3 Transito rifiutato dal controllo accessi                                  #
# 4 Transito con causale numerica                                             #
# 5 Transito con causale menu a tendina                                       #
# 6                                                                           #
# 7 Consumo mensa                                                             #
# 8 Non usato                                                                 #
# 9 Transito inserito da seriale                                              #
# A                                                                           #
# B Transito virtuale trasmesso al terminale                                  #
# C Transito di prenotazione mensa                                            #
#                                                                             #
# Giorno settimana                                                            #
# 0 Domenica                                                                  #
# 1 Lunedi                                                                    #
# 2 ....                                                                      #
#                                                                             #
# badge numero badge a 9 cifre giustificato a destra                          #
#                                                                             #
###############################################################################

import logging
import re
from queue import Queue, Empty
from threading import Thread

from config import MAPPING_CAUSALI_CLIENT_SERVER, OFFSET_ANNO_BADGE, \
    MAX_THREADS, SERVER_ERROR_CODES, REGEX_STAMPING, \
    MAPPING_OPERAZIONE_CLIENT_SERVER

from stamping import Stamping
from stampingSender import sendStamping

# ATTENZIONE: formato della timbratura impostato in configurazione.
stampingRegex = re.compile(REGEX_STAMPING)

from metrics import BAD_STAMPINGS, PARSING_ERRORS, STAMPINGS_SENT

class StampingParsingException(Exception):
    """
    Eccezione sollevata nel caso di timbrature non interpretabili
    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class SendWorker(Thread):
    def __init__(self, queue, badStampings, parsingErrors):
        Thread.__init__(self)
        self.queue = queue
        self.badStampings = badStampings
        self.parsingErrors = parsingErrors

    def run(self):
        while not self.queue.empty():
            # Get the work from the queue
            try:
                line = self.queue.get_nowait()
                stamp = None
            except Empty:
                self.queue.task_done()
                return

            try:
                stamp = StampingImporter._parseLine(line)
            except StampingParsingException as e:
                logging.debug(e)
                self.parsingErrors.append(line)
                self.queue.task_done()
                continue
            
            if stamp is not None:
                if stamp.isToBeIgnored():
                    logging.info("Ignorata timbratura line = %s. Timbratura = %s", line, stamp)
                else:
                    try:

                        response = sendStamping(stamp)

                        if response is None:  # Caso di errore di connessione al server
                            logging.debug("Timbratura non inserita in ePas: %s", line)
                            self.badStampings.append(line)
                        elif response.status_code in SERVER_ERROR_CODES:  # Risposta del server con un errore
                            logging.warning("Errore nell'invio della timbratura %s al server di ePas: %s %s",
                                            line, response.status_code, response.reason)
                            self.badStampings.append(line)
                        else:  # Invio OK
                            logging.debug("Timbratura inserita correttamente in ePas:  %s", line)
                    except Exception as e:
                        logging.error("Eccezione nell'invio delle timbratura line = %s. " + 
                                      "Timbratura = %s. Inserita nelle badStampings. Eccezione = %s", line, stamp, e)
                        self.badStampings.append(line)                        
            self.queue.task_done()


class StampingImporter:
    """
    Processa i file contenenti le timbrature e le invia al sistema di gestione 
    delle presenze Epas
    """

    @staticmethod
    def sendStampingsOnEpas(stampings):
        """
        @param stampings: lista delle righe prelevate dal file delle timbrature
        @return una tupla contenente come primo valore la lista delle timbrature da re-inviare
            ad ePAS e come secondo elemento la lista degli errori di parsing.
            
        Data la lista delle righe contenenti le timbrature effettuate via Badge, 
        effettua il parsing ed invia le informazioni della timbratura via Restful
        al sistema Epas.
        """

        # Righe di timbrature che non è stato possibile inviare correttamente
        bad_stampings = []
        # Tracciati record che hanno causato un errore nel parsing
        parsing_errors = []

        queue = Queue()

        # Vengono inserite tutte le righe corrispondenti al tracciato record delle timbrature nella coda
        for stamping in stampings:
            queue.put(stamping)

        # Crea n thread
        for x in range(MAX_THREADS):
            worker = SendWorker(queue, bad_stampings, parsing_errors)
            logging.debug(f"Avviato thread {x} per l'invio delle timbrature")
            # Setting daemon to True will let the main thread exit even though the workers are blocking
            worker.daemon = True
            worker.start()

        queue.join()
        
        #Impostazione delle metriche Prometheus
        STAMPINGS_SENT.set(len(stampings))
        BAD_STAMPINGS.set(bad_stampings)
        PARSING_ERRORS.set(parsing_errors)
        
        return bad_stampings, parsing_errors

    @staticmethod
    def _parseLine(line):
        """
        Parsa una riga contenente le informazioni relativa ad una timbratura,
        i dati estratti vengono inseriti in un'istanza della classe Stamping
        che viene restituita dal metodo.
        Nel caso di errori durante il parsing viene sollevata una eccezione
        StampingParsingException.
        """
        logging.debug("Parso la riga %s", line)

        matchObject = stampingRegex.search(line.strip())

        if matchObject is None:
            raise StampingParsingException(
                'Errore nel formato della riga da parsare! Riga scartata: %s' % (line,))

        stamping = Stamping()
        stamping.operazione = matchObject.group("operazione")
        stamping.matricolaFirma = matchObject.group("matricolaFirma")
        stamping.ora = matchObject.group("ora")
        stamping.minuti = matchObject.group("minuti")
        stamping.giorno = matchObject.group("giorno")
        stamping.mese = matchObject.group("mese")
        stamping.anno = matchObject.group("anno")

        try:
            stamping.tipo = matchObject.group("tipo")
        except IndexError:
            logging.debug("tipo non presente per timbratura %s", line)
        
        try:
            stamping.giornoSettimana = matchObject.group("giornoSettimana")
        except IndexError:
            logging.debug("Giorno delle settimana non presente per timbratura %s", line)

        try:
            stamping.causale = matchObject.group("causale")
            if stamping.causale and stamping.causale in MAPPING_CAUSALI_CLIENT_SERVER:
                stamping.causale = MAPPING_CAUSALI_CLIENT_SERVER[stamping.causale]
            else:
                logging.warn("Causale %s sconosciuta. Impostata causale vuota" % stamping.causale)
                stamping.causale = None
        except IndexError:
            logging.debug("causale non presente per timbratura %s", line)

        try:
            stamping.secondi = matchObject.group("secondi")
            stamping.secondi = int(stamping.secondi)
        except IndexError:
            stamping.secondi = 0
            logging.debug("secondi non presenti per timbratura %s", line)

        try:
            stamping.lettore = matchObject.group("lettore")
        except IndexError:
            logging.debug("lettore non presente per timbratura %s", line)

        if stamping.operazione and stamping.operazione in MAPPING_OPERAZIONE_CLIENT_SERVER:
            stamping.operazione = MAPPING_OPERAZIONE_CLIENT_SERVER[stamping.operazione]

        try:
            stamping.anno = int(stamping.anno) + OFFSET_ANNO_BADGE
            stamping.mese = int(stamping.mese)
            stamping.giorno = int(stamping.giorno)
            stamping.ora = int(stamping.ora)
            stamping.minuti = int(stamping.minuti)

        except ValueError:
            raise StampingParsingException(
                "Errore nel formato della riga da parsare. Riga = %s." %(line,))

        if not stamping.isValid():
            raise StampingParsingException(
                "Riga di timbratura %s non valida" %(line,))

        return stamping


if __name__ == "__main__":
    logging.basicConfig(
        filename='client.log',
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)

    stampingImporter = StampingImporter()
    line = "E11000092852000008341404011100"
    stamping = stampingImporter._parseLine(line)
    print(stamping)
