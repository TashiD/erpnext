frappe.pages['material-management'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Material Management',
		single_column: true
	});
	$(frappe.render_template('material_management')).appendTo(page.body);
}
