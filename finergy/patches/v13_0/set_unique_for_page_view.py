import finergy


def execute():
	finergy.reload_doc("website", "doctype", "web_page_view", force=True)
	site_url = finergy.utils.get_site_url(finergy.local.site)
	finergy.db.sql(
		"""UPDATE `tabWeb Page View` set is_unique=1 where referrer LIKE '%{0}%'""".format(site_url)
	)
