# repo: camponez/importescala
# path: test/test_escala.py

#!/usr/bin/python2
# -*- coding: utf-8 -*-
# coding=utf-8

import unittest
from datetime import datetime

from lib.escala import Escala
import dirs

dirs.DEFAULT_DIR = dirs.TestDir()


class FrameTest(unittest.TestCase):

    def setUp(self):
        self.escala = Escala('fixtures/escala.xml')
        self.dir = dirs.TestDir()
        self.maxDiff = None

    def tearDown(self):
        pass

    def test_attributos_voo_1(self):
        p_voo = self.escala.escalas[0]

        self.assertEqual(p_voo.activity_date, datetime(2013, 3, 1, 11, 36))
        self.assertEqual(p_voo.present_location, 'VCP')
        self.assertEqual(p_voo.flight_no, '4148')
        self.assertEqual(p_voo.origin, 'VCP')
        self.assertEqual(p_voo.destination, 'GYN')
        self.assertEqual(p_voo.actype, 'E95')
        self.assertTrue(p_voo.checkin)
        self.assertEqual(p_voo.checkin_time, datetime(2013, 3, 1, 10, 36))
        self.assertEqual(p_voo.std, datetime(2013, 3, 1, 13, 13))
        self.assertEqual(p_voo.sta, datetime(2013, 3, 1, 11, 36))
        self.assertEqual(p_voo.activity_info, 'AD4148')
        self.assertFalse(p_voo.duty_design)

    def test_attributos_voo_17(self):
        p_voo = self.escala.escalas[17]

        self.assertEqual(p_voo.activity_date, datetime(2013, 10, 28, 3, 0))
        self.assertEqual(p_voo.present_location, 'VCP')
        self.assertEqual(p_voo.flight_no, None)
        self.assertEqual(p_voo.origin, 'VCP')
        self.assertEqual(p_voo.destination, 'VCP')
        self.assertEqual(p_voo.activity_info, 'P04')
        self.assertEqual(p_voo.actype, None)
        self.assertEqual(p_voo.sta, datetime(2013, 10, 28, 3, 0))
        self.assertEqual(p_voo.std, datetime(2013, 10, 28, 15, 0))
        self.assertFalse(p_voo.checkin)
        self.assertEqual(p_voo.checkin_time, None)
        self.assertFalse(p_voo.duty_design)

    def test_attributos_voo_18(self):
        p_voo = self.escala.escalas[18]

        self.assertEqual(p_voo.activity_date, datetime(2013, 10, 29, 4, 58))
        self.assertEqual(p_voo.present_location, 'VCP')
        self.assertEqual(p_voo.flight_no, '4050')
        self.assertEqual(p_voo.origin, 'VCP')
        self.assertEqual(p_voo.destination, 'FLN')
        self.assertEqual(p_voo.activity_info, 'AD4050')
        self.assertEqual(p_voo.actype, 'E95')
        self.assertEqual(p_voo.sta, datetime(2013, 10, 29, 4, 58))
        self.assertEqual(p_voo.std, datetime(2013, 10, 29, 6, 15))
        self.assertTrue(p_voo.checkin)
        self.assertEqual(p_voo.checkin_time, datetime(2013, 10, 29, 5, 8))
        self.assertFalse(p_voo.duty_design)
        self.assertEqual(p_voo.horas_de_voo, '1:17')

    def test_attributos_quarto_voo(self):
        p_voo = self.escala.escalas[25]
        self.assertFalse(p_voo.checkin)
        self.assertEqual(p_voo.checkin_time, None)
        self.assertEqual(p_voo.flight_no, '2872')
        self.assertEqual(p_voo.activity_info, 'AD2872')

    def test_calculo_horas_voadas(self):
        s_horas = {
            'h_diurno': '6:40',
            'h_noturno': '6:47',
            'h_total_voo': '13:27',
            'h_faixa2': '0:00',
            'h_sobreaviso': '40:00',
            'h_reserva': '29:13'
        }
        self.assertEqual(self.escala.soma_horas(), s_horas)

    def test_ics(self):
        """
        Check ICS output
        """
        escala = Escala('fixtures/escala_ics.xml')
        f_result = open(self.dir.get_data_dir() + 'fixtures/escala.ics')
        self.assertEqual(escala.ics(), f_result.read())
        f_result.close()

    def test_csv(self):
        """
        Check CSV output
        """
        f_result = open(self.dir.get_data_dir() + 'fixtures/escala.csv')

        self.assertEqual(self.escala.csv(), f_result.read())
        f_result.close()


def main():
    unittest.main()


if __name__ == '__main__':
    main()
