// Copyright (c) 2016, Finergy Technologies and contributors
// For license information, please see license.txt

finergy.ui.form.on('Address Template', {
	refresh: function(frm) {
		if(frm.is_new() && !frm.doc.template) {
			// set default template via js so that it is translated
			finergy.call({
				method: 'finergy.contacts.doctype.address_template.address_template.get_default_address_template',
				callback: function(r) {
					frm.set_value('template', r.message);
				}
			});
		}
	}
});