#!/usr/bin/python
# -*- coding: utf-8 -*-

###############################################################################
#         Copyright (C) 2024  Consiglio Nazionale delle Ricerche              #
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
# File: ftpDownloader.py                                                      #
# Description: Funzioni per lo scaricamento dei file contenenti le timbrature #
# da un ftp server remoto              .                                      #
#                                                                             #
# Author: Cristian Lucchesi <cristian.lucchesi@iit.cnr.it>                    #
# Last Modified: 2024-04-16 18:25                                             #
###############################################################################

###############################################################################
#                                                                             #
#  OPERAZIONE PER IL DOWNLOAD DELLE TIMBRATURE TRAMITE PROTOCOLLO FTP         #
#                                                                             #
#    1. Connessione al lettore tramite protocollo FTP.                        #
#    2. Scaricamento dei file con le timbrature (es. timbratureAAAAMMGG.dat)  #
#                                                                             #
###############################################################################

import logging
import os
from ftplib import FTP
from fileInfoManager import FileInfoManager

from config import FTP_SERVER_NAME, FTP_SERVER_PORT, FTP_USERNAME,  \
    FTP_PASSWORD, FTP_SERVER_DIR, FTP_FILE_PREFIX, FTP_FILE_SUFFIX, \
    FTP_CONNECTION_TIMEOUT
    
from stampingImporter import StampingImporter, STAMPINGS_ALREADY_SENT_EXTENSION, StampingParsingException
from fileUtils import FileUtils

from config import STAMPINGS_DIR, DATA_DIR, BAD_STAMPINGS_FILE, \
    PARSING_ERROR_FILE, FILE_LAST_DOWNLOAD, SEND_ALL_STAMPINGS_EVERYTIME

class FTPDownloader:
    """
    Classe per il download dei file contenenti le timbrature da un server
    FTP remoto.
    """
    
    def __init__(self):
        self.bad_stampings_path = os.path.join(DATA_DIR, BAD_STAMPINGS_FILE)
        self.parsing_errors_path = os.path.join(DATA_DIR, PARSING_ERROR_FILE)
        self.file_last_download = os.path.join(DATA_DIR, FILE_LAST_DOWNLOAD)
        self.fileInfoManager = FileInfoManager(self.file_last_download)
        self.loggedIn = False

    def _login(self):
        """
        Effettua il login sul server FTP e si sposta nella directory dove
        sono presenti le timbrature
        """
        self.ftp = FTP()
        self.ftp.connect(FTP_SERVER_NAME, FTP_SERVER_PORT, FTP_CONNECTION_TIMEOUT)        
        self.ftp.login(FTP_USERNAME, FTP_PASSWORD)
        self.loggedIn = True
        self.ftp.cwd(FTP_SERVER_DIR)

    def quit_ftp(self):
        """
        Quit, and close the FTP connection.
        """
        self.ftp.quit()

    def _retrieve_file(self, file_name):
        """
        Scarica via FTP il file richiesto come parametro e lo mette nella "downloadDir"
        """
        with open("%s/%s" % (STAMPINGS_DIR, file_name), 'wb') as f:
            self.ftp.retrbinary("RETR %s" % (file_name,), f.write)
        logging.info("Scaricato file %s", file_name)

    def check_new_stamping_files(self):
        """
        Controlla se ci sono nuovi file di timbratura presenti sul server FTP,
        o aggiornamenti dell'ultimo file processato.
        Nel caso ci siano scarica gli aggiornamenti
        """
        if not os.path.exists(self.file_last_download):
            logging.warning("Il file contenente le informazioni relative all'ultimo "
                            "file di timbrature scaricato (%s) non esiste.Verranno scaricate le timbrature "
                            "a partire dall'ultimo file disponibile", self.file_last_download)

            stamping_file_names = self._get_stamping_file_names()
            if len(stamping_file_names) > 0:
                last_file_name = stamping_file_names[-1]
            else:
                logging.error("Non sono stati trovati file con le timbrature sul server. " +
                              "Prefisso del file: %s, suffisso: %s", FTP_FILE_PREFIX, FTP_FILE_SUFFIX)
                return
                        
            logging.warning("File utilizzato per prelevare le timbrature odierne: %s", last_file_name)
            size = 0
            last_line = 0

        else:
            last_file_name, size, last_line = self.fileInfoManager.getLastDownloadInfo()
            logging.info("Ultimo file scaricato: %s di %s byte. Ultima riga "
                         "processata la numero %s.", last_file_name, size, last_line)

        if not self.loggedIn:
            self._login()

        ftp_size = self.ftp.size(last_file_name)
        if ftp_size != size:
            logging.debug("Il file %s risulta di dimensione diversa rispetto "
                          "all'ultimo download, dimensione sul server FTP = %s,"
                          " dimensione ultimo download %s", last_file_name, ftp_size, size)

            if SEND_ALL_STAMPINGS_EVERYTIME:
                # Invia tutte le timbrature presenti nel file
                from_line = None
            else:
                # Scaricato e processato a partire dalla prossima riga rispetto
                # a last_line
                from_line = last_line + 1
            self._retrieve_and_process_file(last_file_name, from_line)

        # Vengono cercati e processati eventuali nuovi file con timbrature
        # presenti sul server.
        # Vengono cercati tutti i file con data successiva rispetto al file
        # passato come parametro
        self._check_new_files_on_server(last_file_name)

    def _raw_stampings(self, file_name, from_line=None):
        """
        @param file_name: il path assoluto del file da cui prelevare la lista delle timbrature
        @param from_line: il numero di riga da cui prelevare la timbratura
        Restituisce la liste della timbrature prelevate dal file passato a partire
        dalla lina indicata.
        """
        f = open(file_name, "r")
        logging.info("Processo il file %s per estrarne le timbrature", file_name)

        #Questo metodo di lettura delle righe toglie anche gli \n di fine riga
        lines = f.read().splitlines()

        #Numero di righe totali del file da processare
        number_of_lines = len(lines)

        if from_line is not None and from_line > 0:
            logging.info("Il file %s viene processato a partire dalla riga %s", file_name, from_line)
            if from_line > len(lines):
                logging.info("Il file contiene solamente %d righe, è stato richiesto di processare la riga %d. Riga non processata, raggiunta fine del file.", len(lines), from_line)
                return number_of_lines
            else:
                lines = lines[from_line-1:]
        return lines, number_of_lines

    def _already_sent_stampings(self, filename):
        """
        Costruisce un dizionario che ha come chiave la matricola della persona e come valore
        la lista delle timbrature già inviate per quella persona.
        @param filename: il nome del file da utilizzare per cercare le timbrature già inviate
        """
        stampingImporter = StampingImporter()
        rawStampings = stampingImporter.stampingsAlreadySent(filename)
        stampings = {}
        for rawStamping in rawStampings:
            try:
                stamping = stampingImporter._parseLine(rawStamping)
                if stamping.matricolaFirma in stampings:
                    stampings[stamping.matricolaFirma].append(stamping)
                else:
                     stampings[stamping.matricolaFirma] = [stamping]
            except StampingParsingException:
                continue
        return stampings

    def _retrieve_and_process_file(self, file_name, from_line=None):
        """
        Scarica il file via FTP e lo importa in Epas.
        Restituisce il numero dell'ultima riga processata del file.
        """
        logging.info("Process il file %s", file_name)
        self._retrieve_file(file_name)
        file_path = "%s/%s" % (STAMPINGS_DIR, file_name)
        
        lines, last_line_processed = self._raw_stampings(file_path, from_line)

        stampingImporter = StampingImporter()
        alreadySentRawStampings = stampingImporter.stampingsAlreadySent(file_name)
        lines = [line for line in lines if line not in alreadySentRawStampings]

        bad_stampings, parsing_errors = \
            stampingImporter.sendStampingsOnEpas(lines, filename = file_name)

        if len(bad_stampings) > 0:
            # Rimuove eventuali duplicati
            bad_stampings = set(bad_stampings)
            FileUtils.storestamping(self.bad_stampings_path, bad_stampings)

        if len(parsing_errors) > 0:
            FileUtils.storestamping(self.parsing_errors_path, parsing_errors)

        file_size = os.path.getsize(file_path)
        self.fileInfoManager.save(file_name, file_size, last_line_processed)

    def _check_new_files_on_server(self, from_file_name):
        """
        Cerca eventuali nuovi file con data successiva rispetto al file
        passato come parametro.
        Ogni nuovo file trovato viene processato e le timbrature inviata al
        sistema Epas
        """
        stamping_file_names = self._get_stamping_file_names()
        new_stamping_file_names = stamping_file_names[stamping_file_names.index(from_file_name) + 1:]
        if len(new_stamping_file_names) == 0:
            logging.info("Non ci sono sul server file di timbrature più nuovi di %s", from_file_name)
            return
        for fileName in new_stamping_file_names:
            self._retrieve_and_process_file(fileName)

    def import_all_stamping_files(self):
        """
        Importa le timbrature di tutti i file che cominciano con il prefisso FTP_FILE_PREFIX
        """
        if not self.loggedIn:
            self._login()

        stamping_file_names = self._get_stamping_file_names()

        for fileName in stamping_file_names[0:5]:
            self._retrieve_file(fileName)

        stamping_importer = StampingImporter()
        for fileName in stamping_file_names[0:5]:
            stamping_importer.sendStampingsOnEpas("%s/%s" % (STAMPINGS_DIR, fileName))

    def _get_stamping_file_names(self):
        """
        Restituisce la lista dei nomi di file di timbrature presenti in FTP
        """
        try:
            file_names = self.ftp.nlst()
        except:
            self.ftp = FTP(FTP_SERVER_NAME)
            self._login()
            file_names = self.ftp.nlst()
        file_names.sort()

        # Solamente i file con il prefisso "FTP_FILE_PREFIX" sono quelli che ci
        # interessano per le timbrature
        return [fileName for fileName in file_names if fileName.startswith(FTP_FILE_PREFIX) and fileName.endswith(FTP_FILE_SUFFIX)]

if __name__ == "__main__":
    ftp = FTPDownloader()
    ftp._login()
    file_names = ftp._get_stamping_file_names()
    print(file_names)
    stamping_file = file_names[-1]
    ftp._retrieve_file(stamping_file)

    file_path = "%s/%s" % (STAMPINGS_DIR, stamping_file)
    lines, last_line_processed = ftp._raw_stampings(file_path)
    #ftp.check_new_stamping_files()