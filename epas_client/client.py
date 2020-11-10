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
# File: client.py                                                             #
# Description: si occupa di prelevare via directory locale/FTP/SFTP i file    #
# con le timbrature del personale e di inviarle via Restful all'applicazione  #
# ePAS che gestisce le  presenze del personale.                               #
#                                                                             #
# Author: Cristian Lucchesi <cristian.lucchesi@iit.cnr.it>                    #
# Last Modified: 2020-11-04 10:12                                             #
###############################################################################

import logging
import os

from ftpDownloader import FTPDownloader
from sftpDownloader import SFTPDownloader
from localFolderManager import LocalFolderManager
from smartclockManager import SmartClockManager

from config import PARSING_ERROR_FILE, BAD_STAMPINGS_FILE, DATA_DIR

#Quando questa configurazione è true viene ignorata la parte 
# STAMPINGS_SERVER_PROTOCOL
from config import STAMPINGS_ON_LOCAL_FOLDER

from config import STAMPINGS_SERVER_PROTOCOL

from fileUtils import FileUtils
from lock import lock
from epasClient import EpasClient

bad_stampings_path = os.path.join(DATA_DIR, BAD_STAMPINGS_FILE)
parsing_errors_path = os.path.join(DATA_DIR, PARSING_ERROR_FILE)

# Comando per effettuare l'invio solo delle bad stampings
BAD_STAMPINGS_COMMAND = '-b'


class StampingClient:
    """
    Client per il sistema di rilevazione delle presenze presenti su file.
    I file con le timbrature possono essere in locale, in ftp o in sftp.
    Si occupa di elaborare i file presenti in "dataDir" e di spedire le timbrature
    via HTTP/Restful al sistema di rilevazione delle presenze.
    """

    @staticmethod
    def process_stamping_files():
        
        logging.info("@@ Invio timbrature @@")
        if STAMPINGS_ON_LOCAL_FOLDER or STAMPINGS_SERVER_PROTOCOL == "local":
            manager = LocalFolderManager()
            manager.check_new_stamping_files()
        elif STAMPINGS_SERVER_PROTOCOL == "sftp":
            manager = SFTPDownloader()
            manager.check_new_stamping_files()
            manager.close()            
        elif STAMPINGS_SERVER_PROTOCOL == "ftp":
            ftpDownloader = FTPDownloader()
            ftpDownloader.check_new_stamping_files()
        elif STAMPINGS_SERVER_PROTOCOL == "smartclock":            
            last_stamping, last_stampingdate = SmartClockManager.downloadstampings()
            if last_stamping is not None:
                FileUtils.save_last_request(last_stamping, last_stampingdate)
            SmartClockManager.process_stamping_files()

if __name__ == "__main__":
    from config import LOGGING
    import timeit
    import sys
    import logging.config

    start = timeit.default_timer()
    FileUtils.checkdirs()

    logging.config.dictConfig(LOGGING)
    logging.getLogger("requests").setLevel(logging.WARNING)

    lock.lock()

    LOG_START = '#####################################    AVVIO CLIENT TIMBRATURE    ######################################'

    logging.info(LOG_START)

    if BAD_STAMPINGS_COMMAND in sys.argv:
        EpasClient.send_bad_stampings()
    else:
        StampingClient.process_stamping_files()
        
    LOG_END = '#########################    ESECUZIONE CLIENT COMPLETATA IN  %02dmin e %02dsec   ############################'

    end = timeit.default_timer()

    lock.release()

    seconds = end - start
    m, s = divmod(seconds, 60)

    logging.info(LOG_END, m, s)
