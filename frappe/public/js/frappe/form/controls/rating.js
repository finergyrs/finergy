frappe.ui.form.ControlRating  = frappe.ui.form.ControlInt.extend({
	make_input() {
		this._super();
		const star_template = `
		<div class = "rating">
			<i class="fa fa-fw fa-star" data-idx=1></i>
			<i class="fa fa-fw fa-star" data-idx=2></i>
			<i class="fa fa-fw fa-star" data-idx=3></i>
			<i class="fa fa-fw fa-star" data-idx=4></i>
			<i class="fa fa-fw fa-star" data-idx=5></i>
		</div>
		`;
		
		this.$input_wrapper.html(star_template);

		this.$input_wrapper.find('i').hover((ev) => {
			const el = $(ev.currentTarget);
			let star_value = el.data('idx');
			el.parent().children('i.fa').each( function(e){
				if (e < star_value) {
					$(this).addClass('star-hover');
				} else {
					$(this).removeClass('star-hover');
				}
			});
		}, (ev) => {
				const el = $(ev.currentTarget);
				el.parent().children('i.fa').each( function(e) {
					$(this).removeClass('star-hover');
				});
		});

		this.$input_wrapper.find('i').click((ev) => {
			const el = $(ev.currentTarget);
			let star_value = el.data('idx');
			el.parent().children('i.fa').each( function(e) {
				if (e < star_value){
					$(this).addClass('star-click');
				} else {
					$(this).removeClass('star-click');
				}
			});
			this.set_value(star_value);
		});
	},
	get_value() {
		return this.value ? this.value : 0;
	},
	set_formatted_input(value) {
		let el = this.$input_wrapper.find('i');
		el.children('i.fa').prevObject.each( function(e) {
			if (e < value){
				$(this).addClass('star-click');
			}
		});
	}
});