// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
//
frappe.require("assets/erpnext/js/financial_statements.js", function() {

frappe.query_reports["COP"] = {
        "filters": [
                {
                        "fieldname": "company",
                        "label": __("Company"),
                        "fieldtype": "Link",
                        "options": "Company",
                        "default": frappe.defaults.get_user_default("Company"),
                        "reqd": 1
                },
                {
                        "fieldname": "from_date",
                        "label": __("From Date"),
                        "fieldtype": "Date",
                        "default": frappe.defaults.get_user_default("year_start_date"),
                },
                {
                        "fieldname": "to_date",
                        "label": __("To Date"),
                        "fieldtype": "Date",
                        "default": frappe.defaults.get_user_default("year_end_date"),
                },
                {
                        "fieldname": "cost_center",
                        "label": __("Cost Center"),
                        "fieldtype": "Link",
                        "options": "Cost Center",
                        "get_query": function() {return {'filters': [['Cost Center', 'is_disabled', '!=', '1']]}},
                        "reqd": 1
                }
		/* {
                        "fieldname": "detail_cop",
                        "label": __("Show Detail COP"),
                        "fieldtype": "Check",
                        "default": 0
                },
                {
                        "fieldname": "with_period_closing_entry",
                        "label": __("Period Closing Entry"),
                        "fieldtype": "Check",
                        "default": 1
                },
                {
                        "fieldname": "show_zero_values",
                        "label": __("Show zero values"),
                        "fieldtype": "Check"
                },*/
        ],
        "formatter": erpnext.financial_statements.formatter,
        "tree": true,
        "name_field": "account",
        "parent_field": "parent_account",
        "initial_depth": 3,
	 onload: function(report) {
                report.page.add_inner_button(__("Detail COP"), function() {
                        var filters = report.get_values();
                        frappe.set_route('query-report', 'COP Computation Report', 
				{company: filters.company, from_date: filters.from_date, 
					to_date: filters.to_date, cost_center: filters.cost_center});
                }, 'Detail COP');
        }
   }
});
