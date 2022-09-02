# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import json
import unittest
from unittest.mock import patch

import finergy
import finergy.exceptions
from finergy.core.doctype.user.user import (
	extract_mentions,
	reset_password,
	sign_up,
	test_password_strength,
	update_password,
	verify_password,
)
from finergy.finergyclient import FinergyClient
from finergy.model.delete_doc import delete_doc
from finergy.utils import get_url

user_module = finergy.core.doctype.user.user
test_records = finergy.get_test_records("User")


class TestUser(unittest.TestCase):
	def tearDown(self):
		# disable password strength test
		finergy.db.set_value("System Settings", "System Settings", "enable_password_policy", 0)
		finergy.db.set_value("System Settings", "System Settings", "minimum_password_score", "")
		finergy.db.set_value("System Settings", "System Settings", "password_reset_limit", 3)
		finergy.set_user("Administrator")

	def test_user_type(self):
		new_user = finergy.get_doc(
			dict(doctype="User", email="test-for-type@example.com", first_name="Tester")
		).insert(ignore_if_duplicate=True)
		self.assertEqual(new_user.user_type, "Website User")

		# social login userid for finergy
		self.assertTrue(new_user.social_logins[0].userid)
		self.assertEqual(new_user.social_logins[0].provider, "finergy")

		# role with desk access
		new_user.add_roles("_Test Role 2")
		new_user.save()
		self.assertEqual(new_user.user_type, "System User")

		# clear role
		new_user.roles = []
		new_user.save()
		self.assertEqual(new_user.user_type, "Website User")

		# role without desk access
		new_user.add_roles("_Test Role 4")
		new_user.save()
		self.assertEqual(new_user.user_type, "Website User")

		delete_contact(new_user.name)
		finergy.delete_doc("User", new_user.name)

	def test_delete(self):
		finergy.get_doc("User", "test@example.com").add_roles("_Test Role 2")
		self.assertRaises(finergy.LinkExistsError, delete_doc, "Role", "_Test Role 2")
		finergy.db.sql("""delete from `tabHas Role` where role='_Test Role 2'""")
		delete_doc("Role", "_Test Role 2")

		if finergy.db.exists("User", "_test@example.com"):
			delete_contact("_test@example.com")
			delete_doc("User", "_test@example.com")

		user = finergy.copy_doc(test_records[1])
		user.email = "_test@example.com"
		user.insert()

		finergy.get_doc({"doctype": "ToDo", "description": "_Test"}).insert()

		delete_contact("_test@example.com")
		delete_doc("User", "_test@example.com")

		self.assertTrue(
			not finergy.db.sql("""select * from `tabToDo` where owner=%s""", ("_test@example.com",))
		)

		from finergy.core.doctype.role.test_role import test_records as role_records

		finergy.copy_doc(role_records[1]).insert()

	def test_get_value(self):
		self.assertEqual(finergy.db.get_value("User", "test@example.com"), "test@example.com")
		self.assertEqual(finergy.db.get_value("User", {"email": "test@example.com"}), "test@example.com")
		self.assertEqual(
			finergy.db.get_value("User", {"email": "test@example.com"}, "email"), "test@example.com"
		)
		self.assertEqual(
			finergy.db.get_value("User", {"email": "test@example.com"}, ["first_name", "email"]),
			("_Test", "test@example.com"),
		)
		self.assertEqual(
			finergy.db.get_value(
				"User", {"email": "test@example.com", "first_name": "_Test"}, ["first_name", "email"]
			),
			("_Test", "test@example.com"),
		)

		test_user = finergy.db.sql("select * from tabUser where name='test@example.com'", as_dict=True)[0]
		self.assertEqual(
			finergy.db.get_value("User", {"email": "test@example.com"}, "*", as_dict=True), test_user
		)

		self.assertEqual(finergy.db.get_value("User", "xxxtest@example.com"), None)

		finergy.db.set_value("Website Settings", "Website Settings", "_test", "_test_val")
		self.assertEqual(finergy.db.get_value("Website Settings", None, "_test"), "_test_val")
		self.assertEqual(
			finergy.db.get_value("Website Settings", "Website Settings", "_test"), "_test_val"
		)

	def test_high_permlevel_validations(self):
		user = finergy.get_meta("User")
		self.assertTrue("roles" in [d.fieldname for d in user.get_high_permlevel_fields()])

		me = finergy.get_doc("User", "testperm@example.com")
		me.remove_roles("System Manager")

		finergy.set_user("testperm@example.com")

		me = finergy.get_doc("User", "testperm@example.com")
		me.add_roles("System Manager")

		# system manager is not added (it is reset)
		self.assertFalse("System Manager" in [d.role for d in me.roles])

		# ignore permlevel using flags
		me.flags.ignore_permlevel_for_fields = ["roles"]
		me.add_roles("System Manager")

		# system manager now added due to flags
		self.assertTrue("System Manager" in [d.role for d in me.get("roles")])

		# reset flags
		me.flags.ignore_permlevel_for_fields = None

		# change user
		finergy.set_user("Administrator")

		me = finergy.get_doc("User", "testperm@example.com")
		me.add_roles("System Manager")

		# system manager now added by Administrator
		self.assertTrue("System Manager" in [d.role for d in me.get("roles")])

	def test_delete_user(self):
		new_user = finergy.get_doc(
			dict(doctype="User", email="test-for-delete@example.com", first_name="Tester Delete User")
		).insert(ignore_if_duplicate=True)
		self.assertEqual(new_user.user_type, "Website User")

		# role with desk access
		new_user.add_roles("_Test Role 2")
		new_user.save()
		self.assertEqual(new_user.user_type, "System User")

		comm = finergy.get_doc(
			{
				"doctype": "Communication",
				"subject": "To check user able to delete even if linked with communication",
				"content": "To check user able to delete even if linked with communication",
				"sent_or_received": "Sent",
				"user": new_user.name,
			}
		)
		comm.insert(ignore_permissions=True)

		delete_contact(new_user.name)
		finergy.delete_doc("User", new_user.name)
		self.assertFalse(finergy.db.exists("User", new_user.name))

	def test_password_strength(self):
		# Test Password without Password Strength Policy
		finergy.db.set_value("System Settings", "System Settings", "enable_password_policy", 0)

		# password policy is disabled, test_password_strength should be ignored
		result = test_password_strength("test_password")
		self.assertFalse(result.get("feedback", None))

		# Test Password with Password Strenth Policy Set
		finergy.db.set_value("System Settings", "System Settings", "enable_password_policy", 1)
		finergy.db.set_value("System Settings", "System Settings", "minimum_password_score", 2)

		# Score 1; should now fail
		result = test_password_strength("bee2ve")
		self.assertEqual(result["feedback"]["password_policy_validation_passed"], False)

		# Score 4; should pass
		result = test_password_strength("Eastern_43A1W")
		self.assertEqual(result["feedback"]["password_policy_validation_passed"], True)

		# test password strength while saving user with new password
		user = finergy.get_doc("User", "test@example.com")
		finergy.flags.in_test = False
		user.new_password = "password"
		self.assertRaisesRegex(finergy.exceptions.ValidationError, "Invalid Password", user.save)
		user.reload()
		user.new_password = "Eastern_43A1W"
		user.save()
		finergy.flags.in_test = True

	def test_comment_mentions(self):
		comment = """
			<span class="mention" data-id="test.comment@example.com" data-value="Test" data-denotation-char="@">
				<span><span class="ql-mention-denotation-char">@</span>Test</span>
			</span>
		"""
		self.assertEqual(extract_mentions(comment)[0], "test.comment@example.com")

		comment = """
			<div>
				Testing comment,
				<span class="mention" data-id="test.comment@example.com" data-value="Test" data-denotation-char="@">
					<span><span class="ql-mention-denotation-char">@</span>Test</span>
				</span>
				please check
			</div>
		"""
		self.assertEqual(extract_mentions(comment)[0], "test.comment@example.com")
		comment = """
			<div>
				Testing comment for
				<span class="mention" data-id="test_user@example.com" data-value="Test" data-denotation-char="@">
					<span><span class="ql-mention-denotation-char">@</span>Test</span>
				</span>
				and
				<span class="mention" data-id="test.again@example1.com" data-value="Test" data-denotation-char="@">
					<span><span class="ql-mention-denotation-char">@</span>Test</span>
				</span>
				please check
			</div>
		"""
		self.assertEqual(extract_mentions(comment)[0], "test_user@example.com")
		self.assertEqual(extract_mentions(comment)[1], "test.again@example1.com")

		finergy.delete_doc("User Group", "Team")
		doc = finergy.get_doc(
			{
				"doctype": "User Group",
				"name": "Team",
				"user_group_members": [{"user": "test@example.com"}, {"user": "test1@example.com"}],
			}
		)

		doc.insert()

		comment = """
			<div>
				Testing comment for
				<span class="mention" data-id="Team" data-value="Team" data-is-group="true" data-denotation-char="@">
					<span><span class="ql-mention-denotation-char">@</span>Team</span>
				</span> and
				<span class="mention" data-id="Unknown Team" data-value="Unknown Team" data-is-group="true" data-denotation-char="@">
					<span><span class="ql-mention-denotation-char">@</span>Unknown Team</span>
				</span><!-- this should be ignored-->
				please check
			</div>
		"""
		self.assertListEqual(extract_mentions(comment), ["test@example.com", "test1@example.com"])

	def test_rate_limiting_for_reset_password(self):
		# Allow only one reset request for a day
		finergy.db.set_value("System Settings", "System Settings", "password_reset_limit", 1)
		finergy.db.commit()

		url = get_url()
		data = {"cmd": "finergy.core.doctype.user.user.reset_password", "user": "test@test.com"}

		# Clear rate limit tracker to start fresh
		key = f"rl:{data['cmd']}:{data['user']}"
		finergy.cache().delete(key)

		c = FinergyClient(url)
		res1 = c.session.post(url, data=data, verify=c.verify, headers=c.headers)
		res2 = c.session.post(url, data=data, verify=c.verify, headers=c.headers)
		self.assertEqual(res1.status_code, 400)
		self.assertEqual(res2.status_code, 417)

	def test_user_rename(self):
		old_name = "test_user_rename@example.com"
		new_name = "test_user_rename_new@example.com"
		user = finergy.get_doc(
			{
				"doctype": "User",
				"email": old_name,
				"enabled": 1,
				"first_name": "_Test",
				"new_password": "Eastern_43A1W",
				"roles": [{"doctype": "Has Role", "parentfield": "roles", "role": "System Manager"}],
			}
		).insert(ignore_permissions=True, ignore_if_duplicate=True)

		finergy.rename_doc("User", user.name, new_name)
		self.assertTrue(finergy.db.exists("Notification Settings", new_name))

		finergy.delete_doc("User", new_name)

	def test_signup(self):
		import finergy.website.utils

		random_user = finergy.mock("email")
		random_user_name = finergy.mock("name")
		# disabled signup
		with patch.object(user_module, "is_signup_disabled", return_value=True):
			self.assertRaisesRegex(
				finergy.exceptions.ValidationError,
				"Sign Up is disabled",
				sign_up,
				random_user,
				random_user_name,
				"/signup",
			)

		self.assertTupleEqual(
			sign_up(random_user, random_user_name, "/welcome"),
			(1, "Please check your email for verification"),
		)
		self.assertEqual(finergy.cache().hget("redirect_after_login", random_user), "/welcome")

		# re-register
		self.assertTupleEqual(
			sign_up(random_user, random_user_name, "/welcome"), (0, "Already Registered")
		)

		# disabled user
		user = finergy.get_doc("User", random_user)
		user.enabled = 0
		user.save()

		self.assertTupleEqual(
			sign_up(random_user, random_user_name, "/welcome"), (0, "Registered but disabled")
		)

		# throttle user creation
		with patch.object(user_module.finergy.db, "get_creation_count", return_value=301):
			self.assertRaisesRegex(
				finergy.exceptions.ValidationError,
				"Throttled",
				sign_up,
				finergy.mock("email"),
				random_user_name,
				"/signup",
			)

	def test_reset_password(self):
		from finergy.auth import CookieManager, LoginManager
		from finergy.utils import set_request

		old_password = "Eastern_43A1W"
		new_password = "easy_password"

		set_request(path="/random")
		finergy.local.cookie_manager = CookieManager()
		finergy.local.login_manager = LoginManager()

		finergy.set_user("testpassword@example.com")
		test_user = finergy.get_doc("User", "testpassword@example.com")
		test_user.reset_password()
		self.assertEqual(update_password(new_password, key=test_user.reset_password_key), "/app")
		self.assertEqual(
			update_password(new_password, key="wrong_key"),
			"The Link specified has either been used before or Invalid",
		)

		# password verification should fail with old password
		self.assertRaises(finergy.exceptions.AuthenticationError, verify_password, old_password)
		verify_password(new_password)

		# reset password
		update_password(old_password, old_password=new_password)

		self.assertRaisesRegex(
			finergy.exceptions.ValidationError, "Invalid key type", update_password, "test", 1, ["like", "%"]
		)

		password_strength_response = {
			"feedback": {"password_policy_validation_passed": False, "suggestions": ["Fix password"]}
		}

		# password strength failure test
		with patch.object(
			user_module, "test_password_strength", return_value=password_strength_response
		):
			self.assertRaisesRegex(
				finergy.exceptions.ValidationError,
				"Fix password",
				update_password,
				new_password,
				0,
				test_user.reset_password_key,
			)

		# test redirect URL for website users
		finergy.set_user("test2@example.com")
		self.assertEqual(update_password(new_password, old_password=old_password), "/")
		# reset password
		update_password(old_password, old_password=new_password)

		# test API endpoint
		with patch.object(user_module.finergy, "sendmail") as sendmail:
			finergy.clear_messages()
			test_user = finergy.get_doc("User", "test2@example.com")
			self.assertEqual(reset_password(user="test2@example.com"), None)
			test_user.reload()
			self.assertEqual(update_password(new_password, key=test_user.reset_password_key), "/")
			update_password(old_password, old_password=new_password)
			self.assertEqual(
				json.loads(finergy.message_log[0]).get("message"),
				"Password reset instructions have been sent to your email",
			)

		sendmail.assert_called_once()
		self.assertEqual(sendmail.call_args[1]["recipients"], "test2@example.com")

		self.assertEqual(reset_password(user="test2@example.com"), None)
		self.assertEqual(reset_password(user="Administrator"), "not allowed")
		self.assertEqual(reset_password(user="random"), "not found")

	def test_user_onload_modules(self):
		from finergy.config import get_modules_from_all_apps
		from finergy.desk.form.load import getdoc

		finergy.response.docs = []
		getdoc("User", "Administrator")
		doc = finergy.response.docs[0]
		self.assertListEqual(
			doc.get("__onload").get("all_modules", []),
			[m.get("module_name") for m in get_modules_from_all_apps()],
		)


def delete_contact(user):
	finergy.db.sql("DELETE FROM `tabContact` WHERE `email_id`= %s", user)
	finergy.db.sql("DELETE FROM `tabContact Email` WHERE `email_id`= %s", user)