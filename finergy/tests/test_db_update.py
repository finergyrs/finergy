import unittest

import finergy
from finergy.core.utils import find
from finergy.custom.doctype.property_setter.property_setter import make_property_setter
from finergy.utils import cstr


class TestDBUpdate(unittest.TestCase):
	def test_db_update(self):
		doctype = "User"
		finergy.reload_doctype("User", force=True)
		finergy.model.meta.trim_tables("User")
		make_property_setter(doctype, "bio", "fieldtype", "Text", "Data")
		make_property_setter(doctype, "middle_name", "fieldtype", "Data", "Text")
		make_property_setter(doctype, "enabled", "default", "1", "Int")

		finergy.db.updatedb(doctype)

		field_defs = get_field_defs(doctype)
		table_columns = finergy.db.get_table_columns_description("tab{}".format(doctype))

		self.assertEqual(len(field_defs), len(table_columns))

		for field_def in field_defs:
			fieldname = field_def.get("fieldname")
			table_column = find(table_columns, lambda d: d.get("name") == fieldname)

			fieldtype = get_fieldtype_from_def(field_def)

			fallback_default = (
				"0" if field_def.get("fieldtype") in finergy.model.numeric_fieldtypes else "NULL"
			)
			default = field_def.default if field_def.default is not None else fallback_default

			self.assertEqual(fieldtype, table_column.type)
			self.assertIn(cstr(table_column.default) or "NULL", [cstr(default), "'{}'".format(default)])

	def test_index_and_unique_constraints(self):
		doctype = "User"
		finergy.reload_doctype("User", force=True)
		finergy.model.meta.trim_tables("User")

		make_property_setter(doctype, "restrict_ip", "unique", "1", "Int")
		finergy.db.updatedb(doctype)
		restrict_ip_in_table = get_table_column("User", "restrict_ip")
		self.assertTrue(restrict_ip_in_table.unique)

		make_property_setter(doctype, "restrict_ip", "unique", "0", "Int")
		finergy.db.updatedb(doctype)
		restrict_ip_in_table = get_table_column("User", "restrict_ip")
		self.assertFalse(restrict_ip_in_table.unique)

		make_property_setter(doctype, "restrict_ip", "search_index", "1", "Int")
		finergy.db.updatedb(doctype)
		restrict_ip_in_table = get_table_column("User", "restrict_ip")
		self.assertTrue(restrict_ip_in_table.index)

		make_property_setter(doctype, "restrict_ip", "search_index", "0", "Int")
		finergy.db.updatedb(doctype)
		restrict_ip_in_table = get_table_column("User", "restrict_ip")
		self.assertFalse(restrict_ip_in_table.index)

		make_property_setter(doctype, "restrict_ip", "search_index", "1", "Int")
		make_property_setter(doctype, "restrict_ip", "unique", "1", "Int")
		finergy.db.updatedb(doctype)
		restrict_ip_in_table = get_table_column("User", "restrict_ip")
		self.assertTrue(restrict_ip_in_table.index)
		self.assertTrue(restrict_ip_in_table.unique)

		make_property_setter(doctype, "restrict_ip", "search_index", "1", "Int")
		make_property_setter(doctype, "restrict_ip", "unique", "0", "Int")
		finergy.db.updatedb(doctype)
		restrict_ip_in_table = get_table_column("User", "restrict_ip")
		self.assertTrue(restrict_ip_in_table.index)
		self.assertFalse(restrict_ip_in_table.unique)

		make_property_setter(doctype, "restrict_ip", "search_index", "0", "Int")
		make_property_setter(doctype, "restrict_ip", "unique", "1", "Int")
		finergy.db.updatedb(doctype)
		restrict_ip_in_table = get_table_column("User", "restrict_ip")
		self.assertFalse(restrict_ip_in_table.index)
		self.assertTrue(restrict_ip_in_table.unique)

		# explicitly make a text index
		finergy.db.add_index(doctype, ["email_signature(200)"])
		finergy.db.updatedb(doctype)
		email_sig_column = get_table_column("User", "email_signature")
		self.assertEqual(email_sig_column.index, 1)


def get_fieldtype_from_def(field_def):
	fieldtuple = finergy.db.type_map.get(field_def.fieldtype, ("", 0))
	fieldtype = fieldtuple[0]
	if fieldtype in ("varchar", "datetime", "int"):
		fieldtype += "({})".format(field_def.length or fieldtuple[1])
	return fieldtype


def get_field_defs(doctype):
	meta = finergy.get_meta(doctype, cached=False)
	field_defs = meta.get_fieldnames_with_value(True)
	field_defs += get_other_fields_meta(meta)
	return field_defs


def get_other_fields_meta(meta):
	default_fields_map = {
		"name": ("Data", 0),
		"owner": ("Data", 0),
		"parent": ("Data", 0),
		"parentfield": ("Data", 0),
		"modified_by": ("Data", 0),
		"parenttype": ("Data", 0),
		"creation": ("Datetime", 0),
		"modified": ("Datetime", 0),
		"idx": ("Int", 8),
		"docstatus": ("Check", 0),
	}

	optional_fields = finergy.db.OPTIONAL_COLUMNS
	if meta.track_seen:
		optional_fields.append("_seen")

	optional_fields_map = {field: ("Text", 0) for field in optional_fields}
	fields = dict(default_fields_map, **optional_fields_map)
	field_map = [
		finergy._dict({"fieldname": field, "fieldtype": _type, "length": _length})
		for field, (_type, _length) in fields.items()
	]

	return field_map


def get_table_column(doctype, fieldname):
	table_columns = finergy.db.get_table_columns_description("tab{}".format(doctype))
	return find(table_columns, lambda d: d.get("name") == fieldname)