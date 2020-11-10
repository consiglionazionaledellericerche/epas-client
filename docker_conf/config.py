#!/usr/bin/python
# -*- coding: utf-8 -*-

#################################################################################
# File: config.py                                                               #
# Description: file di configurazione contenente le informazioni necessarie al  #
# client di acquisizione delle timbrature.                                      #
#                                                                               #
# Author: Cristian Lucchesi <cristian.lucchesi@iit.cnr.it>                      #
# Last Modified: 2020-11-05 19:24                                               #
#################################################################################

#################################################################################
# Configurazione dei parametri per l'accesso ai dati delle timbrature           #
# e per il loro processamento                                                   #
#################################################################################

# Directory principale che fa da contenitore per le altre cartelle
BASE_DIR = 'data'
# Directory con i file delle timbrature
STAMPINGS_DIR = BASE_DIR + '/source'
# Directory per il file lastRequest.txt e parsingErrors.txt
DATA_DIR = BASE_DIR + '/info'
# Directory in cui vengono archiviate in file tutte le timbrature scaricate dal
# lettore
ARCHIVES_DIR = BASE_DIR + '/archives'
# Directory dei log
LOG_DIR = BASE_DIR + '/log'
# Directories necessarie
DIRECTORIES = [BASE_DIR, DATA_DIR, STAMPINGS_DIR, ARCHIVES_DIR, LOG_DIR]
# File in cui vengono salvati i tracciati record che causano un errore nel
# parsing
PARSING_ERROR_FILE = 'parsing_errors.txt'
# File in cui vengono salvate le timbrature non inviate correttamente al server
BAD_STAMPINGS_FILE = 'bad_stampings.txt'
# File in cui viene salvato il datetime relativa all'ultimo download delle
# timbature andato a buon fine
LAST_REQUEST_FILE = 'last_request.txt'
# Formato della data dell'ultimo download delle timbrature
LAST_REQUEST_FORMAT = '%Y-%m-%d %H:%M:%S'
# Formato della data utilizzato per il naming dei file contenenti le timbrature
# scaricate
STAMPINGS_FILE_FORMAT = '%Y%m%d-%H%M%S'
# Formato della data usato per il parsing della data dalle timbrature scaricate
# dal lettore
STAMPING_DATE_FORMAT = '%H%M%S%d%m%y'
# Formato della data usato per il naming dei file di archivio timbrature
ARCHIVE_FILE_FORMAT = '%Y%m%d'
# Numero di giorni per la prima richiesta di download delle timbrature
DAYS_TO_DOWNLOAD = {{DAYS_TO_DOWNLOAD}}
# Numero di giorni massimo, da oggi per le timbrature con problemi
MAX_BAD_STAMPING_DAYS = {{MAX_BAD_STAMPING_DAYS}}
# All'anno restituito dal lettore di badge è necessario aggiungere il numero
# sottostante per calcolare l'anno reale della timbratura
OFFSET_ANNO_BADGE = {{OFFSET_ANNO_BADGE}}
#Se impostata a True tutte le volte invia tutti le timbrature presenti nel file
#scaricato. Per esempio per l'Area della Ricerca di Pisa questo è obbligatorio
#perché nel file con le timbrature del giorno le nuove timbrature non vengono aggiunte
#alla fine del file ma il file viene rigenerato con tutte le timbrature (precedenti + nuove)
#in ordine sparso :-(
SEND_ALL_STAMPINGS_EVERYTIME=False

# Numero di thread da utilizzare per l'invio delle timbrature; Default 1
MAX_THREADS = {{MAX_THREADS}}
# Numero massimo di secondi di attesa del client per ogni PUT di inserimento
# timbratura prima di terminare il comando HTTP.
CONNECTION_TIMEOUT=10
# Gli errore ricevuti dal server che comportano un re-invio delle timbrature
SERVER_ERROR_CODES = [{{SERVER_ERROR_CODES}}]

# Espressione regolare per eseguire il parsing delle timbrature
REGEX_STAMPING = "{{REGEX_STAMPING}}"

# File di log dove verranno riportate le operazioni fatte dal client
LOG_FILE = LOG_DIR + '/client.log'

LOG_LEVEL = '{{LOG_LEVEL}}'

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
            'backupCount': 60,
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

# Quando il campo causale è 0000 vuol dire che non è stata selezionata nessuna causale
#{'0000': None, '0001': 'motiviDiServizio', '0007': 'pausaPranzo', '0008': 'permessoBreve'}
MAPPING_CAUSALI_CLIENT_SERVER = {{MAPPING_CAUSALI_CLIENT_SERVER}}

# Mapping tra il campo operazione ricevuto dal client e quello del server
# Default {'E':'0','U':'1'}
MAPPING_OPERAZIONE_CLIENT_SERVER = {{MAPPING_OPERAZIONE_CLIENT_SERVER}}

#File all'interno del quale vengono salvate le informazioni relative all'ultimo
#file di timbrature processato dal client
FILE_LAST_DOWNLOAD="ultimo_file.txt"

###############################################################################
# Parametri di configurazione standard da non modificare a meno di non        #
# conoscerne esattamente il significato                                       #
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
EPAS_SERVER_PROTOCOL = "{{SERVER_PROTOCOL}}"

EPAS_SERVER_NAME = "{{SERVER_HOST}}"

EPAS_SERVER_PORT = {{SERVER_PORT}}

EPAS_REST_USERNAME = "{{EPAS_CLIENT_USER}}"
EPAS_REST_PASSWORD = "{{EPAS_CLIENT_PASSWORD}}"

EPAS_STAMPING_URL = "/stampings/create"

#Possibile valori sono ftp/sftp/local
STAMPINGS_SERVER_PROTOCOL="{{STAMPINGS_SERVER_PROTOCOL}}"

#Se impostata a true viene ignorata la variabile STAMPINGS_SERVER_PROTOCOL
#Viene lasciata per compatibilità con il pregresso
STAMPINGS_ON_LOCAL_FOLDER = {{STAMPINGS_ON_LOCAL_FOLDER}}

###############################################################################
# Parametri di configurazione del server dal quale scaricare le timbrature    #
###############################################################################

#Nome del host su cui è presente il servizio FTP/SFTP

FTP_SERVER_NAME = "{{FTP_SERVER_NAME}}"
FTP_SERVER_PORT = "{{FTP_SERVER_PORT}}"
FTP_CONNECTION_TIMEOUT = 30

#Username e password per l'accesso FTP/SFTP
FTP_USERNAME = "{{FTP_USERNAME}}"
FTP_PASSWORD = "{{FTP_PASSWORD}}"

#Directory del server FTP/SFTP in cui sono presenti i file con le timbrature
FTP_SERVER_DIR="{{FTP_SERVER_DIR}}"

#Prefisso e suffisso dei file con le timbrature
#I nomi del file son nella forma ATAAMMGG (es. AT20120805)
FTP_FILE_PREFIX="{{FTP_FILE_PREFIX}}"
FTP_FILE_SUFFIX="{{FTP_FILE_SUFFIX}}"

###############################################################################
# Parametri di configurazione del lettore badge dal quale scaricare le        #
# timbrature                                                                  #
###############################################################################

BADGE_READER_IP = "{{BR_IP}}"
BADGE_READER_PORT = {{BR_PORT}}
BADGE_READER_USER = "{{BR_USER}}"
BADGE_READER_PSW = "{{BR_PSW}}"
