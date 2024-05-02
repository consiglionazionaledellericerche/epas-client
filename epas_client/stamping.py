#!/usr/bin/python
# -*- coding: utf-8 -*-

###############################################################################
#         Copyright (C) 2024  Consiglio Nazionale delle Ricerche              #
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

#################################################################################
# File: stamping.py                                                             #
# Description: mantiene al suo interno le informazioni relative ad una          #
#              timbratura                                                       #
#                                                                               #
# Author: Cristian Lucchesi <cristian.lucchesi@iit.cnr.it>                      #
# Last Modified: 2024-04-16 12:18                                               #
#################################################################################

from config import TIPOLOGIE_BADGE_DA_IGNORARE

class Stamping:
    """
    Classe contenitore per le informazioni relative ad una timbratura via Badge
    """

    def __init__(self, matricolaFirma=None, operazione=None, 
                 anno=None, mese=None, giorno=None, 
                 ora=None, minuti=None, causale=None):
        self.matricolaFirma = matricolaFirma
        self.operazione = operazione
        self.anno = anno
        self.mese = mese
        self.giorno = giorno
        self.ora = ora
        self.minuti = minuti
        self.causale = causale

    def isEntrance(self):
        return hasattr(self, "operazione") and (self.operazione.endswith("0")  or self.operazione == "E")

    def isExit(self):
        return hasattr(self, "operazione") and (self.operazione.endswith("1") or self.operazione == "U")

    def hasReason(self):
        return hasattr(self, "causale") and self.causale != None and self.causale != ""

    def isToBeIgnored(self):
        """
        Le timbrature di alcune tipologie di contratti devono essere ignorate.
        Anche le timbrature con senso diverso da Transito di Entrata (E) 
        transito di Uscita (U) sono ignorate
        """

        return self.matricolaFirma is None or \
               self.matricolaFirma in TIPOLOGIE_BADGE_DA_IGNORARE or \
               self.operazione not in ["0", "1", "00", "01"]

    def isValid(self):
        """
        Ritorna true se la timbratura è valida, false altrimenti.
        Effettua dei controlli di base sui valori di cui è composta
        la timbratura, principalmente su quelli relativi a data
        e ora.
        """

        # i controlli sull'anno molto empirici, chissà cosa passerà come
        # valore se superiamo l'anno 2099...
        isValid = not (self.operazione is None \
                       or self.anno is None or not type(self.anno) == int \
                       or self.anno < 1980 \
                       or self.mese is None or not type(self.mese) == int \
                       or self.mese < 1 or self.mese > 12 \
                       or self.giorno is None or not type(self.giorno) == int \
                       or self.giorno < 1 or self.giorno > 31 \
                       or self.ora is None or not type(self.ora) == int \
                       or self.ora < 0 or self.ora > 24 \
                       or self.minuti is None or not type(self.minuti) == int \
                       or self.minuti < 0 or self.minuti > 60 \
                       or self.secondi is None or not type(self.secondi) == int \
                       or self.secondi < 0 or self.secondi > 60)

        return isValid

    def __str__(self):
        return """operazione: %s, tipo: %s, giorno settimana: %s, numero badge: %s, causale: %s
ora: %s, minuti: %s, secondi: %s, giorno: %s, mese: %s, anno: %s 
lettore: %s""" % (self.operazione if hasattr(self, "operazione") else None, 
                  self.tipo if hasattr(self, "tipo") else None, 
                  self.giornoSettimana if hasattr(self, "giornoSettimana") else None,
                  self.matricolaFirma if hasattr(self, "matricolaFirma") else None, 
                  self.causale if hasattr(self, "causale") else None,
                  self.ora if hasattr(self, "ora") else None, 
                  self.minuti if hasattr(self, "minuti") else None, 
                  self.secondi if hasattr(self, "secondi") else None,
                  self.giorno if hasattr(self, "giorno") else None, 
                  self.mese if hasattr(self, "mese") else None, 
                  self.anno if hasattr(self, "anno") else None,
                  self.lettore if hasattr(self, "lettore") else None
                  )
