# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import copy
import json
import os
import re

from six import string_types

import finergy
from finergy import _
from finergy.core.doctype.access_log.access_log import make_access_log
from finergy.core.doctype.document_share_key.document_share_key import is_expired
from finergy.modules import get_doc_path
from finergy.utils import cint, sanitize_html, strip_html
from finergy.utils.jinja import is_rtl

no_cache = 1

base_template_path = "templates/www/printview.html"
standard_format = "templates/print_formats/standard.html"


def get_context(context):
	"""Build context for print"""
	if not ((finergy.form_dict.doctype and finergy.form_dict.name) or finergy.form_dict.doc):
		return {
			"body": sanitize_html(
				"""<h1>Error</h1>
				<p>Parameters doctype and name required</p>
				<pre>%s</pre>"""
				% repr(finergy.form_dict)
			)
		}

	if finergy.form_dict.doc:
		doc = finergy.form_dict.doc
	else:
		doc = finergy.get_doc(finergy.form_dict.doctype, finergy.form_dict.name)

	settings = finergy.parse_json(finergy.form_dict.settings)

	letterhead = finergy.form_dict.letterhead or None

	meta = finergy.get_meta(doc.doctype)

	print_format = get_print_format_doc(None, meta=meta)

	make_access_log(
		doctype=finergy.form_dict.doctype, document=finergy.form_dict.name, file_type="PDF", method="Print"
	)

	is_invalid_print = False
	print_style = None
	try:
		body = get_rendered_template(
			doc,
			print_format=print_format,
			meta=meta,
			trigger_print=finergy.form_dict.trigger_print,
			no_letterhead=finergy.form_dict.no_letterhead,
			letterhead=letterhead,
			settings=settings,
		)
		print_style = get_print_style(finergy.form_dict.style, print_format)
	except finergy.exceptions.LinkExpired:
		body = finergy.get_template("templates/print_formats/print_key_expired.html").render({})
		context.http_status_code = 410
		is_invalid_print = True
	except finergy.exceptions.InvalidKeyError:
		body = finergy.get_template("templates/print_formats/print_key_invalid.html").render({})
		context.http_status_code = 401
		is_invalid_print = True

	return {
		"body": body,
		"print_style": print_style,
		"comment": finergy.session.user,
		"title": finergy.utils.strip_html(doc.get_title() or doc.name),
		"lang": finergy.local.lang,
		"layout_direction": "rtl" if is_rtl() else "ltr",
		"is_invalid_print": is_invalid_print,
		"doctype": finergy.form_dict.doctype,
		"name": finergy.form_dict.name,
		"key": finergy.form_dict.get("key"),
	}


def get_print_format_doc(print_format_name, meta):
	"""Returns print format document"""
	if not print_format_name:
		print_format_name = finergy.form_dict.format or meta.default_print_format or "Standard"

	if print_format_name == "Standard":
		return None
	else:
		try:
			return finergy.get_doc("Print Format", print_format_name)
		except finergy.DoesNotExistError:
			# if old name, return standard!
			return None


def get_rendered_template(
	doc,
	name=None,
	print_format=None,
	meta=None,
	no_letterhead=None,
	letterhead=None,
	trigger_print=False,
	settings=None,
):

	print_settings = finergy.get_single("Print Settings").as_dict()
	print_settings.update(settings or {})

	if isinstance(no_letterhead, string_types):
		no_letterhead = cint(no_letterhead)

	elif no_letterhead is None:
		no_letterhead = not cint(print_settings.with_letterhead)

	doc.flags.in_print = True
	doc.flags.print_settings = print_settings

	if not finergy.flags.ignore_print_permissions:
		validate_print_permission(doc)

	if doc.meta.is_submittable:
		if doc.docstatus == 0 and not cint(print_settings.allow_print_for_draft):
			finergy.throw(_("Not allowed to print draft documents"), finergy.PermissionError)

		if doc.docstatus == 2 and not cint(print_settings.allow_print_for_cancelled):
			finergy.throw(_("Not allowed to print cancelled documents"), finergy.PermissionError)

	doc.run_method("before_print", print_settings)

	if not hasattr(doc, "print_heading"):
		doc.print_heading = None
	if not hasattr(doc, "sub_heading"):
		doc.sub_heading = None

	if not meta:
		meta = finergy.get_meta(doc.doctype)

	jenv = finergy.get_jenv()
	format_data, format_data_map = [], {}

	# determine template
	if print_format:
		doc.print_section_headings = print_format.show_section_headings
		doc.print_line_breaks = print_format.line_breaks
		doc.align_labels_right = print_format.align_labels_right
		doc.absolute_value = print_format.absolute_value

		def get_template_from_string():
			return jenv.from_string(get_print_format(doc.doctype, print_format))

		if print_format.custom_format:
			template = get_template_from_string()

		elif print_format.format_data:
			# set format data
			format_data = json.loads(print_format.format_data)
			for df in format_data:
				format_data_map[df.get("fieldname")] = df
				if "visible_columns" in df:
					for _df in df.get("visible_columns"):
						format_data_map[_df.get("fieldname")] = _df

			doc.format_data_map = format_data_map

			template = "standard"

		elif print_format.standard == "Yes":
			template = get_template_from_string()

		else:
			# fallback
			template = "standard"

	else:
		template = "standard"

	if template == "standard":
		template = jenv.get_template(standard_format)

	letter_head = finergy._dict(get_letter_head(doc, no_letterhead, letterhead) or {})

	if letter_head.content:
		letter_head.content = finergy.utils.jinja.render_template(
			letter_head.content, {"doc": doc.as_dict()}
		)

	if letter_head.footer:
		letter_head.footer = finergy.utils.jinja.render_template(
			letter_head.footer, {"doc": doc.as_dict()}
		)

	convert_markdown(doc, meta)

	args = {}
	# extract `print_heading_template` from the first field and remove it
	if format_data and format_data[0].get("fieldname") == "print_heading_template":
		args["print_heading_template"] = format_data.pop(0).get("options")

	args.update(
		{
			"doc": doc,
			"meta": finergy.get_meta(doc.doctype),
			"layout": make_layout(doc, meta, format_data),
			"no_letterhead": no_letterhead,
			"trigger_print": cint(trigger_print),
			"letter_head": letter_head.content,
			"footer": letter_head.footer,
			"print_settings": print_settings,
		}
	)

	html = template.render(args, filters={"len": len})

	if cint(trigger_print):
		html += trigger_print_script

	return html


def convert_markdown(doc, meta):
	"""Convert text field values to markdown if necessary"""
	for field in meta.fields:
		if field.fieldtype == "Text Editor":
			value = doc.get(field.fieldname)
			if value and "<!-- markdown -->" in value:
				doc.set(field.fieldname, finergy.utils.md_to_html(value))


@finergy.whitelist()
def get_html_and_style(
	doc,
	name=None,
	print_format=None,
	meta=None,
	no_letterhead=None,
	letterhead=None,
	trigger_print=False,
	style=None,
	settings=None,
	templates=None,
):
	"""Returns `html` and `style` of print format, used in PDF etc"""

	if isinstance(doc, string_types) and isinstance(name, string_types):
		doc = finergy.get_doc(doc, name)

	if isinstance(doc, string_types):
		doc = finergy.get_doc(json.loads(doc))

	print_format = get_print_format_doc(print_format, meta=meta or finergy.get_meta(doc.doctype))

	try:
		html = get_rendered_template(
			doc,
			name=name,
			print_format=print_format,
			meta=meta,
			no_letterhead=no_letterhead,
			letterhead=letterhead,
			trigger_print=trigger_print,
			settings=finergy.parse_json(settings),
		)
	except finergy.TemplateNotFoundError:
		finergy.clear_last_message()
		html = None

	return {"html": html, "style": get_print_style(style=style, print_format=print_format)}


@finergy.whitelist()
def get_rendered_raw_commands(doc, name=None, print_format=None, meta=None, lang=None):
	"""Returns Rendered Raw Commands of print format, used to send directly to printer"""

	if isinstance(doc, string_types) and isinstance(name, string_types):
		doc = finergy.get_doc(doc, name)

	if isinstance(doc, string_types):
		doc = finergy.get_doc(json.loads(doc))

	print_format = get_print_format_doc(print_format, meta=meta or finergy.get_meta(doc.doctype))

	if not print_format or (print_format and not print_format.raw_printing):
		finergy.throw(
			_("{0} is not a raw printing format.").format(print_format), finergy.TemplateNotFoundError
		)

	return {
		"raw_commands": get_rendered_template(doc, name=name, print_format=print_format, meta=meta)
	}


def validate_print_permission(doc):
	for ptype in ("read", "print"):
		if finergy.has_permission(doc.doctype, ptype, doc) or finergy.has_website_permission(doc):
			return

	key = finergy.form_dict.get("key")
	if key:
		validate_key(key, doc)
	else:
		raise finergy.PermissionError(_("You do not have permission to view this document"))


def validate_key(key, doc):
	try:
		document_key_expiry = finergy.get_cached_value(
			"Document Share Key",
			{"reference_doctype": doc.doctype, "reference_docname": doc.name, "key": key},
			"expires_on",
		)
		if is_expired(document_key_expiry):
			raise finergy.exceptions.LinkExpired
		else:
			return
	except finergy.DoesNotExistError:
		finergy.clear_last_message()

	# TODO: Deprecate this! kept it for backward compatibility
	if finergy.get_system_settings("allow_older_web_view_links") and key == doc.get_signature():
		return

	raise finergy.exceptions.InvalidKeyError


def get_letter_head(doc, no_letterhead, letterhead=None):
	if no_letterhead:
		return {}
	if letterhead:
		return finergy.db.get_value("Letter Head", letterhead, ["content", "footer"], as_dict=True)
	if doc.get("letter_head"):
		return finergy.db.get_value("Letter Head", doc.letter_head, ["content", "footer"], as_dict=True)
	else:
		return (
			finergy.db.get_value("Letter Head", {"is_default": 1}, ["content", "footer"], as_dict=True) or {}
		)


def get_print_format(doctype, print_format):
	if print_format.disabled:
		finergy.throw(
			_("Print Format {0} is disabled").format(print_format.name), finergy.DoesNotExistError
		)

	# server, find template
	path = os.path.join(
		get_doc_path(
			finergy.db.get_value("DocType", doctype, "module"), "Print Format", print_format.name
		),
		finergy.scrub(print_format.name) + ".html",
	)

	if os.path.exists(path):
		with open(path, "r") as pffile:
			return pffile.read()
	else:
		if print_format.raw_printing:
			return print_format.raw_commands
		if print_format.html:
			return print_format.html

		finergy.throw(_("No template found at path: {0}").format(path), finergy.TemplateNotFoundError)


def make_layout(doc, meta, format_data=None):
	"""Builds a hierarchical layout object from the fields list to be rendered
	by `standard.html`

	:param doc: Document to be rendered.
	:param meta: Document meta object (doctype).
	:param format_data: Fields sequence and properties defined by Print Format Builder."""
	layout, page = [], []
	layout.append(page)

	def get_new_section():
		return {"columns": [], "has_data": False}

	def append_empty_field_dict_to_page_column(page):
		"""append empty columns dict to page layout"""
		if not page[-1]["columns"]:
			page[-1]["columns"].append({"fields": []})

	for df in format_data or meta.fields:
		if format_data:
			# embellish df with original properties
			df = finergy._dict(df)
			if df.fieldname:
				original = meta.get_field(df.fieldname)
				if original:
					newdf = original.as_dict()
					newdf.hide_in_print_layout = original.get("hide_in_print_layout")
					newdf.update(df)
					df = newdf

			df.print_hide = 0

		if df.fieldtype == "Section Break" or page == []:
			if len(page) > 1:
				if page[-1]["has_data"] == False:
					# truncate last section if empty
					del page[-1]

			section = get_new_section()
			if df.fieldtype == "Section Break" and df.label:
				section["label"] = df.label

			page.append(section)

		elif df.fieldtype == "Column Break":
			# if last column break and last column is not empty
			page[-1]["columns"].append({"fields": []})

		else:
			# add a column if not yet added
			append_empty_field_dict_to_page_column(page)

		if df.fieldtype == "HTML" and df.options:
			doc.set(df.fieldname, True)  # show this field

		if df.fieldtype == "Signature" and not doc.get(df.fieldname):
			placeholder_image = "/assets/finergyrs/images/signature-placeholder.png"
			doc.set(df.fieldname, placeholder_image)

		if is_visible(df, doc) and has_value(df, doc):
			append_empty_field_dict_to_page_column(page)

			page[-1]["columns"][-1]["fields"].append(df)

			# section has fields
			page[-1]["has_data"] = True

			# if table, add the row info in the field
			# if a page break is found, create a new docfield
			if df.fieldtype == "Table":
				df.rows = []
				df.start = 0
				df.end = None
				for i, row in enumerate(doc.get(df.fieldname)):
					if row.get("page_break"):
						# close the earlier row
						df.end = i

						# new page, with empty section and column
						page = [get_new_section()]
						layout.append(page)
						append_empty_field_dict_to_page_column(page)

						# continue the table in a new page
						df = copy.copy(df)
						df.start = i
						df.end = None
						page[-1]["columns"][-1]["fields"].append(df)

	return layout


def is_visible(df, doc):
	"""Returns True if docfield is visible in print layout and does not have print_hide set."""
	if df.fieldtype in ("Section Break", "Column Break", "Button"):
		return False

	if (df.permlevel or 0) > 0 and not doc.has_permlevel_access_to(df.fieldname, df):
		return False

	return not doc.is_print_hide(df.fieldname, df)


def has_value(df, doc):
	value = doc.get(df.fieldname)
	if value in (None, ""):
		return False

	elif isinstance(value, string_types) and not strip_html(value).strip():
		if df.fieldtype in ["Text", "Text Editor"]:
			return True

		return False

	elif isinstance(value, list) and not len(value):
		return False

	return True


def get_print_style(style=None, print_format=None, for_legacy=False):
	print_settings = finergy.get_doc("Print Settings")

	if not style:
		style = print_settings.print_style or ""

	context = {
		"print_settings": print_settings,
		"print_style": style,
		"font": get_font(print_settings, print_format, for_legacy),
	}

	css = finergy.get_template("templates/styles/standard.css").render(context)

	if style and finergy.db.exists("Print Style", style):
		css = css + "\n" + finergy.db.get_value("Print Style", style, "css")

	# move @import to top
	for at_import in list(set(re.findall(r"(@import url\([^\)]+\)[;]?)", css))):
		css = css.replace(at_import, "")

		# prepend css with at_import
		css = at_import + css

	if print_format and print_format.css:
		css += "\n\n" + print_format.css

	return css


def get_font(print_settings, print_format=None, for_legacy=False):
	default = 'Inter, "Helvetica Neue", Helvetica, Arial, "Open Sans", sans-serif'
	if for_legacy:
		return default

	font = None
	if print_format:
		if print_format.font and print_format.font != "Default":
			font = "{0}, sans-serif".format(print_format.font)

	if not font:
		if print_settings.font and print_settings.font != "Default":
			font = "{0}, sans-serif".format(print_settings.font)

		else:
			font = default

	return font


def get_visible_columns(data, table_meta, df):
	"""Returns list of visible columns based on print_hide and if all columns have value."""
	columns = []
	doc = data[0] or finergy.new_doc(df.options)

	hide_in_print_layout = df.get("hide_in_print_layout") or []

	def add_column(col_df):
		if col_df.fieldname in hide_in_print_layout:
			return False
		return is_visible(col_df, doc) and column_has_value(data, col_df.get("fieldname"), col_df)

	if df.get("visible_columns"):
		# columns specified by column builder
		for col_df in df.get("visible_columns"):
			# load default docfield properties
			docfield = table_meta.get_field(col_df.get("fieldname"))
			if not docfield:
				continue
			newdf = docfield.as_dict().copy()
			newdf.update(col_df)
			if add_column(newdf):
				columns.append(newdf)
	else:
		for col_df in table_meta.fields:
			if add_column(col_df):
				columns.append(col_df)

	return columns


def column_has_value(data, fieldname, col_df):
	"""Check if at least one cell in column has non-zero and non-blank value"""
	has_value = False

	if col_df.fieldtype in ["Float", "Currency"] and not col_df.print_hide_if_no_value:
		return True

	for row in data:
		value = row.get(fieldname)
		if value:
			if isinstance(value, string_types):
				if strip_html(value).strip():
					has_value = True
					break
			else:
				has_value = True
				break

	return has_value


trigger_print_script = """
<script>
//allow wrapping of long tr
var elements = document.getElementsByTagName("tr");
var i = elements.length;
while (i--) {
	if(elements[i].clientHeight>300){
		elements[i].setAttribute("style", "page-break-inside: auto;");
	}
}

window.print();

// close the window after print
// NOTE: doesn't close if print is cancelled in Chrome
// Changed timeout to 5s from 1s because it blocked mobile view rendering
setTimeout(function() {
	window.close();
}, 5000);
</script>
"""