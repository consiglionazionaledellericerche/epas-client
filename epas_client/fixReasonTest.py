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
# File: fixReasonTest.py                                                      #
# Description: test relativi alle funzioni attribuzione delle causale di      #
#    pranzo.                                                                  #
#                                                                             #
# Author: Cristian Lucchesi <cristian.lucchesi@iit.cnr.it>                    #
# Last Modified: 2024-04-16 12:28                                             #
###############################################################################

import logging
import unittest

from fixReason import fixStampingForMealBreak
from stamping import Stamping
from config import CAUSALE_PAUSA_PRANZO_MIN_HOUR, CAUSALE_PAUSA_PRANZO_MAX_HOUR

class StampingImporterTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_first_entrance_in_breaktime(self):
        currentStamping_dict = \
            {"matricolaFirma": "9802", "ora": CAUSALE_PAUSA_PRANZO_MIN_HOUR, 
             "minuti": 15, "operazione" : "0"}
        currentStamping = Stamping(**currentStamping_dict)
        self.assertTrue(currentStamping.isEntrance())
        fixStampingForMealBreak(currentStamping, [])
        self.assertTrue(not currentStamping.hasReason())

    def test_first_exit_in_breaktime(self):
        currentStamping_dict = \
            {"matricolaFirma": "9802", "ora": CAUSALE_PAUSA_PRANZO_MIN_HOUR, 
             "minuti": 15, "operazione" : "1"}
        currentStamping = Stamping(**currentStamping_dict)
        self.assertTrue(currentStamping.isExit())
        fixStampingForMealBreak(currentStamping, [])
        self.assertTrue(currentStamping.hasReason())
        self.assertEqual(currentStamping.causale, "pausaPranzo")

    def test_first_exit_in_breaktime_with_reason(self):
        currentStamping_dict = \
            {"matricolaFirma": "9802", "ora": 12, "minuti": 15,
             "operazione" : "1", "causale" : "motiviDiServizio"}
        currentStamping = Stamping(**currentStamping_dict)

        self.assertTrue(currentStamping.isExit())
        fixStampingForMealBreak(currentStamping, [])
        self.assertTrue(currentStamping.hasReason())
        self.assertEqual(currentStamping.causale, "motiviDiServizio")

    def test_entrance_in_breaktime(self):
        stamping1_dict = {"matricolaFirma": "9802", "ora": CAUSALE_PAUSA_PRANZO_MIN_HOUR - 3, "minuti": 0, "operazione" : "0"}
        stamping1 = Stamping(**stamping1_dict)
        self.assertTrue(stamping1.isEntrance())
        stamping2_dict = \
            {"matricolaFirma": "9802", "ora": CAUSALE_PAUSA_PRANZO_MIN_HOUR, "minuti": 30, 
             "operazione" : "1", "causale" : "pausaPranzo"}
        stamping2 = Stamping(**stamping2_dict)
        self.assertTrue(stamping2.isExit())

        currentStamping_dict = \
            {"matricolaFirma": "9802", "ora": CAUSALE_PAUSA_PRANZO_MAX_HOUR - 1, 
             "minuti": 0, "operazione" : "0"}
        currentStamping = Stamping(**currentStamping_dict)
        self.assertTrue(currentStamping.isEntrance())

        fixStampingForMealBreak(currentStamping, [stamping1, stamping2])
        self.assertTrue(currentStamping.hasReason())
        self.assertEqual(currentStamping.causale, "pausaPranzo")

    def test_entrance_after_breaktime_with_previous_entrance_for_meal(self):
        stamping1_dict = {"matricolaFirma": "9802", "ora": CAUSALE_PAUSA_PRANZO_MIN_HOUR - 3, "minuti": 0, "operazione" : "0"}
        stamping1 = Stamping(**stamping1_dict)
        self.assertTrue(stamping1.isEntrance())
        stamping2_dict = \
            {"matricolaFirma": "9802", "ora": CAUSALE_PAUSA_PRANZO_MIN_HOUR, "minuti": 30, 
             "operazione" : "1", "causale" : "pausaPranzo"}
        stamping2 = Stamping(**stamping2_dict)
        self.assertTrue(stamping2.isExit())

        currentStamping_dict = \
            {"matricolaFirma": "9802", "ora": CAUSALE_PAUSA_PRANZO_MAX_HOUR + 1, 
             "minuti": 0, "operazione" : "0"}
        currentStamping = Stamping(**currentStamping_dict)
        self.assertTrue(currentStamping.isEntrance())

        fixStampingForMealBreak(currentStamping, [stamping1, stamping2])
        self.assertTrue(currentStamping.hasReason())
        self.assertEqual(currentStamping.causale, "pausaPranzo")

    def test_entrance_after_breaktime_without_previous_entrance_for_meal(self):
        stamping1_dict = {"matricolaFirma": "9802", "ora": CAUSALE_PAUSA_PRANZO_MIN_HOUR - 3, "minuti": 0, "operazione" : "0"}
        stamping1 = Stamping(**stamping1_dict)
        self.assertTrue(stamping1.isEntrance())
        stamping2_dict = \
            {"matricolaFirma": "9802", "ora": CAUSALE_PAUSA_PRANZO_MIN_HOUR - 1, "minuti": 0, 
             "operazione" : "1"}
        stamping2 = Stamping(**stamping2_dict)
        self.assertTrue(stamping2.isExit())

        currentStamping_dict = \
            {"matricolaFirma": "9802", "ora": CAUSALE_PAUSA_PRANZO_MAX_HOUR + 1, 
             "minuti": 0, "operazione" : "0"}
        currentStamping = Stamping(**currentStamping_dict)
        self.assertTrue(currentStamping.isEntrance())

        fixStampingForMealBreak(currentStamping, [stamping1, stamping2])
        self.assertTrue(not currentStamping.hasReason())

if __name__ == '__main__':
    logging.basicConfig(
        filename='test.log',
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)

    unittest.main()
