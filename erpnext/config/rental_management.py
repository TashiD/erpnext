from frappe import _

def get_data():
	return [
		{
			"label": _("Master Data"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Town Category",
				},
				{
					"type": "doctype",
					"name": "Locations",
				},
				{
					"type": "doctype",
					"name": "Building Classification",
				},
				{
					"type": "doctype",
					"name": "Building Category",
				},
				{
					"type": "doctype",
					"name": "Block No",
				},
				{
					"type": "doctype",
					"name": "Flat No",
				},
				{
					"type": "doctype",
					"name": "Floor Area",
				},
				{
					"type": "doctype",
					"name": "Ministry and Agency",
				},
				{
					"type": "doctype",
					"name": "Tenant Department",
				},
				
			]
		},
		{
			"label": _("Settings"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Rental Setting",
				},
				{
					"type": "doctype",
					"name": "Rate",
				},
			]
		},
		{
			"label": _("Tenant Transactions"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Tenant Information",
				},
				{
					"type": "doctype",
					"name": "Process Rental Billing",
				},
				{
					"type": "doctype",
					"name": "Rental Bill",
				},
				{
					"type": "doctype",
					"name": "Rental Payment",
				},
				
			]
		},
		{
                        "label": _("Reports"),
                        "icon": "icon-list",
                        "items": [
				 {
                                        "type": "report",
                                        "is_query_report": True,
                                        "name": "Rental Register",
                                        "doctype": "Rental Information",
                                        "Label": _("Rental Register")
                                },
				{
                                        "type": "report",
                                        "is_query_report": True,
                                        "name": "Tenant Information",
                                        "doctype": "Tenant Information",
                                        "Label": _("Tenant Information")
                                }


			]
		},
		   {
                        "label": _("Tools"),
                        "icon": "icon-list",
                        "items": [
                                 {
                                        "type": "doctype",
                                        "name": "Tenant Updation Tool",
                                },

                                 {
                                        "type": "doctype",
                                        "name": "Rental Bill Cancelation Tool",
					"label": "Bill Cancellation Tool"
                                }

                        ]
                },
	]
