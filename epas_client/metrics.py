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
# File: metrics.py                                                            #
# Description: definisce le metriche Prometheus e il metodo per inviare al    #
# pushgateway                                                                 #
#                                                                             #
# Author: Cristian Lucchesi <cristian.lucchesi@iit.cnr.it>                    #
# Last Modified: 2020-11-17 19:36                                             #
###############################################################################

from prometheus_client import CollectorRegistry, Summary, Histogram, Gauge, \
    Info
from prometheus_client.exposition import basic_auth_handler
from pathlib import Path

from config import METRICS_ENABLED, METRICS_PUSHGATEWAY_URL, \
    METRICS_PUSHGATEWAY_USER, METRICS_PUSHGATEWAY_PASSWORD, \
    EPAS_REST_USERNAME, BADGE_READER_IP, FTP_SERVER_NAME

#################### CONFIGURAZIONI METRICHE PROMETHEUS ########################

CLIENT_REGISTRY = CollectorRegistry()

METRICS_LABEL_NAMES = ['instance', 'badgeReader', 'ftp_server']

_CLIENT_INFO = Info('epas_client', 'Tipologia di client e protocollo utilizzato',
                    METRICS_LABEL_NAMES, registry = CLIENT_REGISTRY)

CLIENT_INFO = _CLIENT_INFO.labels(EPAS_REST_USERNAME, BADGE_READER_IP, FTP_SERVER_NAME)

# Create a metric to track time spent to execute job.
_JOB_TIME= Summary('epas_client_job_processing_seconds', 
                   'Time spent executing job', 
                   METRICS_LABEL_NAMES,
                   registry = CLIENT_REGISTRY)
JOB_TIME = _JOB_TIME.labels(EPAS_REST_USERNAME, BADGE_READER_IP, FTP_SERVER_NAME)

_SEND_TIME = Histogram('epas_client_send_stamping_seconds', 
                       'Tempi di invio delle timbrature',
                       METRICS_LABEL_NAMES, 
                       registry = CLIENT_REGISTRY)
SEND_TIME = _SEND_TIME.labels(EPAS_REST_USERNAME, BADGE_READER_IP, FTP_SERVER_NAME)

_STAMPINGS_SENT = Gauge('epas_client_stampings_sent_total', 
                        'Timbrature inviate',
                        METRICS_LABEL_NAMES, 
                        registry = CLIENT_REGISTRY)
STAMPINGS_SENT = _STAMPINGS_SENT.labels(EPAS_REST_USERNAME, BADGE_READER_IP, FTP_SERVER_NAME)

_BAD_STAMPINGS = Gauge('epas_client_bad_stampings_total', 
                       'Timbrature inviate con problemi',
                       METRICS_LABEL_NAMES, 
                       registry = CLIENT_REGISTRY)
BAD_STAMPINGS = _BAD_STAMPINGS.labels(EPAS_REST_USERNAME, BADGE_READER_IP, FTP_SERVER_NAME)

_PARSING_ERRORS = Gauge('epas_client_parsing_errors_total', 
                        'Timbrature con problemi di parsing',
                        METRICS_LABEL_NAMES,
                        registry = CLIENT_REGISTRY)
PARSING_ERRORS = _PARSING_ERRORS.labels(EPAS_REST_USERNAME, BADGE_READER_IP, FTP_SERVER_NAME)

################# FINE CONFIGURAZIONI METRICHE PROMETHEUS #####################


class PrometheusClient:

    @staticmethod
    def version():
        path = Path(__file__).parent / "../VERSION"
        with path.open() as vf:
            version = vf.readline()        
        return str(version)

    @staticmethod
    def my_auth_handler(url, method, timeout, headers, data):
        return basic_auth_handler(url, method, timeout, headers, data, 
            METRICS_PUSHGATEWAY_USER, METRICS_PUSHGATEWAY_PASSWORD)

    @staticmethod
    def push_metrics():
        from prometheus_client import push_to_gateway
        from config import STAMPINGS_SERVER_PROTOCOL

        CLIENT_INFO.info({'type' : 'epas-client', 
                          'stampings_server_protocol': STAMPINGS_SERVER_PROTOCOL,
                          'version' : PrometheusClient.version()})

        if METRICS_PUSHGATEWAY_USER and METRICS_PUSHGATEWAY_PASSWORD:
            push_to_gateway(METRICS_PUSHGATEWAY_URL, job=f"epas-client-{EPAS_REST_USERNAME}", 
                            registry=CLIENT_REGISTRY, handler=PrometheusClient.my_auth_handler)
        else:
            push_to_gateway(METRICS_PUSHGATEWAY_URL, job=f"epas-client-{EPAS_REST_USERNAME}", 
                            registry=CLIENT_REGISTRY)
