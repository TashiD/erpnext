// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

cur_frm.add_fetch("branch", "cost_center", "cost_center");
frappe.ui.form.on("Project", {
	setup: function(frm) {
		frm.get_docfield("activity_tasks").allow_bulk_edit = 1;		
		frm.get_docfield("additional_tasks").allow_bulk_edit = 1;		
		
		frm.get_field('activity_tasks').grid.editable_fields = [
			{fieldname: 'task', columns: 3},
			{fieldname: 'is_group', columns: 1},
			{fieldname: 'start_date', columns: 2},
			{fieldname: 'end_date', columns: 2},
			{fieldname: 'work_quantity', columns: 1},
			{fieldname: 'work_quantity_complete', columns: 1}
		];
		
		frm.get_field('additional_tasks').grid.editable_fields = [
			{fieldname: 'task', columns: 3},
			{fieldname: 'is_group', columns: 1},
			{fieldname: 'start_date', columns: 2},
			{fieldname: 'end_date', columns: 2},
			{fieldname: 'work_quantity', columns: 1},
			{fieldname: 'work_quantity_complete', columns: 1}
		];
		
		frm.get_field('project_advance_item').grid.editable_fields = [
			{fieldname: 'advance_name', columns: 2},
			{fieldname: 'advance_date', columns: 2},
			{fieldname: 'received_amount', columns: 2},
			{fieldname: 'adjustment_amount', columns: 2},
			{fieldname: 'balance_amount', columns: 2}
		];		
		
		frm.get_field('project_boq_item').grid.editable_fields = [
			{fieldname: 'boq_name', columns: 2},
			{fieldname: 'boq_date', columns: 2},
			{fieldname: 'total_amount', columns: 2},
			{fieldname: 'received_amount', columns: 2},
			{fieldname: 'balance_amount', columns: 2}
		];				
		
		frm.get_field('project_invoice_item').grid.editable_fields = [
			{fieldname: 'invoice_name', columns: 2},
			{fieldname: 'invoice_date', columns: 2},
			{fieldname: 'net_invoice_amount', columns: 2},
			{fieldname: 'total_received_amount', columns: 2},
			{fieldname: 'total_balance_amount', columns: 2}
		];						
	},	
	
	onload: function(frm) {
		enable_disable(frm);
		var so = frappe.meta.get_docfield("Project", "sales_order");
		so.get_route_options_for_new_doc = function(field) {
			if(frm.is_new()) return;
			return {
				"customer": frm.doc.customer,
				"project_name": frm.doc.name
			}
		}

		frm.set_query('customer', 'erpnext.controllers.queries.customer_query');
		
		frm.set_query("user", "users", function() {
					return {
						query:"erpnext.projects.doctype.project.project.get_users_for_project"
					}
				});

		// sales order
		frm.set_query('sales_order', function() {
			var filters = {
				'project': ["in", frm.doc.__islocal ? [""] : [frm.doc.name, ""]]
			};

			if (frm.doc.customer) {
				filters["customer"] = frm.doc.customer;
			}

			return {
				filters: filters
			}
		});
	},
	refresh: function(frm) {
		enable_disable(frm);
		if(!frm.doc.__islocal){
			frm.add_custom_button(__("Advance"), function(){frm.trigger("make_project_advance")},__("Make"), "icon-file-alt");
			frm.add_custom_button(__("BOQ"), function(){frm.trigger("make_boq")},__("Make"), "icon-file-alt");
			frm.add_custom_button(__("Project Register"), function(){
					frappe.route_options = {
						project: frm.doc.name,
						additional_info: 1
					};
					frappe.set_route("query-report", "Project Register");
				},__("Reports"), "icon-file-alt"
			);
			frm.add_custom_button(__("Manpower"), function(){
					frappe.route_options = {
						project: frm.doc.name
					};
					frappe.set_route("query-report", "Project Manpower");
				},__("Reports"), "icon-file-alt"
			);
		}
		
		if(frm.doc.__islocal) {
			frm.web_link && frm.web_link.remove();
		} else {
			frm.add_web_link("/projects?project=" + encodeURIComponent(frm.doc.name));

			if(frappe.model.can_read("Task")) {
				frm.add_custom_button(__("Gantt Chart"), function() {
					frappe.route_options = {"project": frm.doc.name,
						"start": frm.doc.expected_start_date, "end": frm.doc.expected_end_date};
					frappe.set_route("Gantt", "Task");
				});
			}

			frm.trigger('show_dashboard');
		}
		
		if(frm.doc.docstatus === 0){
			enable_disable_items(frm);
		}
	},
	
	make_boq: function(frm){
		frappe.model.open_mapped_doc({
			method: "erpnext.projects.doctype.project.project.make_boq",
			frm: frm
		});
	},
	
	// ++++++++++++++++++++ Ver 1.0 BEGINS ++++++++++++++++++++
	// Following function created by SHIV on 02/09/2017
	make_project_advance: function(frm){
		frappe.model.open_mapped_doc({
			method: "erpnext.projects.doctype.project.project.make_project_advance",
			frm: frm
		});
	},
	// +++++++++++++++++++++ Ver 1.0 ENDS +++++++++++++++++++++
	
	tasks_refresh: function(frm) {
		var grid = frm.get_field('tasks').grid;
		grid.wrapper.find('select[data-fieldname="status"]').each(function() {
			if($(this).val()==='Open') {
				$(this).addClass('input-indicator-open');
			} else {
				$(this).removeClass('input-indicator-open');
			}
		});
	},
	show_dashboard: function(frm) {
		if(frm.doc.__onload.activity_summary.length) {
			var days = $.map(frm.doc.__onload.activity_summary, function(d) { return d.total_days });
			var max_count = Math.max.apply(null, days);
			var sum = days.reduce(function(a, b) { return a + b; }, 0);
			var section = frm.dashboard.add_section(
				frappe.render_template('test_dashboard',
					{
						sum: sum
					}
			));
			
			section.on('click', '.time-sheet-link', function() {
				var activity_type = $(this).attr('data-activity_type');
				frappe.set_route('List', 'Timesheet',
					{'activity_type': activity_type, 'project': frm.doc.name});
			});
		}
	},
	
	imprest_limit: function(frm){
		if (parseFloat(frm.doc.imprest_limit || 0.0) < parseFloat(frm.doc.imprest_received || 0.0)){
			msgprint(__("Imprest Limit cannot be less than already received amount."));
		}
		else {
			cur_frm.set_value("imprest_receivable",parseFloat(frm.doc.imprest_limit || 0.0)-parseFloat(frm.doc.imprest_received || 0.0))
		}
	},
		
	project_type: function(frm){
		enable_disable(frm);
		update_party_info(frm.doc);
	},
	party_type: function(frm){
		enable_disable(frm);
		update_party_info(frm.doc);
	},
	party: function(frm){
		update_party_info(frm.doc);
	},
	project_category: function(){
		cur_frm.set_value('project_sub_category','');
		cur_frm.fields_dict['project_sub_category'].get_query = function(doc, dt, dn) {
		   return {
				filters:{"project_category": doc.project_category}
		   }
		}
	}
});

var update_party_info=function(doc){
	cur_frm.call({
		method: "update_party_info",
		doc:doc
	});
}

var enable_disable = function(frm){
	// Display tasks only after the project is saved
	cur_frm.toggle_display("activity_and_tasks", !frm.doc.__islocal);
	cur_frm.toggle_display("activity_tasks", !frm.doc.__islocal);
	cur_frm.toggle_display("sb_additional_tasks", !frm.doc.__islocal);
	cur_frm.toggle_display("additional_tasks", !frm.doc.__islocal);
	
	//cur_frm.toggle_reqd("party_type", frm.doc.project_type=="External");
	//cur_frm.toggle_reqd("party", frm.doc.party_type || frm.doc.project_type=="External");
	cur_frm.toggle_reqd("party_type", 1);
	cur_frm.toggle_reqd("party", 1);
	
	if (frm.doc.project_type == "External") {
		frm.set_query("party_type", function() {
			return {
				//filters: {"name": ["in", ["Customer", "Supplier"]]}
				filters: {"name": ["in", ["Supplier"]]}
			}
		});
		//cur_frm.toggle_reqd("party", frm.doc.party_type);
	} else {
		frm.set_query("party_type", function() {
			return {
				//filters: {"name": ["in", ["Employee"]]}
				filters: {"name": ["in", ["Customer"]]}
			}
		});
	}
}

frappe.ui.form.on("Project Task", {
	edit_task: function(frm, doctype, name) {
		var doc = frappe.get_doc(doctype, name);
		if(doc.task_id) {
			frappe.set_route("Form", "Task", doc.task_id);
		} else {
			msgprint(__("Save the document first."));
		}
	},
	status: function(frm, doctype, name) {
		frm.trigger('tasks_refresh');
	},
});

frappe.ui.form.on("Project Advance Item",{
	view_advance: function(frm, doctype, name){
		var doc = frappe.get_doc(doctype, name);
		frappe.set_route("Form", "Project Advance", doc.advance_name);
	}
});

// ++++++++++++++++++++ Ver 1.0 BEGINS ++++++++++++++++++++
// Following block of code added by SHIV on 11/08/2017
frappe.ui.form.on("Activity Tasks", {
	activity_tasks_remove: function(frm, doctype, name){
		calculate_work_quantity(frm);
	},
	edit_task: function(frm, doctype, name) {
		var doc = frappe.get_doc(doctype, name);
		if(doc.task_id) {
			frappe.set_route("Form", "Task", doc.task_id);
		} else {
			msgprint(__("Save the document first."));
		}
	},
	view_timesheet: function(frm, doctype, name){
		var doc = frappe.get_doc(doctype, name);
		if(doc.task_id){
			frappe.route_options = {"project": frm.doc.name, "task": doc.task_id}
			frappe.set_route("List", "Timesheet");
		} else {
			msgprint(__("Save the document first."));
		}
	},
	status: function(frm, doctype, name) {
		frm.trigger('tasks_refresh');
	},
	work_quantity: function(frm, doctype, name){
		calculate_work_quantity(frm);
	},
});

frappe.ui.form.on("Additional Tasks", {
	activity_tasks_remove: function(frm, doctype, name){
		calculate_work_quantity(frm);
	},
	edit_task: function(frm, doctype, name) {
		var doc = frappe.get_doc(doctype, name);
		if(doc.task_id) {
			frappe.set_route("Form", "Task", doc.task_id);
		} else {
			msgprint(__("Save the document first."));
		}
	},
	view_timesheet: function(frm, doctype, name){
		var doc = frappe.get_doc(doctype, name);
		if(doc.task_id){
			frappe.route_options = {"project": frm.doc.name, "task": doc.task_id}
			frappe.set_route("List", "Timesheet");
		} else {
			msgprint(__("Save the document first."));
		}
	},
	status: function(frm, doctype, name) {
		frm.trigger('tasks_refresh');
	},
	work_quantity: function(frm, doctype, name){
		calculate_work_quantity(frm);
	},
});
// +++++++++++++++++++++ Ver 1.0 ENDS +++++++++++++++++++++

frappe.ui.form.on("Project", "refresh", function(frm) {
    cur_frm.set_query("cost_center", function() {
        return {
            "filters": {
		"is_group": 0,
		"is_disabled": 0
            }
        };
    });
})


// ++++++++++++++++++++ Ver 1.0 BEGINS ++++++++++++++++++++
// Following function created by SHIV on 2017/08/17
var calculate_work_quantity = function(frm){
	var at = frm.doc.activity_tasks || [];
	var adt= frm.doc.additional_tasks || [];
	total_work_quantity = 0.0;
	total_work_quantity_complete = 0.0;
	total_add_work_quantity = 0.0;
	total_add_work_quantity_complete = 0.0;

	for(var i=0; i<at.length; i++){
		//console.log(at[i].is_group);
		if (at[i].work_quantity && !at[i].is_group){
			total_work_quantity += at[i].work_quantity || 0;
			total_work_quantity_complete += at[i].work_quantity_complete || 0;
		}
	}
	
	for(var i=0; i<adt.length; i++){
		//console.log(at[i].is_group);
		if (adt[i].work_quantity && !adt[i].is_group){
			total_add_work_quantity += adt[i].work_quantity || 0;
			total_add_work_quantity_complete += adt[i].work_quantity_complete || 0;
		}
	}
	
	cur_frm.set_value("tot_wq_percent",total_work_quantity);
	cur_frm.set_value("tot_wq_percent_complete",total_work_quantity_complete);
	cur_frm.set_value("tot_add_wq_percent",total_add_work_quantity);
	cur_frm.set_value("tot_add_wq_percent_complete",total_add_work_quantity_complete);
}
// +++++++++++++++++++++ Ver 1.0 ENDS +++++++++++++++++++++

function enable_disable_items(frm){
	var toggle_fields = ["branch"];
	
	if(frm.doc.branch){
		if(in_list(user_roles, "CPBD")){
			toggle_fields.forEach(function(field_name){
				frm.set_df_property(field_name, "read_only", 0);
			});
		}
		else {
			toggle_fields.forEach(function(field_name){
				frm.set_df_property(field_name, "read_only", 1);
			});
		}
	}
}