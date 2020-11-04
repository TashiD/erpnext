// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Supplementary Budget', {
	refresh: function(frm) {
		if(!frm.doc.posting_date) {
			cur_frm.set_value("posting_date", get_today())
		}
	}
});

cur_frm.fields_dict.cost_center.get_query = function(doc) {
	return{
		filters:{
			'is_group': 0,
			'is_disabled': 0,
		}
	}
}

cur_frm.fields_dict['items'].grid.get_field('account').get_query = function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
	return {
		filters: {
			'is_group': 0
		}
	}
}

frappe.ui.form.on("Supplementary Budget Item", "amount", function(frm, cdt, cdn) {

    calculate_value(frm, cdt, cdn);
});

function calculate_value(frm, cdt, cdn) {
        var sup_amount = 0;
        frm.doc.items.forEach(function(d) {
                if(d.amount) {

                        sup_amount += d.amount
                }

        })
        frm.set_value("total_amount", sup_amount);
        cur_frm.refresh_field("total_amount");

}
