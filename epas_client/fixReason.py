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

###############################################################################
# File: fixReason.py                                                          #
# Description: modifica delle causale delle timbrature durante la fascia      #
# di pausa pranzo                                                             #
#                                                                             #
# Author: Cristian Lucchesi <cristian.lucchesi@iit.cnr.it>                    #
# Last Modified: 2024-04-16 12:18                                             #
###############################################################################
from stamping import Stamping
from operator import attrgetter
import logging

from config import CAUSALE_PAUSA_PRANZO_MIN_HOUR, CAUSALE_PAUSA_PRANZO_MAX_HOUR

def isFirstEntrance(stamping: Stamping, stampingsAlreadySentList):
    """
    Verifica se la timbratura è la prima timbratura di ingresso. 
    """
    entrances = [stamp for stamp in stampingsAlreadySentList if stamp.isEntrance()]
    return stamping.isEntrance() and len(entrances) == 0

def fixStampingForMealBreak(stamping: Stamping, stampingsAlreadySentList):
    """
    Modifica la timbratura inserendo la causale pausaPranzo quando la timbratura è nella 
    fascia orario della pausa pranzo (es. 12:00 - 15:00).
    Se è già presente una causale questa non viene modificata.
    Se la timbratura è il primo ingresso non viene impostata la causale pausaPranzo anche se nella
    fascia oraria del pranzo.
    Se la timbratura è un ingresso ed è presente una precedente uscita per pausa pranzo allora viene
    impostata sulla timbratura la causale pausaPranzo anche se è fuori dalla fascia oraria del pranzo. 
    """
    if not isFirstEntrance(stamping, stampingsAlreadySentList) \
        and stamping.ora >= CAUSALE_PAUSA_PRANZO_MIN_HOUR and stamping.ora < CAUSALE_PAUSA_PRANZO_MAX_HOUR \
        and not stamping.hasReason():
        stamping.causale = "pausaPranzo"

    #Se l'ultima timbratura inviata era un'uscita per pausa pranzo allora
    #il successivo ingresso è sempre con causale pausa pranzo a chiusura dell'uscita precedente
    #per pausa pranzo
    stampingsAlreadySentList = sorted(stampingsAlreadySentList, key=attrgetter('ora', 'minuti'))
    if stamping.isEntrance() and len(stampingsAlreadySentList) > 0 \
        and stampingsAlreadySentList[len(stampingsAlreadySentList) - 1].isExit() \
        and stampingsAlreadySentList[len(stampingsAlreadySentList) - 1].causale == "pausaPranzo":
        stamping.causale = "pausaPranzo"
    return stamping
