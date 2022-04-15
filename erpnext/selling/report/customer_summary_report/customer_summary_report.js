// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Customer Summary Report"] = {
	"filters": [
		{
                        "fieldname":"company",
                        "label": __("Company"),
                        "fieldtype": "Link",
                        "options": "Company",
                        "default": frappe.defaults.get_user_default("Company"),
                        "reqd": 1
                },
                /*{
                        "fieldname":"fiscal_year",
                        "label": __("Fiscal Year"),
                        "fieldtype": "Link",
                        "options": "Fiscal Year",
                        "default": frappe.defaults.get_user_default("fiscal_year"),
                        "reqd": 1
                },
                {
                        "fieldname": "periodicity",
                        "label": __("Periodicity"),
                        "fieldtype": "Select",
                        "options": [
                                { "value": "Monthly", "label": __("Monthly") },
                                { "value": "Quarterly", "label": __("Quarterly") },
                                { "value": "Half-Yearly", "label": __("Half-Yearly") },
                                { "value": "Yearly", "label": __("Yearly") }
                        ],
                        "default": "Monthly",
                        "reqd": 1
                },*/
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
                        "default": get_today(),
                },
		{
			"fieldname": "item_code",
			"label": __("Material Code"),
			"fieldtype": "Link",
			"options": "Item",
			"get_query": function() {return {'filters': [['Item', 'disabled', '!=', '1']]}}
		},
		{
                        "fieldname": "item_type",
                        "label": __("Item Type"),
                        "fieldtype": "Link",
                        "options": "Item Type"
                },
		{
			"fieldname": "market",
			"label": __("Market"),
			"fieldtype": "Link",
			"options": "Market"
		},
		{
			"fieldname": "cost_center",
			"label": __("Cost Center"),
			"fieldtype": "Link",
			"options": "Cost Center",
			"get_query": function() {return {'filters': [['Cost Center', 'is_disabled', '!=', '1']]}}
		}

	]
};
