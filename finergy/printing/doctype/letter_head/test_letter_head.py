# -*- coding: utf-8 -*-
# Copyright (c) 2017, Finergy Technologies and Contributors
# See license.txt
from __future__ import unicode_literals

import unittest

import finergy


class TestLetterHead(unittest.TestCase):
	def test_auto_image(self):
		letter_head = finergy.get_doc(
			dict(doctype="Letter Head", letter_head_name="Test", source="Image", image="/public/test.png")
		).insert()

		# test if image is automatically set
		self.assertTrue(letter_head.image in letter_head.content)