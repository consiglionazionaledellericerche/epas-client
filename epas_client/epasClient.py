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
# File: epasClient.py                                                         #
# Description: si occupa di prelevare via FTP i file con le timbrature del    #
# personale e di inviarle via Restful all'applicazione "Epas" che gestisce le #
# presenze del personale                                                      #
#                                                                             #
# Author: Cristian Lucchesi <cristian.lucchesi@iit.cnr.it>                    #
# Last Modified: 2020-10-30 18:27                                             #
###############################################################################

import logging
import os
from datetime import datetime, timedelta

from config import DATA_DIR, PARSING_ERROR_FILE, BAD_STAMPINGS_FILE,  \
    MAX_BAD_STAMPING_DAYS
from fileUtils import FileUtils
from stampingImporter import StampingImporter

bad_stampings_path = os.path.join(DATA_DIR, BAD_STAMPINGS_FILE)
parsing_errors_path = os.path.join(DATA_DIR, PARSING_ERROR_FILE)

class EpasClient:
    """
    Client per il sistema di rilevazione delle presenze ePAS.
    Questa classe di supporto serve solamente per inviare le "bad stampings".
    """

    @staticmethod
    def send_bad_stampings():

        logging.info("@@ Invio timbrature con problemi @@")

        if os.path.exists(bad_stampings_path):
            bad_stampings = []
            parsing_errors = []

            now = datetime.now()
            still_good_stampings = []
            oldest_day_allowed = datetime.combine(now - timedelta(MAX_BAD_STAMPING_DAYS), now.time().min)
            logging.info("Bad Stampings: verranno mantenute solo le timbrature più nuove di %s", oldest_day_allowed)
            
            with open(bad_stampings_path, 'r') as f:
                lines = f.read().splitlines()
                lines = set(lines)

            # butto via le timbrature più vecchie di x giorni
            for line in lines:
                stamp = StampingImporter._parseLine(line)
                stamping_date = datetime(stamp.anno,stamp.mese,stamp.giorno,stamp.ora,stamp.minuti)

                if stamping_date >= oldest_day_allowed:
                    still_good_stampings.append(line)

            removed_lines = len(lines) - len(still_good_stampings)
            if removed_lines > 0:
                logging.info('Rimosse %d timbrature dal file %s perché più vecchie del %s',
                         removed_lines, BAD_STAMPINGS_FILE, oldest_day_allowed)

            os.remove(bad_stampings_path)
            logging.info("Rimosso il file %s", BAD_STAMPINGS_FILE)

            if still_good_stampings:
                bad, errors = StampingImporter.sendStampingsOnEpas(still_good_stampings)

                bad_stampings += bad
                parsing_errors += errors

                if len(bad_stampings) > 0:
                    # Rimuove eventuali duplicati
                    bad_stampings = set(bad_stampings)
                    FileUtils.storestamping(bad_stampings_path, bad_stampings)

                if len(parsing_errors) > 0:
                    FileUtils.storestamping(parsing_errors_path, parsing_errors)

        else:
            logging.info("File %s non presente.", BAD_STAMPINGS_FILE)
