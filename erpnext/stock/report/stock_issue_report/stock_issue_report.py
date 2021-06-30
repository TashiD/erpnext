# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt, cint,add_days, cstr, flt, getdate, nowdate, rounded, date_diff
from erpnext.accounts.utils import get_child_cost_centers

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data


def get_columns(filters):
	cols = [
		("Date") + ":date:100",
		("Material Code") + ":data:110",
		("Material Name")+":data:120",
		("Material Group")+":data:120",
		("Material Sub Group")+":data:150",
		("From Warehouse")+":data:150",
		("UoM") + ":data:50",
		("Qty")+":Float:50",
		("Valuation Rate")+":data:120",
		("Amount")+":Currency:110",
		("Lot Number")+ ":data:100",
		("To Warehouse")+":data:170"
	]
	cols.append(("Stock Entry")+":Link/Stock Entry:170")
	return cols

def get_data(filters):
	data = "select se.posting_date, sed.item_code, sed.item_name, (select i.item_group from tabItem i where i.item_code = sed.item_code) as item_group, (select i.item_sub_group from tabItem i where i.item_code = sed.item_code) as item_sub_group, sed.s_warehouse, sed.uom, sed.qty, sed.valuation_rate,sed.amount, sed.lot_list, sed.t_warehouse, se.name FROM `tabStock Entry` se, `tabStock Entry Detail` sed WHERE se.name = sed.parent and  se.docstatus = 1"
	if filters.cost_center:
		if not filters.get("branch"):
			all_ccs = get_child_cost_centers(filters.cost_center)
			data += " and se.from_warehouse in (select parent from `tabWarehouse Branch` wb where wb.branch in (select name from `tabBranch` b where b.cost_center in {0}))".format(tuple(all_ccs))
		else:
			branch_name = frappe.db.get_value("Branch",{"cost_center": filters.get("branch")}, "name")
			data += " and se.from_warehouse in (select parent from `tabWarehouse Branch` wb where wb.branch in (select name from `tabBranch` b where b.name = '{0}'))".format(branch_name)
	if filters.get("purpose") == "Material Receipt":
		data += " and se.purpose = 'Material Receipt'"
	if filters.get("purpose") == "Material Transfer":
		data += " and se.purpose = 'Material Transfer'"
	if filters.get("warehouse"):
		data += " and sed.s_warehouse = \'" + str(filters.warehouse) + "\'"
	if filters.get("item_code"):
		data += " and sed.item_code = \'" + str(filters.item_code) + "\'"
	if filters.get("item_group"):
		data += " and sed.item_group = \'" + str(filters.item_group) + "\'"
	if filters.get("from_date") and filters.get("to_date"):
		data += " and se.posting_date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'"
	if filters.lot_number:
		data += " and sed.lot_list = \'" + str(filters.lot_number) + "\'"
	return frappe.db.sql(data)
