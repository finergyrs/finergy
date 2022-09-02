# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import json
import os

import finergy
from finergy.model.document import Document


class ModuleDef(Document):
	def on_update(self):
		"""If in `developer_mode`, create folder for module and
		add in `modules.txt` of app if missing."""
		finergy.clear_cache()
		if not self.custom and finergy.conf.get("developer_mode"):
			self.create_modules_folder()
			self.add_to_modules_txt()

	def create_modules_folder(self):
		"""Creates a folder `[app]/[module]` and adds `__init__.py`"""
		module_path = finergy.get_app_path(self.app_name, self.name)
		if not os.path.exists(module_path):
			os.mkdir(module_path)
			with open(os.path.join(module_path, "__init__.py"), "w") as f:
				f.write("")

	def add_to_modules_txt(self):
		"""Adds to `[app]/modules.txt`"""
		modules = None
		if not finergy.local.module_app.get(finergy.scrub(self.name)):
			with open(finergy.get_app_path(self.app_name, "modules.txt"), "r") as f:
				content = f.read()
				if not self.name in content.splitlines():
					modules = list(filter(None, content.splitlines()))
					modules.append(self.name)

			if modules:
				with open(finergy.get_app_path(self.app_name, "modules.txt"), "w") as f:
					f.write("\n".join(modules))

				finergy.clear_cache()
				finergy.setup_module_map()

	def on_trash(self):
		"""Delete module name from modules.txt"""

		if not finergy.conf.get("developer_mode") or finergy.flags.in_uninstall or self.custom:
			return

		modules = None
		if finergy.local.module_app.get(finergy.scrub(self.name)):
			with open(finergy.get_app_path(self.app_name, "modules.txt"), "r") as f:
				content = f.read()
				if self.name in content.splitlines():
					modules = list(filter(None, content.splitlines()))
					modules.remove(self.name)

			if modules:
				with open(finergy.get_app_path(self.app_name, "modules.txt"), "w") as f:
					f.write("\n".join(modules))

				finergy.clear_cache()
				finergy.setup_module_map()


@finergy.whitelist()
def get_installed_apps():
	return json.dumps(finergy.get_installed_apps())