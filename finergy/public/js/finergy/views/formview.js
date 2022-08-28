// Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
// MIT License. See license.txt

finergy.provide('finergy.views.formview');

finergy.views.FormFactory = class FormFactory extends finergy.views.Factory {
	make(route) {
		var doctype = route[1],
			doctype_layout = finergy.router.doctype_layout || doctype;

		if (!finergy.views.formview[doctype_layout]) {
			finergy.model.with_doctype(doctype, () => {
				this.page = finergy.container.add_page(doctype_layout);
				finergy.views.formview[doctype_layout] = this.page;
				this.make_and_show(doctype, route);
			});
		} else {
			this.show_doc(route);
		}

		this.setup_events();
	}

	make_and_show(doctype, route) {
		if (finergy.router.doctype_layout) {
			finergy.model.with_doc('DocType Layout', finergy.router.doctype_layout, () => {
				this.make_form(doctype);
				this.show_doc(route);
			});
		} else {
			this.make_form(doctype);
			this.show_doc(route);
		}
	}

	make_form(doctype) {
		this.page.frm = new finergy.ui.form.Form(doctype, this.page, true, finergy.router.doctype_layout);
	}

	setup_events() {
		if (!this.initialized) {
			$(document).on("page-change", function() {
				finergy.ui.form.close_grid_form();
			});

			finergy.realtime.on("doc_viewers", function(data) {
				// set users that currently viewing the form
				finergy.ui.form.FormViewers.set_users(data, 'viewers');
			});

			finergy.realtime.on("doc_typers", function(data) {
				// set users that currently typing on the form
				finergy.ui.form.FormViewers.set_users(data, 'typers');
			});
		}
		this.initialized = true;
	}

	show_doc(route) {
		var doctype = route[1],
			doctype_layout = finergy.router.doctype_layout || doctype,
			name = route.slice(2).join("/");

		if (finergy.model.new_names[name]) {
			// document has been renamed, reroute
			name = finergy.model.new_names[name];
			finergy.set_route("Form", doctype_layout, name);
			return;
		}

		const doc = finergy.get_doc(doctype, name);
		if (doc && finergy.model.get_docinfo(doctype, name) && (doc.__islocal || finergy.model.is_fresh(doc))) {
			// is document available and recent?
			this.render(doctype_layout, name);
		} else {
			this.fetch_and_render(doctype, name, doctype_layout);
		}
	}

	fetch_and_render(doctype, name, doctype_layout) {
		finergy.model.with_doc(doctype, name, (name, r) => {
			if (r && r['403']) return; // not permitted

			if (!(locals[doctype] && locals[doctype][name])) {
				if (name && name.substr(0, 3) === 'new') {
					this.render_new_doc(doctype, name, doctype_layout);
				} else {
					finergy.show_not_found();
				}
				return;
			}
			this.render(doctype_layout, name);
		});
	}

	render_new_doc(doctype, name, doctype_layout) {
		const new_name = finergy.model.make_new_doc_and_get_name(doctype, true);
		if (new_name===name) {
			this.render(doctype_layout, name);
		} else {
			finergy.route_flags.replace_route = true;
			finergy.set_route("Form", doctype_layout, new_name);
		}
	}

	render(doctype_layout, name) {
		finergy.container.change_to(doctype_layout);
		finergy.views.formview[doctype_layout].frm.refresh(name);
	}
}
