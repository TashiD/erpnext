# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate

def execute(filters=None):
	if not filters: filters = {}
	
	#validate_filters(filters)

	columns = get_columns()
	item_map = get_item_details(filters)
	iwb_map = get_item_warehouse_map(filters)

	data = []
	for (company, item, warehouse) in sorted(iwb_map):
		qty_dict = iwb_map[(company, item, warehouse)]
		data.append([item, item_map[item]["item_name"],
			item_map[item]["item_group"],
			item_map[item]["item_sub_group"],
			warehouse,
			item_map[item]["stock_uom"], qty_dict.opening_qty,
			qty_dict.opening_val, qty_dict.in_qty,
			qty_dict.in_val, qty_dict.out_qty,
			qty_dict.out_val, qty_dict.bal_qty,
			qty_dict.bal_val, qty_dict.val_rate,
			company
		])

	return columns, data

def get_columns():
	"""return columns"""

	columns = [
		_("Material Code")+":Link/Item:100",
		_("Material Name")+"::150",
		_("Material Group")+"::100",
		_("Material Sub Group")+"::150",
		_("Warehouse")+":Link/Warehouse:100",
		_("Stock UOM")+":Link/UOM:90",
		_("Opening Qty")+":Float:100",
		_("Opening Value")+":Float:110",
		_("Receipt Qty")+":Float:80",
		_("Receipt Value")+":Float:80",
		_("Issue Qty")+":Float:80",
		_("Issue Value")+":Float:80",
		_("Balance Qty")+":Float:100",
		_("Balance Value")+":Float:100",
		_("MAP")+":Float:90",
		_("Company")+":Link/Company:100"
	]

	return columns

def get_conditions(filters):
	conditions = ""
	if not filters.get("from_date"):
		frappe.throw(_("'From Date' is required"))

	if filters.get("from_date") > filters.get("to_date"):
		frappe.throw(_("To Date cannot be before From Date"))
	
	if filters.get("to_date"):
		conditions += " and posting_date <= '%s'" % frappe.db.escape(filters["to_date"])
	else:
		frappe.throw(_("'To Date' is required"))

	if filters.get("item_code"):
		conditions += " and item_code = '%s'" % frappe.db.escape(filters.get("item_code"), percent=False)

	if filters.get("item_group"):
		conditions += " and item_group = '%s'" % frappe.db.escape(filters.get("item_group"), percent=False)

	if filters.get("item_sub_group"):
		conditions += " and item_sub_group = '%s'" % frappe.db.escape(filters.get("item_sub_group"), percent = False)

	if filters.get("warehouse"):
		conditions += " and warehouse = '%s'" % frappe.db.escape(filters.get("warehouse"), percent=False)

	return conditions

def get_stock_ledger_entries(filters):
	conditions = get_conditions(filters)
	return frappe.db.sql("""select item_code, warehouse, posting_date, actual_qty, valuation_rate, item_group, item_sub_group,
			company, voucher_type, qty_after_transaction, stock_value_difference
		from `tabStock Ledger Entry` force index (posting_sort_index)
		where docstatus < 2 %s order by posting_date, posting_time, name""" %
		conditions, as_dict=1)

def get_item_warehouse_map(filters):
	iwb_map = {}
	from_date = getdate(filters["from_date"])
	to_date = getdate(filters["to_date"])

	sle = get_stock_ledger_entries(filters)

	for d in sle:
		key = (d.company, d.item_code, d.warehouse)
		if key not in iwb_map:
			iwb_map[key] = frappe._dict({
				"opening_qty": 0.0, "opening_val": 0.0,
				"in_qty": 0.0, "in_val": 0.0,
				"out_qty": 0.0, "out_val": 0.0,
				"bal_qty": 0.0, "bal_val": 0.0,
				"val_rate": 0.0, "uom": None
			})

		qty_dict = iwb_map[(d.company, d.item_code, d.warehouse)]

		if d.voucher_type == "Stock Reconciliation":
			qty_diff = flt(d.qty_after_transaction) - qty_dict.bal_qty
		else:
			qty_diff = flt(d.actual_qty)

		value_diff = flt(d.stock_value_difference)

		if d.posting_date < from_date:
			# Following if condition added by SHIV on 2020/09/30
			# if d.voucher_type == "Stock Reconciliation" and not flt(d.qty_after_transaction):
			# 	qty_dict.opening_qty = 0
			# 	qty_dict.opening_val = 0
			# 	qty_diff = 0
			# 	value_diff = 0
			# 	qty_dict.bal_qty = 0
			# 	qty_dict.bal_val = 0
			qty_dict.opening_qty += qty_diff
			qty_dict.opening_val += value_diff

		elif d.posting_date >= from_date and d.posting_date <= to_date:
			if qty_diff > 0:
				# Following if condition added by SHIV on 2020/09/30
				# if d.voucher_type == "Stock Reconciliation" and not flt(d.qty_after_transaction):
				# 	qty_diff = 0
				# 	value_diff = 0
				# 	qty_dict.in_qty = 0
				# 	qty_dict.in_val = 0
				# 	qty_dict.bal_qty = 0
				# 	qty_dict.bal_val = 0
				qty_dict.in_qty += qty_diff
				qty_dict.in_val += value_diff
			else:
				# Following if condition added by SHIV on 2020/09/30
				# if d.voucher_type == "Stock Reconciliation" and not flt(d.qty_after_transaction):
				# 	qty_diff = 0
				# 	value_diff = 0
				# 	qty_dict.out_qty = 0
				# 	qty_dict.out_val = 0
				# 	qty_dict.bal_qty = 0
				# 	qty_dict.bal_val = 0
				qty_dict.out_qty += abs(qty_diff)
				qty_dict.out_val += abs(value_diff)

		qty_dict.val_rate = d.valuation_rate
		qty_dict.bal_qty += qty_diff
		qty_dict.bal_val += value_diff

	return iwb_map

def get_item_details(filters):
	condition = ''
	#value = ()
	if filters.get("item_code"):
		condition += " and item_code= '{0}'".format(filters.get('item_code'))
	if filters.get("item_group"):
		condition += " and item_group = '{0}'".format(filters.get('item_group'))

	if filters.get('item_sub_group'):
		condition += " and item_sub_group = '{0}'".format(filters.get('item_sub_group'))

	#value = (filters["item_code"],)

	'''items = frappe.db.sql("""select name, item_name, stock_uom, item_group, item_sub_group, brand, description
		from tabItem where 1 = 1 {condition}""".format(condition=condition), value, as_dict=1)
	'''
	items = frappe.db.sql("""select name, item_name, stock_uom, item_group, item_sub_group, brand, description
                from tabItem where 1 = 1 {condition}""".format(condition=condition), as_dict=1)

	return dict((d.name, d) for d in items)

def validate_filters(filters):
	if not (filters.get("item_code") or filters.get("warehouse")):
		sle_count = flt(frappe.db.sql("""select count(name) from `tabStock Ledger Entry`""")[0][0])
		if sle_count > 500000:
			frappe.throw(_("Please set filter based on Item or Warehouse"))
	
