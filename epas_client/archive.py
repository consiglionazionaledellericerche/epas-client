#!/usr/bin/python3
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
from datetime import datetime

from config import ARCHIVES_DIR, ARCHIVE_FILE_FORMAT
from stampingImporter import StampingImporter

class Archive:

    @staticmethod
    def archive_and_check_stampings(stampings):
        """
        :param stampings: La lista delle timbrature da archiviare
        :return: La timbratura più recente tra le timbrature passate e la relativa data
        """
        last_stamping_date = None
        last_stamping = None

        for stamping in stampings:
            try:
                stamp = StampingImporter._parseLine(stamping)
                stamping_date = datetime(stamp.anno,stamp.mese,stamp.giorno,stamp.ora,stamp.minuti)
                if last_stamping_date is None or last_stamping_date < stamping_date:
                    last_stamping_date = stamping_date
                last_stamping = stamping
                dailyfile = stamping_date.__format__(ARCHIVE_FILE_FORMAT)
                archive_path = os.path.join(ARCHIVES_DIR, dailyfile)

                with open(archive_path, 'a+') as f:
                    f.write("%s\n" % (stamping,))

            except Exception as e:
                logging.warn("Impossibile estrarre la data dal tracciato %s: %s", stamping, e)

        return last_stamping, last_stamping_date
