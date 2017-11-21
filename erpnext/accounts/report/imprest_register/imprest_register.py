# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
'''
--------------------------------------------------------------------------------------------------------------------------
Version          Author          CreatedOn          ModifiedOn          Remarks
------------ --------------- ------------------ -------------------  -----------------------------------------------------
2.0		  SSK		 20/11/2017                           Original
--------------------------------------------------------------------------------------------------------------------------                                                                          
'''

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt

def execute(filters=None):
	columns = get_columns()
	data    = get_data(filters)

	return columns, data

def get_data(filters):
        cond = get_conditions(filters)
        frappe.msgprint(str(frappe.get_roles(frappe.session.user)))

        
        #frappe.msgprint(_("{0}").format(frappe.permissions.get_user_permissions(frappe.session.user)))

        #for i in frape.get_roles(frappe.session.user):
        #        frappe.msgprint(str(frappe.permissions.get_all_perms(i)))
        #frappe.msgprint(str(frappe.permissions.get_user_permissions(frappe.session.user)))


        result = frappe.db.sql("""
                select
                        name            as tran_no,
                        remarks,
                        entry_date      as tran_date,
                        entry_type      as tran_type,
                        receipt_amount  as receipt_amt,
                        purchase_amount as purchase_amt,
                        reference_no    as ref_no,
                        imprest_type    as imprest_type,
                        cost_center,
                        project
                from `tabCash Journal Entry`
                order by cost_center, ifnull(reference_no, name), entry_date
        """, as_dict=1)
        
        return result

def get_conditions(filters):
        cond = ''
        
        if filters.get('imprest_type'):
                cond += ' and imprest_type = "{0}"'.format(filters.get('imprest_type'))

        if filters.get('from_date') and filters.get('to_date'):
                cond += ' and entry_date between "{0}" and "{1}"'.format(filters.from_date, filters.to_date)
        
def get_columns():
        return [
                {
                        "fieldname": "tran_no",
                        "label": _("Transaction#"),
                        "fieldtype": "Link",
                        "options": "Cash Journal Entry",
                        "width": 100,
                },
                {
                        "fieldname": "remarks",
                        "label": _("Title"),
                        "fieldtype": "Data",
                        "width": 260,
                },
                {
                        "fieldname": "tran_date",
                        "label": "Date",
                        "fieldtype": "Date",
                        "width": 80
                },
                {
                        "fieldname": "tran_type",
                        "label": _("Type"),
                        "fieldtype": "Data",
                        "width": 80,
                },
                {
                        "fieldname": "receipt_amt",
                        "label": _("Receipt Amount"),
                        "fieldtype": "Currency",
                        "width": 100,
                },
                {
                        "fieldname": "purchase_amt",
                        "label": _("Purchase Amount"),
                        "fieldtype": "Currency",
                        "width": 100,
                },
                {
                        "fieldname": "ref_no",
                        "label": _("Receipt Ref#"),
                        "fieldtype": "Link",
                        "options": "Cash Journal Entry",
                        "width": 100,
                },
                {
                        "fieldname": "imprest_type",
                        "label": _("Imprest Type"),
                        "fieldtype": "Link",
                        "options": "Cost Center",
                        "width": 80,
                },
                {
                        "fieldname": "cost_center",
                        "label": _("Cost Center"),
                        "fieldtype": "Data",
                        "width": 180
                },
                {
                        "fieldname": "project",
                        "label": _("Project"),
                        "fieldtype": "Link",
                        "options": "Project",
                        "width": 80
                },
        ]        
