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

import os
import logging
import sys

LOCK_FILE = 'client.pid'

class lock:
    """
    Semplice classe che si occupa di effettuare i controlli sul file di lock
    """
    @staticmethod
    def lock():

        # Verifico l'esistenza del file
        if os.path.exists(LOCK_FILE):

            # Se esiste verifico il pid presente
            with open(LOCK_FILE, 'r') as f:
                oldpid = f.readline()

            if os.path.exists('/proc/%s' % oldpid):
                logging.warning('Process is already running with pid %s. Aborting execution', oldpid)
                sys.exit(1)
            else:
                # il file esiste già ma non è associato a nessun processo
                logging.warning('File %s is present but program is not running. Deleting old pid file', LOCK_FILE)
                os.remove(LOCK_FILE)

        # Il file non è presente
        with open(LOCK_FILE, "w") as f:
            f.write("%s" % os.getpid())

    @staticmethod
    def release():

        with open(LOCK_FILE, "r") as f:
            pid = f.readline()

        if int(pid) == os.getpid():
            os.remove(LOCK_FILE)
        else:
            logging.error('File %s is present with a different pid. Aborting', LOCK_FILE)
            sys.exit(1)