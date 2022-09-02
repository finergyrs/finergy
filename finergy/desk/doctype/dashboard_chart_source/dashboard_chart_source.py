# -*- coding: utf-8 -*-
# Copyright (c) 2019, Finergy Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import os

import finergy
from finergy import _
from finergy.model.document import Document
from finergy.modules import get_module_path, scrub
from finergy.modules.export_file import export_to_files


@finergy.whitelist()
def get_config(name):
	doc = finergy.get_doc("Dashboard Chart Source", name)
	with open(
		os.path.join(
			get_module_path(doc.module), "dashboard_chart_source", scrub(doc.name), scrub(doc.name) + ".js"
		),
		"r",
	) as f:
		return f.read()


class DashboardChartSource(Document):
	def on_update(self):
		export_to_files(
			record_list=[[self.doctype, self.name]], record_module=self.module, create_init=True
		)