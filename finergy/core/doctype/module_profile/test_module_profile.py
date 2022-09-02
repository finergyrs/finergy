# -*- coding: utf-8 -*-
# Copyright (c) 2020, Finergy Technologies and Contributors
# See license.txt
from __future__ import unicode_literals

import unittest

import finergy


class TestModuleProfile(unittest.TestCase):
	def test_make_new_module_profile(self):
		if not finergy.db.get_value("Module Profile", "_Test Module Profile"):
			finergy.get_doc(
				{
					"doctype": "Module Profile",
					"module_profile_name": "_Test Module Profile",
					"block_modules": [{"module": "Accounts"}],
				}
			).insert()

		# add to user and check
		if not finergy.db.get_value("User", "test-for-module_profile@example.com"):
			new_user = finergy.get_doc(
				{"doctype": "User", "email": "test-for-module_profile@example.com", "first_name": "Test User"}
			).insert()
		else:
			new_user = finergy.get_doc("User", "test-for-module_profile@example.com")

		new_user.module_profile = "_Test Module Profile"
		new_user.save()

		self.assertEqual(new_user.block_modules[0].module, "Accounts")