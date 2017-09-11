# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt

class VehicleLogbook(Document):
	def validate(self):
		self.check_duplicate()
		self.calculate_totals()

	def on_update(self):
		if self.rate_type == 'With Fuel':
			self.calculate_balance()

	def on_submit(self):
		self.update_hire()

	def check_duplicate(self):		
		for a in self.vlogs:
			for b in self.vlogs:
				if a.date == b.date and a.idx != b.idx:
					frappe.throw("Duplicate Dates in Vehicle Logs in row " + str(a.idx) + " and " + str(b.idx))

	def calculate_totals(self):
		if self.vlogs:
			total_w = total_i = 0
			for a in self.vlogs:
				total_w += flt(a.work_time)
				total_i += flt(a.idle_time)
			self.total_work_time = total_w
			self.total_idle_time = total_i

	def update_hire(self):
		if self.ehf_name:
			doc = frappe.get_doc("Equipment Hiring Form", self.ehf_name)
			doc.db_set("hiring_status", 1)

	def calculate_balance(self):
		self.db_set("closing_balance", flt(self.opening_balance) + flt(self.hsd_received) - flt(self.consumption))

@frappe.whitelist()
def get_opening(equipment, from_date, to_date):
	closing = frappe.db.sql("select closing_balance from `tabVehicle Logbook` where docstatus = 1 and equipment = %s and rate_type = 'With Fuel' and to_date <= %s order by to_date desc limit 1", (equipment, from_date), as_dict=True)

	qty = frappe.db.sql("select sum(qty) as qty from `tabConsumed POL` where equipment = %s and date between %s and %s and docstatus = 1", (equipment, from_date, to_date), as_dict=True)

	c_km = frappe.db.sql("select final_km from `tabVehicle Logbook` where docstatus = 1 and equipment = %s and to_date <= %s order by to_date desc limit 1", (equipment, from_date), as_dict=True)

	c_hr = frappe.db.sql("select final_hour from `tabVehicle Logbook` where docstatus = 1 and equipment = %s and to_date <= %s order by to_date desc limit 1", (equipment, from_date), as_dict=True)
	result = []
	if closing:
		result.append(closing[0].closing_balance)
	else:
		result.append(0)

	if qty:
		result.append(qty[0].qty)
	else:
		result.append(0)

	if c_km:
		result.append(c_km[0].final_km)
	else:
		result.append(0)

	if c_hr:
		result.append(c_hr[0].final_hour)
	else:
		result.append(0)

	return result
		
