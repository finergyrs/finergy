from __future__ import unicode_literals

from . import __version__ as app_version

app_name = "finergy"
app_title = "Finergy Framework"
app_publisher = "Finergy Technologies"
app_description = "Full stack web framework with Python, Javascript, MariaDB, Redis, Node"
app_icon = "octicon octicon-circuit-board"
app_color = "orange"
source_link = "https://github.com/finergyrs/finergy"
app_license = "MIT"
app_logo_url = "/assets/finergyrs/images/finergy-framework-logo.svg"

develop_version = "13.x.x-develop"

app_email = "info@finergy-rs.fr"

docs_app = "finergy_io"

translator_url = "https://translate.capkpi.com"

before_install = "finergy.utils.install.before_install"
after_install = "finergy.utils.install.after_install"

page_js = {"setup-wizard": "public/js/finergyrs/setup_wizard.js"}

# website
app_include_js = [
	"/assets/js/libs.min.js",
	"/assets/js/desk.min.js",
	"/assets/js/list.min.js",
	"/assets/js/form.min.js",
	"/assets/js/control.min.js",
	"/assets/js/report.min.js",
]
app_include_css = [
	"/assets/css/desk.min.css",
	"/assets/css/report.min.css",
]

doctype_js = {
	"Web Page": "public/js/finergyrs/utils/web_template.js",
	"Website Settings": "public/js/finergyrs/utils/web_template.js",
}

web_include_js = ["website_script.js"]

web_include_css = []

website_route_rules = [
	{"from_route": "/blog/<category>", "to_route": "Blog Post"},
	{"from_route": "/kb/<category>", "to_route": "Help Article"},
	{"from_route": "/newsletters", "to_route": "Newsletter"},
	{"from_route": "/profile", "to_route": "me"},
	{"from_route": "/app/<path:app_path>", "to_route": "app"},
]

website_redirects = [
	{"source": r"/desk(.*)", "target": r"/app\1"},
]

base_template = "templates/base.html"

write_file_keys = ["file_url", "file_name"]

notification_config = "finergy.core.notifications.get_notification_config"

before_tests = "finergy.utils.install.before_tests"

email_append_to = ["Event", "ToDo", "Communication"]


calendars = ["Event"]

leaderboards = "finergy.desk.leaderboard.get_leaderboards"

# login

on_session_creation = [
	"finergy.core.doctype.activity_log.feed.login_feed",
	"finergy.core.doctype.user.user.notify_admin_access_to_system_manager",
]

on_logout = (
	"finergy.core.doctype.session_default_settings.session_default_settings.clear_session_defaults"
)

# permissions

permission_query_conditions = {
	"Event": "finergy.desk.doctype.event.event.get_permission_query_conditions",
	"ToDo": "finergy.desk.doctype.todo.todo.get_permission_query_conditions",
	"User": "finergy.core.doctype.user.user.get_permission_query_conditions",
	"Dashboard Settings": "finergy.desk.doctype.dashboard_settings.dashboard_settings.get_permission_query_conditions",
	"Notification Log": "finergy.desk.doctype.notification_log.notification_log.get_permission_query_conditions",
	"Dashboard": "finergy.desk.doctype.dashboard.dashboard.get_permission_query_conditions",
	"Dashboard Chart": "finergy.desk.doctype.dashboard_chart.dashboard_chart.get_permission_query_conditions",
	"Number Card": "finergy.desk.doctype.number_card.number_card.get_permission_query_conditions",
	"Notification Settings": "finergy.desk.doctype.notification_settings.notification_settings.get_permission_query_conditions",
	"Note": "finergy.desk.doctype.note.note.get_permission_query_conditions",
	"Kanban Board": "finergy.desk.doctype.kanban_board.kanban_board.get_permission_query_conditions",
	"Contact": "finergy.contacts.address_and_contact.get_permission_query_conditions_for_contact",
	"Address": "finergy.contacts.address_and_contact.get_permission_query_conditions_for_address",
	"Communication": "finergy.core.doctype.communication.communication.get_permission_query_conditions_for_communication",
	"Workflow Action": "finergy.workflow.doctype.workflow_action.workflow_action.get_permission_query_conditions",
	"Prepared Report": "finergy.core.doctype.prepared_report.prepared_report.get_permission_query_condition",
}

has_permission = {
	"Event": "finergy.desk.doctype.event.event.has_permission",
	"ToDo": "finergy.desk.doctype.todo.todo.has_permission",
	"User": "finergy.core.doctype.user.user.has_permission",
	"Note": "finergy.desk.doctype.note.note.has_permission",
	"Dashboard Chart": "finergy.desk.doctype.dashboard_chart.dashboard_chart.has_permission",
	"Number Card": "finergy.desk.doctype.number_card.number_card.has_permission",
	"Kanban Board": "finergy.desk.doctype.kanban_board.kanban_board.has_permission",
	"Contact": "finergy.contacts.address_and_contact.has_permission",
	"Address": "finergy.contacts.address_and_contact.has_permission",
	"Communication": "finergy.core.doctype.communication.communication.has_permission",
	"Workflow Action": "finergy.workflow.doctype.workflow_action.workflow_action.has_permission",
	"File": "finergy.core.doctype.file.file.has_permission",
	"Prepared Report": "finergy.core.doctype.prepared_report.prepared_report.has_permission",
}

has_website_permission = {
	"Address": "finergy.contacts.doctype.address.address.has_website_permission"
}

standard_queries = {"User": "finergy.core.doctype.user.user.user_query"}

doc_events = {
	"*": {
		"after_insert": [
			"finergy.event_streaming.doctype.event_update_log.event_update_log.notify_consumers"
		],
		"on_update": [
			"finergy.desk.notifications.clear_doctype_notifications",
			"finergy.core.doctype.activity_log.feed.update_feed",
			"finergy.workflow.doctype.workflow_action.workflow_action.process_workflow_actions",
			"finergy.automation.doctype.assignment_rule.assignment_rule.apply",
			"finergy.core.doctype.file.file.attach_files_to_document",
			"finergy.event_streaming.doctype.event_update_log.event_update_log.notify_consumers",
			"finergy.automation.doctype.assignment_rule.assignment_rule.update_due_date",
			"finergy.core.doctype.user_type.user_type.apply_permissions_for_non_standard_user_type",
		],
		"after_rename": "finergy.desk.notifications.clear_doctype_notifications",
		"on_cancel": [
			"finergy.desk.notifications.clear_doctype_notifications",
			"finergy.workflow.doctype.workflow_action.workflow_action.process_workflow_actions",
			"finergy.event_streaming.doctype.event_update_log.event_update_log.notify_consumers",
		],
		"on_trash": [
			"finergy.desk.notifications.clear_doctype_notifications",
			"finergy.workflow.doctype.workflow_action.workflow_action.process_workflow_actions",
			"finergy.event_streaming.doctype.event_update_log.event_update_log.notify_consumers",
		],
		"on_update_after_submit": [
			"finergy.workflow.doctype.workflow_action.workflow_action.process_workflow_actions"
		],
		"on_change": [
			"finergy.social.doctype.energy_point_rule.energy_point_rule.process_energy_points",
			"finergy.automation.doctype.milestone_tracker.milestone_tracker.evaluate_milestone",
		],
	},
	"Event": {
		"after_insert": "finergy.integrations.doctype.google_calendar.google_calendar.insert_event_in_google_calendar",
		"on_update": "finergy.integrations.doctype.google_calendar.google_calendar.update_event_in_google_calendar",
		"on_trash": "finergy.integrations.doctype.google_calendar.google_calendar.delete_event_from_google_calendar",
	},
	"Contact": {
		"after_insert": "finergy.integrations.doctype.google_contacts.google_contacts.insert_contacts_to_google_contacts",
		"on_update": "finergy.integrations.doctype.google_contacts.google_contacts.update_contacts_to_google_contacts",
	},
	"DocType": {
		"after_insert": "finergy.cache_manager.build_domain_restriced_doctype_cache",
		"after_save": "finergy.cache_manager.build_domain_restriced_doctype_cache",
	},
	"Page": {
		"after_insert": "finergy.cache_manager.build_domain_restriced_page_cache",
		"after_save": "finergy.cache_manager.build_domain_restriced_page_cache",
	},
}

scheduler_events = {
	"cron": {
		"0/15 * * * *": [
			"finergy.oauth.delete_oauth2_data",
			"finergy.website.doctype.web_page.web_page.check_publish_status",
			"finergy.twofactor.delete_all_barcodes_for_users",
		]
	},
	"all": [
		"finergy.email.queue.flush",
		"finergy.email.doctype.email_account.email_account.pull",
		"finergy.email.doctype.email_account.email_account.notify_unreplied",
		"finergy.integrations.doctype.razorpay_settings.razorpay_settings.capture_payment",
		"finergy.utils.global_search.sync_global_search",
		"finergy.monitor.flush",
	],
	"hourly": [
		"finergy.model.utils.link_count.update_link_count",
		"finergy.model.utils.user_settings.sync_user_settings",
		"finergy.utils.error.collect_error_snapshots",
		"finergy.desk.page.backups.backups.delete_downloadable_backups",
		"finergy.deferred_insert.save_to_db",
		"finergy.desk.form.document_follow.send_hourly_updates",
		"finergy.integrations.doctype.google_calendar.google_calendar.sync",
		"finergy.email.doctype.newsletter.newsletter.send_scheduled_email",
	],
	"daily": [
		"finergy.email.queue.set_expiry_for_email_queue",
		"finergy.desk.notifications.clear_notifications",
		"finergy.core.doctype.error_log.error_log.set_old_logs_as_seen",
		"finergy.desk.doctype.event.event.send_event_digest",
		"finergy.sessions.clear_expired_sessions",
		"finergy.email.doctype.notification.notification.trigger_daily_alerts",
		"finergy.utils.scheduler.restrict_scheduler_events_if_dormant",
		"finergy.website.doctype.personal_data_deletion_request.personal_data_deletion_request.remove_unverified_record",
		"finergy.desk.form.document_follow.send_daily_updates",
		"finergy.social.doctype.energy_point_settings.energy_point_settings.allocate_review_points",
		"finergy.integrations.doctype.google_contacts.google_contacts.sync",
		"finergy.automation.doctype.auto_repeat.auto_repeat.make_auto_repeat_entry",
		"finergy.automation.doctype.auto_repeat.auto_repeat.set_auto_repeat_as_completed",
		"finergy.email.doctype.unhandled_email.unhandled_email.remove_old_unhandled_emails",
		"finergy.core.doctype.prepared_report.prepared_report.delete_expired_prepared_reports",
		"finergy.core.doctype.log_settings.log_settings.run_log_clean_up",
	],
	"daily_long": [
		"finergy.integrations.doctype.dropbox_settings.dropbox_settings.take_backups_daily",
		"finergy.utils.change_log.check_for_update",
		"finergy.integrations.doctype.s3_backup_settings.s3_backup_settings.take_backups_daily",
		"finergy.email.doctype.auto_email_report.auto_email_report.send_daily",
		"finergy.integrations.doctype.google_drive.google_drive.daily_backup",
	],
	"weekly_long": [
		"finergy.integrations.doctype.dropbox_settings.dropbox_settings.take_backups_weekly",
		"finergy.integrations.doctype.s3_backup_settings.s3_backup_settings.take_backups_weekly",
		"finergy.desk.doctype.route_history.route_history.flush_old_route_records",
		"finergy.desk.form.document_follow.send_weekly_updates",
		"finergy.social.doctype.energy_point_log.energy_point_log.send_weekly_summary",
		"finergy.integrations.doctype.google_drive.google_drive.weekly_backup",
	],
	"monthly": [
		"finergy.email.doctype.auto_email_report.auto_email_report.send_monthly",
		"finergy.social.doctype.energy_point_log.energy_point_log.send_monthly_summary",
	],
	"monthly_long": [
		"finergy.integrations.doctype.s3_backup_settings.s3_backup_settings.take_backups_monthly"
	],
}

get_translated_dict = {
	("doctype", "System Settings"): "finergy.geo.country_info.get_translated_dict",
	("page", "setup-wizard"): "finergy.geo.country_info.get_translated_dict",
}

sounds = [
	{"name": "email", "src": "/assets/finergyrs/sounds/email.mp3", "volume": 0.1},
	{"name": "submit", "src": "/assets/finergyrs/sounds/submit.mp3", "volume": 0.1},
	{"name": "cancel", "src": "/assets/finergyrs/sounds/cancel.mp3", "volume": 0.1},
	{"name": "delete", "src": "/assets/finergyrs/sounds/delete.mp3", "volume": 0.05},
	{"name": "click", "src": "/assets/finergyrs/sounds/click.mp3", "volume": 0.05},
	{"name": "error", "src": "/assets/finergyrs/sounds/error.mp3", "volume": 0.1},
	{"name": "alert", "src": "/assets/finergyrs/sounds/alert.mp3", "volume": 0.2},
	# {"name": "chime", "src": "/assets/finergyrs/sounds/chime.mp3"},
]

bot_parsers = [
	"finergy.utils.bot.ShowNotificationBot",
	"finergy.utils.bot.GetOpenListBot",
	"finergy.utils.bot.ListBot",
	"finergy.utils.bot.FindBot",
	"finergy.utils.bot.CountBot",
]

setup_wizard_exception = [
	"finergy.desk.page.setup_wizard.setup_wizard.email_setup_wizard_exception",
	"finergy.desk.page.setup_wizard.setup_wizard.log_setup_wizard_exception",
]

before_migrate = []
after_migrate = ["finergy.website.doctype.website_theme.website_theme.after_migrate"]

otp_methods = ["OTP App", "Email", "SMS"]

user_data_fields = [
	{"doctype": "Access Log", "strict": True},
	{"doctype": "Activity Log", "strict": True},
	{"doctype": "Comment", "strict": True},
	{
		"doctype": "Contact",
		"filter_by": "email_id",
		"redact_fields": ["first_name", "last_name", "phone", "mobile_no"],
		"rename": True,
	},
	{"doctype": "Contact Email", "filter_by": "email_id"},
	{
		"doctype": "Address",
		"filter_by": "email_id",
		"redact_fields": [
			"address_title",
			"address_line1",
			"address_line2",
			"city",
			"county",
			"state",
			"pincode",
			"phone",
			"fax",
		],
	},
	{
		"doctype": "Communication",
		"filter_by": "sender",
		"redact_fields": ["sender_full_name", "phone_no", "content"],
	},
	{"doctype": "Communication", "filter_by": "recipients"},
	{"doctype": "Email Group Member", "filter_by": "email"},
	{"doctype": "Email Unsubscribe", "filter_by": "email", "partial": True},
	{"doctype": "Email Queue", "filter_by": "sender"},
	{"doctype": "Email Queue Recipient", "filter_by": "recipient"},
	{
		"doctype": "File",
		"filter_by": "attached_to_name",
		"redact_fields": ["file_name", "file_url"],
	},
	{
		"doctype": "User",
		"filter_by": "name",
		"redact_fields": [
			"email",
			"username",
			"first_name",
			"middle_name",
			"last_name",
			"full_name",
			"birth_date",
			"user_image",
			"phone",
			"mobile_no",
			"location",
			"banner_image",
			"interest",
			"bio",
			"email_signature",
		],
	},
	{"doctype": "Version", "strict": True},
]

global_search_doctypes = {
	"Default": [
		{"doctype": "Contact"},
		{"doctype": "Address"},
		{"doctype": "ToDo"},
		{"doctype": "Note"},
		{"doctype": "Event"},
		{"doctype": "Blog Post"},
		{"doctype": "Dashboard"},
		{"doctype": "Country"},
		{"doctype": "Currency"},
		{"doctype": "Newsletter"},
		{"doctype": "Letter Head"},
		{"doctype": "Workflow"},
		{"doctype": "Web Page"},
		{"doctype": "Web Form"},
	]
}