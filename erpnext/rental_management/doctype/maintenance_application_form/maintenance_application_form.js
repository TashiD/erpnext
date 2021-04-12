// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch("tenant", "tenant_name", "tenant_name");
cur_frm.add_fetch("tenant", "dzongkhag", "dzongkhag");
cur_frm.add_fetch("tenant", "location", "location");
cur_frm.add_fetch("tenant", "structure_no", "structure_no");
cur_frm.add_fetch("tenant", "flat_no", "flat_no");
cur_frm.add_fetch("tenant", "block_no", "block_no");
cur_frm.add_fetch("tenant", "mobile_no", "mobile_no");
cur_frm.add_fetch("tenant", "branch", "branch");

frappe.ui.form.on('Maintenance Application Form', {
	onload: function (frm) {
		frm.set_query("tenant", function () {
			return {
				"filters": {
					"status": "Allocated",
					//                 "branch": frm.doc.branch,
				}
			};
		});
		frm.set_query("location", function () {
			return {
				"filters": {
					"dzongkhag": frm.doc.dzongkhag,
				}
			};
		});

		frappe.call({
			method: "erpnext.rental_management.doctype.tenant_information.tenant_information.get_distinct_structure_no",
			callback: function (r) {
				var structure_options = ["",];
				if (r.message) {
					r.message.forEach(function (rec) {
						structure_options.push(rec);
					});
					// console.log(structure_options);
					cur_frm.set_df_property("structure_no", "options", structure_options);
				}
			}
		});
	},


	refresh: function (frm) {
		if (!frm.doc.technical_sanction && frm.doc.docstatus == 1) {
			console.log("hell oworlsd")
			frm.add_custom_button("Create Technical Sanction", function () {
				frappe.model.open_mapped_doc({
					method: "erpnext.rental_management.doctype.maintenance_application_form.maintenance_application_form.make_technical_sanction",
					frm: cur_frm
				});
			});
		}
		//	cur_frm.page.set_inner_btn_group_as_primary(__("Make"));
	},

	// introduced by phuntsho on march 22 2021.
	// When there is no tenant in a building or a flat and maintenance needs to be done. 
	"no_current_tenant": function (frm) {
		if (frm.doc.no_current_tenant == 1) {
			frm.set_df_property("tenant", "hidden", 1)
			frm.set_df_property("structure_no", "read_only", 0)
			frm.set_df_property("location", "read_only", 0)
			frm.set_df_property("flat_no", "read_only", 0)
			frm.set_df_property("block_no", "read_only", 0)
			frm.set_df_property("dzongkhag", "read_only", 0)

		}
		else {
			frm.set_df_property("tenant", "hidden", 0)
			frm.set_df_property("structure_no", "read_only", 1)
			frm.set_df_property("location", "read_only", 1)
			frm.set_df_property("flat_no", "read_only", 1)
			frm.set_df_property("block_no", "read_only", 1)
			frm.set_df_property("dzongkhag", "read_only", 1)
		}
	},
});
