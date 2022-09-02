# -*- coding: utf-8 -*-
# Copyright (c) 2019, Finergy Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import finergy
from finergy.model.document import Document


class NotificationSettings(Document):
	def on_update(self):
		from finergy.desk.notifications import clear_notification_config

		clear_notification_config(finergy.session.user)


def is_notifications_enabled(user):
	enabled = finergy.db.get_value("Notification Settings", user, "enabled")
	if enabled is None:
		return True
	return enabled


def is_email_notifications_enabled(user):
	enabled = finergy.db.get_value("Notification Settings", user, "enable_email_notifications")
	if enabled is None:
		return True
	return enabled


def is_email_notifications_enabled_for_type(user, notification_type):
	if not is_email_notifications_enabled(user):
		return False

	if notification_type == "Alert":
		return False

	fieldname = "enable_email_" + finergy.scrub(notification_type)
	enabled = finergy.db.get_value("Notification Settings", user, fieldname)
	if enabled is None:
		return True
	return enabled


def create_notification_settings(user):
	if not finergy.db.exists("Notification Settings", user):
		_doc = finergy.new_doc("Notification Settings")
		_doc.name = user
		_doc.insert(ignore_permissions=True)


def toggle_notifications(user: str, enable: bool = False):
	try:
		settings = finergy.get_doc("Notification Settings", user)
	except finergy.DoesNotExistError:
		finergy.clear_last_message()
		return

	if settings.enabled != enable:
		settings.enabled = enable
		settings.save()


@finergy.whitelist()
def get_subscribed_documents():
	if not finergy.session.user:
		return []

	try:
		if finergy.db.exists("Notification Settings", finergy.session.user):
			doc = finergy.get_doc("Notification Settings", finergy.session.user)
			return [item.document for item in doc.subscribed_documents]
	# Notification Settings is fetched even before sync doctype is called
	# but it will throw an ImportError, we can ignore it in migrate
	except ImportError:
		pass

	return []


def get_permission_query_conditions(user):
	if not user:
		user = finergy.session.user

	if user == "Administrator":
		return

	roles = finergy.get_roles(user)
	if "System Manager" in roles:
		return """(`tabNotification Settings`.name != 'Administrator')"""

	return """(`tabNotification Settings`.name = {user})""".format(user=finergy.db.escape(user))


@finergy.whitelist()
def set_seen_value(value, user):
	finergy.db.set_value("Notification Settings", user, "seen", value, update_modified=False)