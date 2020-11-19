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
# File: config.py                                                             #
# Description: file di configurazione contenente le informazioni necessarie   #
# al client di acquisizione delle timbrature.                                 #
#                                                                             #
# Author: Cristian Lucchesi <cristian.lucchesi@iit.cnr.it>                    #
# Last Modified: 2020-11-17 19:07                                             #
###############################################################################

#from multiprocessing.connection import CONNECTION_TIMEOUT

###############################################################################
# Configurazione dei parametri per l'accesso ai dati delle timbrature         #
# e per il loro processamento                                                 #
###############################################################################

# Directory principale che fa da contenitore per le altre cartelle
BASE_DIR = 'data'
# Directory con i file delle timbrature
STAMPINGS_DIR = BASE_DIR + '/source'
# Directory per il file lastRequest.txt e parsingErrors.txt
DATA_DIR = BASE_DIR + '/info'
# Directory in cui vengono archiviate in file tutte le timbrature scaricate dal lettore
ARCHIVES_DIR = BASE_DIR + '/archives'
# Directory dei log
LOG_DIR = BASE_DIR + '/log'
# Directories necessarie
DIRECTORIES = [BASE_DIR, DATA_DIR, STAMPINGS_DIR, ARCHIVES_DIR, LOG_DIR]
# File in cui vengono salvati i tracciati record che causano un errore nel parsing
PARSING_ERROR_FILE = 'parsing_errors.txt'
# File in cui vengono salvate le timbrature non inviate correttamente al server
BAD_STAMPINGS_FILE = 'bad_stampings.txt'
# File in cui viene salvato il datetime relativa all'ultimo download delle timbature andato a buon fine
LAST_REQUEST_FILE = 'last_request.txt'
# Formato della data dell'ultimo download delle timbrature
LAST_REQUEST_FORMAT = '%Y-%m-%d %H:%M:%S'
# Formato della data utilizzato per il naming dei file contenenti le timbrature scaricate
STAMPINGS_FILE_FORMAT = '%Y%m%d-%H%M%S'
# Formato della data usato per il parsing della data dalle timbrature scaricate dal lettore
STAMPING_DATE_FORMAT = '%H%M%S%d%m%y'
# Formato della data usato per il naming dei file di archivio timbrature
ARCHIVE_FILE_FORMAT = '%Y%m%d'
# Numero di giorni massimo, da oggi per le timbrature con problemi
MAX_BAD_STAMPING_DAYS = 10

# All'anno restituito dal lettore di badge è necessario aggiungere il numero
# sottostante per calcolare l'anno reale della timbratura
# Per gli SmartClock il valore dovrebbe essere 2000
OFFSET_ANNO_BADGE = 2000
# Numero di giorni per la prima richiesta di download delle timbrature
DAYS_TO_DOWNLOAD = 2
#Se impostata a True tutte le volte invia tutti le timbrature presenti nel file
#scaricato. Per esempio per l'Area della Ricerca di Pisa questo è obbligatorio
#perché nel file con le timbrature del giorno le nuove timbrature non vengono aggiunte
#alla fine del file ma il file viene rigenerato con tutte le timbrature (precedenti + nuove)
#in ordine sparso :-(
SEND_ALL_STAMPINGS_EVERYTIME=False

# Numero di thread da utilizzare per l'invio delle timbrature; Default 1
MAX_THREADS = 1

# Numero massimo di secondi di attesa del client per ogni PUT di inserimento timbratura
# prima di terminare il comando HTTP.
CONNECTION_TIMEOUT=10

# Gli errore ricevuti dal server che comportano un re-invio delle timbrature
SERVER_ERROR_CODES = [401, 404, 500, 501, 502, 503, 504, 505, 506, 507, 508, 509]

#Version Smartclock
REGEX_STAMPING = "^(?P<operazione>[0,E,U,T])(?P<tipo>\w{1})(?P<giornoSettimana>\d{1})(?P<matricolaFirma>\d{6})(?P<causale>\d{4})(?P<ora>\d{2})(?P<minuti>\d{2})(?P<secondi>\d{2})(?P<giorno>\d{2})(?P<mese>\d{2})(?P<anno>\d{2})(?P<lettore>\d{2})$"
#Versione Humanitas
#REGEX_STAMPING = "^(?P<matricolaFirma>\d{6})(?P<giorno>\d{2})(?P<mese>\d{2})(?P<anno>\d{4})(?P<operazione>\w{1})(?P<ora>\d{2})(?P<minuti>\d{2})$"
#Version Area di Bari
#REGEX_STAMPING = "^\"(?P<matricolaFirma>\d{10});(?P<giorno>\d{2})/(?P<mese>\d{2})/(?P<anno>\d{4});(?P<operazione>[0,E,U,T]);(?P<ora>\d{2})(?P<minuti>\d{2});(?P<causale>\d{4})\"$"
#Version Scuola normale superiore
#REGEX_STAMPING = "^(?P<lettore>\w{8})(?P<matricolaFirma>\d{5})(?P<operazione>[0,1])(?P<causale>\d{4})(?P<giorno>\d{2})(?P<mese>\d{2})(?P<anno>\d{2})(?P<ora>\d{2})(?P<minuti>\d{2})$"

# File di log dove verranno riportate le operazioni fatte dal client
LOG_FILE = LOG_DIR + '/client.log'

LOG_LEVEL = 'INFO'

# Fomato dei log
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': LOG_FILE,
            'when': 'midnight',
            'backupCount': 30,
            'interval': 1,
            'level': LOG_LEVEL,
            'formatter': 'default'
        },
        'console': {
            'level': LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': LOG_LEVEL,
    },
}

# Lista delle tipologie di badge da ignorare nell'invio delle timbrature
TIPOLOGIE_BADGE_DA_IGNORARE = []

MAPPING_CAUSALI_CLIENT_SERVER = {
    '0000': None,  # Quando il campo causale è 0000 vuol dire che non è stata selezionata nessuna causale
    '0002': 'motiviDiServizio',
    '0004': 'motiviDiServizio',
    '0003': 'pausaPranzo',
}

# Mapping tra il campo operazione ricevuto dal client e quello del server
MAPPING_OPERAZIONE_CLIENT_SERVER = {
    'E':'0',
    'U':'1'
}

#XXX: questo parametro si sovrappone al parametro LAST_REQUEST_FILE utilizzato
#     da alcuni epas_client (come per esempio per gli smartclock).   
#File all'interno del quale vengono salvate le informazioni relative all'ultimo
#file di timbrature processato dal client
FILE_LAST_DOWNLOAD="ultimo_file.txt"

###############################################################################
# Parametri di configurazione standard per lo smartclock da non modificare a  # 
#meno di non conoscerne esattamente il significato.                           #
###############################################################################

FTP_CONNECTION_TIMEOUT = 30
WAIT_SECONDS = 10
STAMPING_FILTER_COMMAND = 'F4'
STAMPINGS_FILE = 'ltcom.trn'
COMMAND_FILE = 'ltcom.com'
LOG_FILE = 'ltcom.log'
F4_COMMAND_DATA_FORMAT = '%d/%m/%y/%H/%M/%S'

RESPONSE_REG = 'Rx\d{4}'
SUCCESS_MSG = 'Rx0000'

############################################################################
# Parametri di configurazione del server ePAS dove inviare le timbrature   #
############################################################################
EPAS_SERVER_PROTOCOL = 'http'

EPAS_SERVER_NAME = 'localhost'

EPAS_SERVER_PORT = 9000

EPAS_REST_USERNAME = ''
EPAS_REST_PASSWORD = ''

EPAS_STAMPING_URL = "/stampings/create"

#Possibile valori sono ftp/sftp/local
STAMPINGS_SERVER_PROTOCOL="local"

#Se impostata a true viene ignorata la variabile STAMPINGS_SERVER_PROTOCOL
#Viene lasciata per compatibilità con il pregresso
STAMPINGS_ON_LOCAL_FOLDER=False

###############################################################################
# Parametri di configurazione del lettore badge dal quale scaricare le        #
# timbrature                                                                  #
###############################################################################

#Nome del host su cui è presente il servizio FTP/SFTP
FTP_SERVER_NAME="127.0.0.1"
FTP_SERVER_PORT=21
FTP_CONNECTION_TIMEOUT = 30

#Username e password per l'accesso FTP/SFTP
FTP_USERNAME=""
FTP_PASSWORD=""

#Directory del server FTP/SFTP in cui sono presenti i file con le timbrature
FTP_SERVER_DIR="."

#Prefisso e suffisso dei file con le timbrature
#I nomi del file son nella forma ATAAMMGG (es. AT20120805)
FTP_FILE_PREFIX="20"
FTP_FILE_SUFFIX=".txt"


###############################################################################
# Parametri di configurazione del lettore badge dal quale scaricare le        #
# timbrature                                                                  #
###############################################################################

BADGE_READER_IP = '127.0.0.1'
BADGE_READER_PORT = '21'
BADGE_READER_USER = 'epas.client'
BADGE_READER_PSW = 'client.epas'

###############################################################################
# Parametri di configurazione per l'invio delle metriche ad un pushgateway    #
###############################################################################

METRICS_ENABLED = True
METRICS_PUSHGATEWAY_URL="https://pushgateway.tools.iit.cnr.it"
METRICS_PUSHGATEWAY_USER="epas-client"
METRICS_PUSHGATEWAY_PASSWORD=""
