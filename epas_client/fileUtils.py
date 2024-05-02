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

import logging
import os
from configparser import ConfigParser
from datetime import datetime

from config import DATA_DIR, DIRECTORIES, LAST_REQUEST_FILE, LAST_REQUEST_FORMAT

LAST_REQUEST_SECTION = 'Last_Request'
LAST_REQUEST_FIELD = 'lastrequest'
LAST_STAMPING_FIELD = 'lastStamping'


class FileUtils:
    def __init__(self):
        pass

    @staticmethod
    def checkdirs():
        for directory in DIRECTORIES:
            if not os.path.isdir(directory):
                os.makedirs(directory)

    @staticmethod
    def load_last_request():
        lastrequestfile = os.path.join(DATA_DIR, LAST_REQUEST_FILE)

        if os.path.exists(lastrequestfile):
            try:
                config = ConfigParser()
                config.read_file(open(lastrequestfile))
                laststamping = config.get(LAST_REQUEST_SECTION, LAST_STAMPING_FIELD)
                lastrequest = config.get(LAST_REQUEST_SECTION, LAST_REQUEST_FIELD)
                date = datetime.strptime(lastrequest, LAST_REQUEST_FORMAT)
                logging.info("Data e ultima timbratura correttamente caricata dal file %s: %s - %s",
                             LAST_REQUEST_FILE, laststamping, date.__format__(LAST_REQUEST_FORMAT))
                return laststamping, date
            except:
                logging.warning("Errore nel formato dell'ultima data salvata in %s", LAST_REQUEST_FILE)
                return None, None
        else:
            return None, None

    @staticmethod
    def save_last_request(stamping, date):
        last_request = os.path.join(DATA_DIR, LAST_REQUEST_FILE)
        if os.path.exists(last_request):
            os.remove(last_request)

        config = ConfigParser()
        config.add_section(LAST_REQUEST_SECTION)
        config.set(LAST_REQUEST_SECTION, LAST_STAMPING_FIELD, stamping)
        config.set(LAST_REQUEST_SECTION, LAST_REQUEST_FIELD, date.__format__(LAST_REQUEST_FORMAT))
        with open(last_request, 'a+') as configfile:
            config.write(configfile)

        logging.info("Data e timbratura piu' recente salvata correttamente nel file %s: %s - %s",
                     LAST_REQUEST_FILE, stamping, date.__format__(LAST_REQUEST_FORMAT))

    @staticmethod
    def storestamping(file, stampings):

        with open(file, "a+") as f:
            for line in stampings:
                f.write("%s\n" % (line,))
                logging.debug('Aggiunta riga %s al file %s', line, file)

        logging.info("Aggiunte %d timbrature al file %s", len(stampings), file)
