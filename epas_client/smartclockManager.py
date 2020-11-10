#!/usr/bin/python
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
# File: smartClockManager.py                                                  #
# Description: Preleva le timbrature da un badge tipo smartclock              #
#                                                                             #
# Author: Daniele Murgia <dmurgia85@gmail.com>                                #
# Author: Cristian Lucchesi <cristian.lucchesi@iit.cnr.it>                    #
# Last Modified: 2020-11-02 16:39                                             #
###############################################################################

###############################################################################
#                                                                             #
#  OPERAZIONE PER IL DOWNLOAD DELLE TIMBRATURE TRAMITE PROTOCOLLO FTP DAI     #
#  LETTORI SMARTCLOCK e CHECKPOINT II:                                        #
#                                                                             #
#    1. Connessione al lettore tramite protocollo FTP.                        #
#    2. Scrittura del file LTCOM.COM la riga contenente il comando            #
#       F4dd/MM/yy/HH/mm/ss (omettendo la data si scrivono tutte le           #
#       timbrature presenti nel file LTCOM.TRN)                               #
#    3. Controllo della corretta operazione sul file di log LTCOM.LOG         #
#       (T01Rx0000, il codice finale 0000 significa che l'operazione è andata #
#       a buon fine)                                                          #
#    4. Prelievo del file LTCOM.TRN contenente le timbrature filtrate in base #
#       al comando precedente                                                 #
#                                                                             #
###############################################################################

import logging
import os
import re
import time
from datetime import datetime, timedelta
from ftplib import FTP

from archive import Archive
from config import BADGE_READER_IP, BADGE_READER_PORT, BADGE_READER_USER, \
    BADGE_READER_PSW, DAYS_TO_DOWNLOAD, FTP_CONNECTION_TIMEOUT, WAIT_SECONDS, \
    STAMPING_FILTER_COMMAND, STAMPINGS_FILE, COMMAND_FILE, LOG_FILE, \
    F4_COMMAND_DATA_FORMAT, SUCCESS_MSG, DATA_DIR, BAD_STAMPINGS_FILE, \
    PARSING_ERROR_FILE

from config import BASE_DIR, STAMPINGS_FILE_FORMAT, STAMPINGS_DIR
from stampingImporter import StampingImporter
from fileUtils import FileUtils

class SmartClockManager:
    """
    Classe per il download del file contenente le timbrature dal lettore smartclock
    """

    def __init__(self):
        pass

    @staticmethod
    def downloadstampings():
        """
        :return: la timbratura più recente scaricata e la data relativa, se presenti
        """

        last_stamping, from_date = FileUtils.load_last_request()

        now = datetime.now()

        # Elimino nel caso esistano i file residui dall'esecuzione precedente
        command_file = os.path.join(BASE_DIR, COMMAND_FILE)
        if os.path.exists(command_file):
            os.remove(command_file)

        log_file = os.path.join(BASE_DIR, LOG_FILE)
        if os.path.exists(log_file):
            os.remove(log_file)

        stamping_file = os.path.join(BASE_DIR, STAMPINGS_FILE)
        if os.path.exists(stamping_file):
            os.remove(stamping_file)

        if from_date is not None:
            formatted_date = from_date.__format__(F4_COMMAND_DATA_FORMAT)
        else:
            # Richiedo gli ultimi n giorni di timbrature al lettore
            first_request_date = datetime.combine(now - timedelta(DAYS_TO_DOWNLOAD), now.time().min)
            formatted_date = first_request_date.__format__(F4_COMMAND_DATA_FORMAT)

        # Creazione file LTCOM.COM con il comando F4
        filter_command = "%s%s" % (STAMPING_FILTER_COMMAND, formatted_date)
        with open(command_file, 'w') as new_command_file:
            new_command_file.writelines("%s\r\n" % filter_command)

        logging.info('Tentativo di connessione al lettore %s tramite protocollo FTP', BADGE_READER_IP)

        ftp = None

        try:
            ftp = FTP()
            logging.debug(f"Tenativo di connessione al lettore {BADGE_READER_IP}:{BADGE_READER_PORT}" + 
                f"(connection timeout = {FTP_CONNECTION_TIMEOUT}) in corso...")
            ftp.connect(BADGE_READER_IP, int(BADGE_READER_PORT), FTP_CONNECTION_TIMEOUT)
            ftp.login(BADGE_READER_USER, BADGE_READER_PSW)

            logging.info("Connessione al lettore effettuata: %s" % ftp.welcome)

            clear_log = ftp.delete(LOG_FILE)
            logging.info('Ripuliti messaggi di log dal file %s: %s', LOG_FILE, clear_log)

            # INVIO COMANDO F4 AL LETTORE tramite il file LTCOM.COM
            send_com = ftp.storbinary('STOR %s' % COMMAND_FILE, open(command_file, 'rb'))
            logging.info("Inviato comando %s al lettore: %s", filter_command, send_com)

            # Attendo qualche secondo per essere sicuro che il lettore abbia elaborato il comando
            time.sleep(WAIT_SECONDS)
            log_size = ftp.size(LOG_FILE)

            # Se la dimensione differisce presumo che il lettore abbia loggato qualcosa relativamente al comando passato
            # e verifico che non ci siano errori
            if log_size == 0:
                logging.warning('Nessun messaggio di risposta trovato nel file %s. Nessuna timbratura scaricata',
                                LOG_FILE)
                return None, None

            # Download del file di log LTCOM.LOG
            ftp.retrbinary('RETR ' + LOG_FILE, open(log_file, 'wb+').write)

            # Leggo la prima riga contenente la risposta al comando inviato
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    first_line = f.readline().strip()

                response = re.search("Rx\d{4}", first_line).group()
                # Verifico che il messaggio del lettore sia quello di successo
                if response != SUCCESS_MSG:
                    logging.error("Risposta del lettore inattesa, nessuna timbratura scaricata: %s", response)
                    return None, None

                logging.info("Risposta del lettore al comando %s: %s", STAMPING_FILTER_COMMAND, response)

                # Eseguo il download del file LTCOM.TRN contenente le timbrature
                get_stamp = ftp.retrbinary('RETR ' + STAMPINGS_FILE, open(stamping_file, 'wb+').write)
                logging.info("File %s correttamente scaricato dal lettore: %s", STAMPINGS_FILE, get_stamp)
                with open(stamping_file, 'r') as f:
                    stampings_received = f.read().splitlines()  # Rimuovo l'ultima timbratura già ricevuta
                    if last_stamping in stampings_received:
                        stampings_received.remove(last_stamping)

                if len(stampings_received) > 0:
                    filename = now.__format__(STAMPINGS_FILE_FORMAT)
                    new_stampings_file = os.path.join(STAMPINGS_DIR, filename)
                    with open(new_stampings_file, 'w') as new_file:
                        for stamping in stampings_received:
                            new_file.write("%s\n" % (stamping,))
                    logging.info('Salvate %s timbrature nel file %s', len(stampings_received), filename)
                else:
                    logging.info('Nessuna nuova timbratura ricevuta.')
                    return None, None

                return Archive.archive_and_check_stampings(stampings_received)

        except Exception as e:
            logging.error("Errore durante il download delle timbrature: %s", e)

        finally:
            # chiudo la connessione ftp
            if ftp is not None and ftp.sock is not None:
                ftp.quit()

        return None, None

    @staticmethod
    def process_stamping_files():
        stamping_files = os.listdir(STAMPINGS_DIR)
        
        bad_stampings_path = os.path.join(DATA_DIR, BAD_STAMPINGS_FILE)
        parsing_errors_path = os.path.join(DATA_DIR, PARSING_ERROR_FILE)

        bad_stampings = []
        parsing_errors = []

        for stamping_file in stamping_files:
            logging.info("Processo il file %s per estrarne le timbrature", stamping_file)

            stamping_file_path = os.path.join(STAMPINGS_DIR, stamping_file)

            with open(stamping_file_path, 'r') as f:
                # Questo metodo di lettura delle righe toglie anche gli \n di fine riga
                lines = f.read().splitlines()

            # Rimuove eventuali duplicati
            lines = set(lines)

            # Se c'è almeno una timbratura..
            if lines:
                bad, errors = StampingImporter.sendStampingsOnEpas(lines)

                bad_stampings += bad
                parsing_errors += errors

            os.remove(stamping_file_path)
            logging.info("Rimosso il file %s", stamping_file_path)

        if len(bad_stampings) > 0:
            # Rimuove eventuali duplicati
            bad_stampings = set(bad_stampings)
            FileUtils.storestamping(bad_stampings_path, bad_stampings)

        if len(parsing_errors) > 0:
            FileUtils.storestamping(parsing_errors_path, parsing_errors)
    
