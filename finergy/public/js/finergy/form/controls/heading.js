finergy.ui.form.ControlHeading = finergy.ui.form.ControlHTML.extend({
	get_content: function() {
		return "<h4>" + __(this.df.label) + "</h4>";
	}
});