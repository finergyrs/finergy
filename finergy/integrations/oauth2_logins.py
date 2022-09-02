# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import json

import finergy
import finergy.utils
from finergy.utils.oauth import login_via_oauth2, login_via_oauth2_id_token


@finergy.whitelist(allow_guest=True)
def login_via_google(code, state):
	login_via_oauth2("google", code, state, decoder=decoder_compat)


@finergy.whitelist(allow_guest=True)
def login_via_github(code, state):
	login_via_oauth2("github", code, state)


@finergy.whitelist(allow_guest=True)
def login_via_facebook(code, state):
	login_via_oauth2("facebook", code, state, decoder=decoder_compat)


@finergy.whitelist(allow_guest=True)
def login_via_finergy(code, state):
	login_via_oauth2("finergy", code, state, decoder=decoder_compat)


@finergy.whitelist(allow_guest=True)
def login_via_office365(code, state):
	login_via_oauth2_id_token("office_365", code, state, decoder=decoder_compat)


@finergy.whitelist(allow_guest=True)
def login_via_salesforce(code, state):
	login_via_oauth2("salesforce", code, state, decoder=decoder_compat)


@finergy.whitelist(allow_guest=True)
def login_via_fairlogin(code, state):
	login_via_oauth2("fairlogin", code, state, decoder=decoder_compat)


@finergy.whitelist(allow_guest=True)
def custom(code, state):
	"""
	Callback for processing code and state for user added providers

	process social login from /api/method/finergy.integrations.custom/<provider>
	"""
	path = finergy.request.path[1:].split("/")
	if len(path) == 4 and path[3]:
		provider = path[3]
		# Validates if provider doctype exists
		if finergy.db.exists("Social Login Key", provider):
			login_via_oauth2(provider, code, state, decoder=decoder_compat)


def decoder_compat(b):
	# https://github.com/litl/rauth/issues/145#issuecomment-31199471
	return json.loads(bytes(b).decode("utf-8"))