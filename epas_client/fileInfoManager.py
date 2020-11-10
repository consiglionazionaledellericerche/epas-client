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
# File: fileInfoManager.py                                                    #
# Description: si occupa di serializzare e deserializzare su file le          #
# informazioni relative all'ultimo file di timbrature processato per          # 
# elaborare le presenze del personale                                         #
#                                                                             #
# Author: Cristian Lucchesi <cristian.lucchesi@iit.cnr.it>                    #
# Last Modified: 2020-11-05 18:41                                             #
###############################################################################

import logging

class FileInfoManager:
    """
    Mantiene le informazioni relative all'ultimo file scaricato/processato via
    local/FTP/SFTP.
    """

    COMMENT = """# file generato dal client  per l'acquisizione delle timbrature tramite Badge
# contiene: 
# - nome dell'ultimo file scaricato
# - dimensione del file all'ultimo scaricamento
# - ultima riga processata per quel file
#
# I dati sono separati da tab
# nome file nella forma: ATaammgg
# dimensione in byte
#
# ultimo file\tsize\tultima riga
"""

    def __init__(self, file_name):
        """
        file_name è il nome del file che contiene le informazioni sull'ultimo
        file scaricato
        """
        self.fileName = file_name

    def save(self, last_file_name, size, line):
        """
        Salva le informazioni relative all'ultimo file scaricato su file
        """
        f = open(self.fileName, 'w')
        f.write(self.COMMENT)
        info = "%s\t%s\t%s" %(last_file_name, size, line)
        f.write(info)
        f.close()
        logging.debug("Salvato il file file %s con info: %s", last_file_name, info)
        

    def getLastDownloadInfo(self):
        """
        Ritorna una tupla di tre elementi contenente il nome dell'ultimo 
        file scaricato, la sua dimensioni nell'ultimo download ed il numero 
        dell'ultima riga processata per quel file.
        Le informazioni vengono lette da file e sono nel formato:

        PXAAMMGG size line
        
        dove:
          PX = prefisso di due lettere (ex. AT) 
          AA di due cifre
          MM mese 
          GG giorno
          size dimensione del file nell'ultimo scarimento
          line numero dell'ultimo riga processata
        
        """
        f = open(self.fileName, 'r')
        for line in f.readlines():
            if line.startswith('#'):
                continue
            else:
                values = line.split('\t')
                f.close()
                return [values[0], int(values[1]), int(values[2])]
        f.close()
        raise ValueError("informazioni sull'ultimo file scaricato non trovate")
