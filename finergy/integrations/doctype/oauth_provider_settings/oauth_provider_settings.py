# -*- coding: utf-8 -*-
# Copyright (c) 2015, Finergy Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import finergy
from finergy import _
from finergy.model.document import Document


class OAuthProviderSettings(Document):
	pass


def get_oauth_settings():
	"""Returns oauth settings"""
	out = finergy._dict(
		{
			"skip_authorization": finergy.db.get_value("OAuth Provider Settings", None, "skip_authorization")
		}
	)

	return out
