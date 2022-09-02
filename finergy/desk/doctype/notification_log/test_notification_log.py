# -*- coding: utf-8 -*-
# Copyright (c) 2019, Finergy Technologies and Contributors
# See license.txt
from __future__ import unicode_literals

import unittest

import finergy
from finergy.core.doctype.user.user import get_system_users
from finergy.desk.form.assign_to import add as assign_task


class TestNotificationLog(unittest.TestCase):
	def test_assignment(self):
		todo = get_todo()
		user = get_user()

		assign_task(
			{"assign_to": [user], "doctype": "ToDo", "name": todo.name, "description": todo.description}
		)
		log_type = finergy.db.get_value(
			"Notification Log", {"document_type": "ToDo", "document_name": todo.name}, "type"
		)
		self.assertEqual(log_type, "Assignment")

	def test_share(self):
		todo = get_todo()
		user = get_user()

		finergy.share.add("ToDo", todo.name, user, notify=1)
		log_type = finergy.db.get_value(
			"Notification Log", {"document_type": "ToDo", "document_name": todo.name}, "type"
		)
		self.assertEqual(log_type, "Share")

		email = get_last_email_queue()
		content = "Subject: {} shared a document ToDo".format(
			finergy.utils.get_fullname(finergy.session.user)
		)
		self.assertTrue(content in email.message)


def get_last_email_queue():
	res = finergy.db.get_all("Email Queue", fields=["message"], order_by="creation desc", limit=1)
	return res[0]


def get_todo():
	if not finergy.get_all("ToDo"):
		return finergy.get_doc({"doctype": "ToDo", "description": "Test for Notification"}).insert()

	res = finergy.get_all("ToDo", limit=1)
	return finergy.get_cached_doc("ToDo", res[0].name)


def get_user():
	return get_system_users(limit=1)[0]