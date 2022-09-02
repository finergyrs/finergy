import finergy
from finergy import _
from finergy.utils import add_to_date, now


@finergy.whitelist()
def create_if_not_exists(doc):
	"""Create records if they dont exist.
	Will check for uniqueness by checking if a record exists with these field value pairs

	:param doc: dict of field value pairs. can be a list of dict for multiple records.
	"""

	if not finergy.local.dev_server:
		finergy.throw(_("This method can only be accessed in development"), finergy.PermissionError)

	doc = finergy.parse_json(doc)

	if not isinstance(doc, list):
		docs = [doc]
	else:
		docs = doc

	names = []
	for doc in docs:
		doc = finergy._dict(doc)
		filters = doc.copy()
		filters.pop("doctype")
		name = finergy.db.exists(doc.doctype, filters)
		if not name:
			d = finergy.get_doc(doc)
			d.insert(ignore_permissions=True)
			name = d.name
		names.append(name)

	return names


@finergy.whitelist()
def create_todo_records():
	if finergy.db.get_all("ToDo", {"description": "this is first todo"}):
		return

	finergy.get_doc(
		{"doctype": "ToDo", "date": add_to_date(now(), days=7), "description": "this is first todo"}
	).insert()
	finergy.get_doc(
		{"doctype": "ToDo", "date": add_to_date(now(), days=-7), "description": "this is second todo"}
	).insert()
	finergy.get_doc(
		{"doctype": "ToDo", "date": add_to_date(now(), months=2), "description": "this is third todo"}
	).insert()
	finergy.get_doc(
		{"doctype": "ToDo", "date": add_to_date(now(), months=-2), "description": "this is fourth todo"}
	).insert()


@finergy.whitelist()
def create_communication_record():
	doc = finergy.get_doc(
		{
			"doctype": "Communication",
			"recipients": "test@gmail.com",
			"subject": "Test Form Communication 1",
			"communication_date": finergy.utils.now_datetime(),
		}
	)
	doc.insert()
	return doc


@finergy.whitelist()
def setup_workflow():
	from finergy.workflow.doctype.workflow.test_workflow import create_todo_workflow

	create_todo_workflow()
	create_todo_records()
	finergy.clear_cache()


@finergy.whitelist()
def create_contact_phone_nos_records():
	if finergy.db.get_all("Contact", {"first_name": "Test Contact"}):
		return

	doc = finergy.new_doc("Contact")
	doc.first_name = "Test Contact"
	for index in range(1000):
		doc.append("phone_nos", {"phone": "123456{}".format(index)})
	doc.insert()


@finergy.whitelist()
def create_doctype(name, fields):
	fields = finergy.parse_json(fields)
	if finergy.db.exists("DocType", name):
		return
	finergy.get_doc(
		{
			"doctype": "DocType",
			"module": "Core",
			"custom": 1,
			"fields": fields,
			"permissions": [{"role": "System Manager", "read": 1}],
			"name": name,
		}
	).insert()


@finergy.whitelist()
def create_child_doctype(name, fields):
	fields = finergy.parse_json(fields)
	if finergy.db.exists("DocType", name):
		return
	finergy.get_doc(
		{
			"doctype": "DocType",
			"module": "Core",
			"istable": 1,
			"custom": 1,
			"fields": fields,
			"permissions": [{"role": "System Manager", "read": 1}],
			"name": name,
		}
	).insert()


@finergy.whitelist()
def create_contact_records():
	if finergy.db.get_all("Contact", {"first_name": "Test Form Contact 1"}):
		return

	insert_contact("Test Form Contact 1", "12345")
	insert_contact("Test Form Contact 2", "54321")
	insert_contact("Test Form Contact 3", "12345")


@finergy.whitelist()
def create_multiple_todo_records():
	if finergy.db.get_all("ToDo", {"description": "Multiple ToDo 1"}):
		return

	values = [("100{}".format(i), "Multiple ToDo {}".format(i)) for i in range(1, 1002)]

	finergy.db.bulk_insert("ToDo", fields=["name", "description"], values=set(values))


def insert_contact(first_name, phone_number):
	doc = finergy.get_doc({"doctype": "Contact", "first_name": first_name})
	doc.append("phone_nos", {"phone": phone_number})
	doc.insert()


@finergy.whitelist()
def create_form_tour():
	if finergy.db.exists("Form Tour", {"name": "Test Form Tour"}):
		return

	def get_docfield_name(filters):
		return finergy.db.get_value("DocField", filters, "name")

	tour = finergy.get_doc(
		{
			"doctype": "Form Tour",
			"title": "Test Form Tour",
			"reference_doctype": "Contact",
			"save_on_complete": 1,
			"steps": [
				{
					"title": "Test Title 1",
					"description": "Test Description 1",
					"has_next_condition": 1,
					"next_step_condition": "eval: doc.first_name",
					"field": get_docfield_name({"parent": "Contact", "fieldname": "first_name"}),
					"fieldname": "first_name",
					"fieldtype": "Data",
				},
				{
					"title": "Test Title 2",
					"description": "Test Description 2",
					"has_next_condition": 1,
					"next_step_condition": "eval: doc.last_name",
					"field": get_docfield_name({"parent": "Contact", "fieldname": "last_name"}),
					"fieldname": "last_name",
					"fieldtype": "Data",
				},
				{
					"title": "Test Title 3",
					"description": "Test Description 3",
					"field": get_docfield_name({"parent": "Contact", "fieldname": "phone_nos"}),
					"fieldname": "phone_nos",
					"fieldtype": "Table",
				},
				{
					"title": "Test Title 4",
					"description": "Test Description 4",
					"is_table_field": 1,
					"parent_field": get_docfield_name({"parent": "Contact", "fieldname": "phone_nos"}),
					"field": get_docfield_name({"parent": "Contact Phone", "fieldname": "phone"}),
					"next_step_condition": "eval: doc.phone",
					"has_next_condition": 1,
					"fieldname": "phone",
					"fieldtype": "Data",
				},
			],
		}
	)
	tour.insert()


@finergy.whitelist()
def create_data_for_discussions():
	web_page = create_web_page()
	create_topic_and_reply(web_page)


def create_web_page():
	web_page = finergy.db.exists("Web Page", {"route": "test-page-discussions"})
	if not web_page:
		web_page = finergy.get_doc(
			{
				"doctype": "Web Page",
				"title": "Test page for discussions",
				"route": "test-page-discussions",
				"published": True,
			}
		)
		web_page.save()

		web_page.append(
			"page_blocks",
			{
				"web_template": "Discussions",
				"web_template_values": finergy.as_json(
					{"title": "Discussions", "cta_title": "New Discussion", "docname": web_page.name}
				),
			},
		)
		web_page.save()

	return web_page


def create_topic_and_reply(web_page):
	topic = finergy.db.exists(
		"Discussion Topic", {"reference_doctype": "Web Page", "reference_docname": web_page.name}
	)

	if not topic:
		topic = finergy.get_doc(
			{
				"doctype": "Discussion Topic",
				"reference_doctype": "Web Page",
				"reference_docname": web_page.name,
				"title": "Test Topic",
			}
		)
		topic.save()

		reply = finergy.get_doc(
			{"doctype": "Discussion Reply", "topic": topic.name, "reply": "This is a test reply"}
		)

		reply.save()


@finergy.whitelist()
def update_webform_to_multistep():
	if not finergy.db.exists("Web Form", "update-profile-duplicate"):
		doc = finergy.get_doc("Web Form", "edit-profile")
		_doc = finergy.copy_doc(doc)
		_doc.is_multi_step_form = 1
		_doc.title = "update-profile-duplicate"
		_doc.route = "update-profile-duplicate"
		_doc.is_standard = False
		_doc.save()


@finergy.whitelist()
def update_child_table(name):
	doc = finergy.get_doc("DocType", name)
	if len(doc.fields) == 1:
		doc.append(
			"fields",
			{
				"fieldname": "doctype_to_link",
				"fieldtype": "Link",
				"in_list_view": 1,
				"label": "Doctype to Link",
				"options": "Doctype to Link",
			},
		)

		doc.save()


@finergy.whitelist()
def insert_translations():
	translation = [
		{
			"doctype": "Translation",
			"language": "de",
			"source_text": "Other",
			"translated_text": "Sonstiges",
		},
		{
			"doctype": "Translation",
			"language": "de",
			"source_text": "Genderqueer",
			"translated_text": "Nichtbinär",
		},
		{
			"doctype": "Translation",
			"language": "de",
			"source_text": "Non-Conforming",
			"translated_text": "Nicht konform",
		},
		{
			"doctype": "Translation",
			"language": "de",
			"source_text": "Prefer not to say",
			"translated_text": "Keine Angabe",
		},
	]

	for doc in translation:
		if not finergy.db.exists("doc"):
			finergy.get_doc(doc).insert()