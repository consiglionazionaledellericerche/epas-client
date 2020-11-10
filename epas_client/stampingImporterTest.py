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
# File: stampingImporterTest.py                                               #
# Description: test relativi alle funzioni di parsing delle timbrature        #
#                                                                             #
# Author: Cristian Lucchesi <cristian.lucchesi@iit.cnr.it>                    #
# Last Modified: 2020-10-30 18:28                                             #
###############################################################################

import logging
import unittest

from stampingImporter import StampingImporter


class StampingImporterTest(unittest.TestCase):
    def setUp(self):
        self.importer = StampingImporter()

    def test_valid_stamping(self):
        stamping = \
            self.importer._parseLine("E13000000232000013505605031400\r\n")
        self.assertTrue(stamping.isValid())
        self.assertEqual(stamping.operazione, "0")
        self.assertEqual(stamping.tipo, "1")
        self.assertEqual(stamping.giornoSettimana, "3")
        self.assertEqual(stamping.matricolaFirma, "000000232")
        self.assertEqual(stamping.causale, None)
        self.assertEqual(stamping.ora, 13)
        self.assertEqual(stamping.minuti, 50)
        self.assertEqual(stamping.secondi, 56)
        self.assertEqual(stamping.giorno, 5)
        self.assertEqual(stamping.mese, 3)
        self.assertEqual(stamping.anno, 2014)
        self.assertTrue(not stamping.isToBeIgnored())

if __name__ == '__main__':
    logging.basicConfig(
        filename='test.log',
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)

    unittest.main()
