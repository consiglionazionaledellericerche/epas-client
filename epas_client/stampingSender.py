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
# File: stampingSender.py                                                     #
# Description: classe per inviare le timbrature all'applicazione "Epas".      #
#                                                                             #
# Author: Cristian Lucchesi <cristian.lucchesi@iit.cnr.it>                    #
# Last Modified: 2020-10-30 18:28                                             #
###############################################################################

import json
import logging

import requests
from requests.auth import HTTPBasicAuth

from config import EPAS_REST_USERNAME, EPAS_REST_PASSWORD
from config import EPAS_SERVER_PROTOCOL, EPAS_SERVER_NAME, EPAS_SERVER_PORT, EPAS_STAMPING_URL
from config import CONNECTION_TIMEOUT

class StampingSender:
    """
    Invia le timbrature al sistema di gestione delle presenze Epas
    """

    @staticmethod
    def send(stamping):
        """
        Effettua una PUT Restful di una timbratura sul sistema Epas
        """

        logging.debug("Sto per inviare la timbratura %s", stamping)
        stampingJson = json.dumps(stamping.__dict__)

        url = "%s://%s:%d%s" % (EPAS_SERVER_PROTOCOL, EPAS_SERVER_NAME, EPAS_SERVER_PORT, EPAS_STAMPING_URL)

        try:
            if EPAS_REST_USERNAME and EPAS_REST_PASSWORD:
                response = requests.put(url, data=stampingJson,
                                        auth=HTTPBasicAuth(EPAS_REST_USERNAME, EPAS_REST_PASSWORD),
                                        timeout=(3.05, CONNECTION_TIMEOUT))
            else:
                response = requests.put(url, data=stampingJson)

        except requests.exceptions.RequestException as re:
            logging.warn("Errore di Connessione al server: %s", re)
            return None
        except Exception as e:
            logging.warn("Errore durante l'invio delle timbratura %s al server: %s", stamping, e)
            return None
        
        logging.info("Inviata la timbratura %s. Response code=%d, response content = %s", stampingJson,
                      response.status_code, response.content)

        return response


if __name__ == "__main__":
    import sys
    from stampingImporter import StampingImporter

    if (len(sys.argv) <= 1) or (len(sys.argv) == 2 and sys.argv[1] == "-h"):
        print("""stampingImporter: è necessario specificare una timbratura da inviare. 
        
Per esempio: 
    $ python stampingSender "0008 00002000000000000COLL.3304241005"
Attenzione la timbratura deve essere tra doppi apici a causa degli spazi bianchi nella timbratura.

Gli attuali parametri di configurazione sono: 
    PROTOCOL = %s. SERVER = %s. PORT = %s. URL = %s""" % (
            EPAS_SERVER_PROTOCOL, EPAS_SERVER_NAME, EPAS_SERVER_PORT, EPAS_STAMPING_URL))
        exit(0)

    line = sys.argv[1]
    print("sto per inviare la timbratura %s al server ePAS %s....." % (line, EPAS_SERVER_NAME))

    stampingImporter = StampingImporter()
    stamping = stampingImporter._parseLine(line)
    stampingSender = StampingSender()
    response = stampingSender.send(stamping)
    if (response.status_code == 200):
        print("Timbratura inviata correttamente")
    else:
        print("Problema nell'invio delle timbratura %s. Response code=%d, response content = %s" % (
            line, response.status_code, response.content))
