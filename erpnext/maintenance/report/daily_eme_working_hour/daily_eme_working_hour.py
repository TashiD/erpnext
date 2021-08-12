# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt, getdate, add_days, formatdate
from frappe import _

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    # frappe.msgprint(format(data))

    return columns, data

def get_columns(filters):
    columns = [{
        "fieldname": "registration_number",
        "label": _("Registration Number"),
        "fieldtype": "Data",
        "width": 200
    }]

    if filters.from_date and filters.to_date:
        if getdate(filters.from_date) > getdate(filters.to_date):
            frappe.throw("From Date should not be before To Date")

        for cur_date in get_dates(filters):
            columns.append({
                "fieldname": "date_" + str(formatdate(cur_date, 'yyyyMMdd')),
                "label": str(formatdate(cur_date, 'dd/MM/yyyy')),
                "fieldtype": "Float"
            })

        columns.append({
            "fieldname": "grand_total",
            "label": _("Grand Total"),
            "fieldtype": "Float",
            "width": 120
        })
    else:
        frappe.throw("From Date and To Date are mandatory")

    return columns

def get_data(filters):
    data = []
    conditions = get_conditions(filters)

    date_columns = []
    for cur_date in get_dates(filters):
        date_columns.append(
            "SUM((CASE WHEN posting_date = '{}' THEN IFNULL(lb.total_hours,0) ELSE NULL END)) AS date_{}".format(str(cur_date),str(formatdate(cur_date, 'yyyyMMdd')))
        )

    if date_columns:
        date_columns = ", ".join(date_columns)

    res = frappe.db.sql("""
        SELECT lb.equipment_type, e.equipment_number registration_number, 
            {date_columns}, SUM(IFNULL((select round(sum(lbi.hours),2) from `tabLogbook Item` lbi where lb.name=lbi.parent),0)) as grand_total
        FROM `tabLogbook` lb, `tabEquipment` e
        WHERE e.name = lb.equipment
        AND lb.posting_date BETWEEN '{from_date}' AND '{to_date}'
        AND lb.docstatus = 1 {cond}
        GROUP BY lb.equipment_type, e.equipment_number
        ORDER BY lb.equipment_type, e.equipment_number
    """.format(date_columns=date_columns, from_date=filters.get("from_date"), to_date=filters.get("to_date"), cond=conditions), as_dict=True)
    
    equip_type_wise_record = frappe._dict()
    for row in res:
        equip_type_wise_record.setdefault(row.equipment_type, []).append(row)

    for key, value in equip_type_wise_record.iteritems():
        total_row = frappe._dict()
        total_row.registration_number = ['<b>' + key + '</b>']

        for cur_date in get_dates(filters):
            total_row["date_" + str(formatdate(cur_date, 'yyyyMMdd'))] = sum([flt(row.get("date_" + str(formatdate(cur_date, 'yyyyMMdd')))) for row in value])
        total_row["grand_total"] = sum([flt(row.get("grand_total")) for row in value])

        data.append(total_row)
        data += value
    return data

def get_dates(filters):
    date_list = []
    current_date = getdate(filters.from_date)
    while True:
        date_list.append(current_date)
        current_date = add_days(current_date, 1)
        if current_date > getdate(filters.to_date):
            break
    return date_list

def get_conditions(filters):
    conditions = ""
    if filters.get("branch"):
        conditions += " AND  lb.branch = '{}'".format(filters.branch)
    if filters.get("supplier"):
        conditions += " AND e.supplier = '{}'".format(filters.supplier)
    if filters.get("equipment_type"):
        conditions += " AND lb.equipment_type = '{}'".format(filters.equipment_type)
    if filters.get("company_owned"):
        conditions += " AND e.not_cdcl = 0"
    return conditions