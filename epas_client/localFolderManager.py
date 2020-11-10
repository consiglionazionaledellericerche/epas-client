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
# File: localFolderManager.py                                                 #
# Description: Funzioni per il prelevamente da una cartella locale dei file   #
# contenenti le timbrature.                                                   #
#                                                                             #
# Author: Cristian Lucchesi <cristian.lucchesi@iit.cnr.it>                    #
# Last Modified: 2020-11-04 10:09                                             #
###############################################################################

import logging
import os

from fileInfoManager import FileInfoManager
from config import FTP_FILE_PREFIX, FTP_FILE_SUFFIX

from stampingImporter import StampingImporter
from fileUtils import FileUtils
    
from config import  DATA_DIR, BAD_STAMPINGS_FILE, \
    PARSING_ERROR_FILE, STAMPINGS_DIR, FILE_LAST_DOWNLOAD, \
    SEND_ALL_STAMPINGS_EVERYTIME

class LocalFolderManager:
    """
    Classe per il download dei file contenenti le timbrature del sistema della Tecnosoftware
    """
    
    def __init__(self):
        self.bad_stampings_path = os.path.join(DATA_DIR, BAD_STAMPINGS_FILE)
        self.parsing_errors_path = os.path.join(DATA_DIR, PARSING_ERROR_FILE) 
        self.file_last_download = os.path.join(DATA_DIR, FILE_LAST_DOWNLOAD)
        self.fileInfoManager = FileInfoManager(self.file_last_download)
        self.loggedIn = False

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

        file_size = os.path.getsize(os.path.join(STAMPINGS_DIR, last_file_name))
        if file_size != size:
            logging.debug("Il file %s risulta di dimensione diversa rispetto "
                          "all'ultimo download, dimensione sul filesystem = %s,"
                          " dimensione ultimo download %s", last_file_name, file_size, size)

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
    
    def _retrieve_and_process_file(self, file_name, from_line=None):
        """
        Scarica il file via FTP e lo importa in Epas.
        Restituisce il numero dell'ultima riga processata del file.
        """
        logging.info("Process il file %s", file_name)
        #self._retrieve_file(file_name)
        file_path = "%s/%s" % (STAMPINGS_DIR, file_name)
        
        lines, last_line_processed = self._raw_stampings(file_path, from_line)
        
        stamping_importer = StampingImporter()
        bad_stampings, parsing_errors = stamping_importer.sendStampingsOnEpas(lines)
        
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


    def _get_stamping_file_names(self):
        """
        Restituisce la lista dei nomi di file di timbrature presenti in locale/FTP/SFTP
        """
         
        file_names = os.listdir(STAMPINGS_DIR)
        file_names.sort()

        # Solamente i file con il prefisso "FTP_FILE_PREFIX" sono quelli che ci
        # interessano per le timbrature
        return [fileName for fileName in file_names if fileName.startswith(FTP_FILE_PREFIX) and fileName.endswith(FTP_FILE_SUFFIX)]

if __name__ == "__main__":
    manager = LocalFolderManager()
    file_names = manager._get_stamping_file_names()
    print(file_names)
    if file_names:
        stamping_file = file_names[-1]    
        file_path = "%s/%s" % (STAMPINGS_DIR, stamping_file)
        lines, last_line_processed = manager._raw_stampings(file_path)
    manager.check_new_stamping_files()