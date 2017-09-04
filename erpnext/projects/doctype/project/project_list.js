frappe.listview_settings['Project'] = {
	add_fields: ["status", "priority", "is_active", "tot_wq_percent_complete", "expected_end_date"],
	filters:[["status","=", "Open"]],
	get_indicator: function(doc) {
		if(doc.status=="Open" && doc.tot_wq_percent_complete) {
			return [__("{0}% Complete", [parseFloat(doc.tot_wq_percent_complete)]), "orange", "tot_wq_percent_complete,>,0|status,=,Open"];
		} else {
			return [__(doc.status), frappe.utils.guess_colour(doc.status), "status,=," + doc.status];
		}
	}
};
