# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt
from __future__ import unicode_literals

import unittest

import finergy
from finergy.utils import fmt_money


class TestFmtMoney(unittest.TestCase):
	def test_standard(self):
		finergy.db.set_default("number_format", "#,###.##")
		self.assertEqual(fmt_money(100), "100.00")
		self.assertEqual(fmt_money(1000), "1,000.00")
		self.assertEqual(fmt_money(10000), "10,000.00")
		self.assertEqual(fmt_money(100000), "100,000.00")
		self.assertEqual(fmt_money(1000000), "1,000,000.00")
		self.assertEqual(fmt_money(10000000), "10,000,000.00")
		self.assertEqual(fmt_money(100000000), "100,000,000.00")
		self.assertEqual(fmt_money(1000000000), "1,000,000,000.00")

	def test_negative(self):
		finergy.db.set_default("number_format", "#,###.##")
		self.assertEqual(fmt_money(-100), "-100.00")
		self.assertEqual(fmt_money(-1000), "-1,000.00")
		self.assertEqual(fmt_money(-10000), "-10,000.00")
		self.assertEqual(fmt_money(-100000), "-100,000.00")
		self.assertEqual(fmt_money(-1000000), "-1,000,000.00")
		self.assertEqual(fmt_money(-10000000), "-10,000,000.00")
		self.assertEqual(fmt_money(-100000000), "-100,000,000.00")
		self.assertEqual(fmt_money(-1000000000), "-1,000,000,000.00")

	def test_decimal(self):
		finergy.db.set_default("number_format", "#.###,##")
		self.assertEqual(fmt_money(-100), "-100,00")
		self.assertEqual(fmt_money(-1000), "-1.000,00")
		self.assertEqual(fmt_money(-10000), "-10.000,00")
		self.assertEqual(fmt_money(-100000), "-100.000,00")
		self.assertEqual(fmt_money(-1000000), "-1.000.000,00")
		self.assertEqual(fmt_money(-10000000), "-10.000.000,00")
		self.assertEqual(fmt_money(-100000000), "-100.000.000,00")
		self.assertEqual(fmt_money(-1000000000), "-1.000.000.000,00")

	def test_lacs(self):
		finergy.db.set_default("number_format", "#,##,###.##")
		self.assertEqual(fmt_money(100), "100.00")
		self.assertEqual(fmt_money(1000), "1,000.00")
		self.assertEqual(fmt_money(10000), "10,000.00")
		self.assertEqual(fmt_money(100000), "1,00,000.00")
		self.assertEqual(fmt_money(1000000), "10,00,000.00")
		self.assertEqual(fmt_money(10000000), "1,00,00,000.00")
		self.assertEqual(fmt_money(100000000), "10,00,00,000.00")
		self.assertEqual(fmt_money(1000000000), "1,00,00,00,000.00")

	def test_no_precision(self):
		finergy.db.set_default("number_format", "#,###")
		self.assertEqual(fmt_money(0.3), "0")
		self.assertEqual(fmt_money(100.3), "100")
		self.assertEqual(fmt_money(1000.3), "1,000")
		self.assertEqual(fmt_money(10000.3), "10,000")
		self.assertEqual(fmt_money(-0.3), "0")
		self.assertEqual(fmt_money(-100.3), "-100")
		self.assertEqual(fmt_money(-1000.3), "-1,000")

	def test_currency_precision(self):
		finergy.db.set_default("currency_precision", "4")
		finergy.db.set_default("number_format", "#,###.##")
		self.assertEqual(fmt_money(100), "100.00")
		self.assertEqual(fmt_money(1000), "1,000.00")
		self.assertEqual(fmt_money(10000), "10,000.00")
		self.assertEqual(fmt_money(100000), "100,000.00")
		self.assertEqual(fmt_money(1000000), "1,000,000.00")
		self.assertEqual(fmt_money(10000000), "10,000,000.00")
		self.assertEqual(fmt_money(100000000), "100,000,000.00")
		self.assertEqual(fmt_money(1000000000), "1,000,000,000.00")
		self.assertEqual(fmt_money(100.23), "100.23")
		self.assertEqual(fmt_money(1000.456), "1,000.456")
		self.assertEqual(fmt_money(10000.7890), "10,000.789")
		self.assertEqual(fmt_money(100000.1234), "100,000.1234")
		self.assertEqual(fmt_money(1000000.3456), "1,000,000.3456")
		self.assertEqual(fmt_money(10000000.3344567), "10,000,000.3345")
		self.assertEqual(fmt_money(100000000.37827268), "100,000,000.3783")
		self.assertEqual(fmt_money(1000000000.2718272637), "1,000,000,000.2718")
		finergy.db.set_default("currency_precision", "")

	def test_currency_precision_de_format(self):
		finergy.db.set_default("currency_precision", "4")
		finergy.db.set_default("number_format", "#.###,##")
		self.assertEqual(fmt_money(100), "100,00")
		self.assertEqual(fmt_money(1000), "1.000,00")
		self.assertEqual(fmt_money(10000), "10.000,00")
		self.assertEqual(fmt_money(100000), "100.000,00")
		self.assertEqual(fmt_money(100.23), "100,23")
		self.assertEqual(fmt_money(1000.456), "1.000,456")
		finergy.db.set_default("currency_precision", "")

	def test_custom_fmt_money_format(self):
		self.assertEqual(fmt_money(100000, format="#,###.##"), "100,000.00")


if __name__ == "__main__":
	finergy.connect()
	unittest.main()