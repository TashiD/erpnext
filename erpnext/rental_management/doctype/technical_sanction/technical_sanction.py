# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import cstr, flt, fmt_money, formatdate, nowdate

class TechnicalSanction(Document):
	def validate(self):
		self.update_maf()
		if self.outsource:
			if not self.supplier:
				frappe.throw("A Contractor must be selected as the work type is outsource")
		total_amount = 0.0
		for i in self.items:
			total_amount += i.total
		self.total_amount = total_amount

	# def on_update_after_submit(self):
	# 	if self.party:
	# 		frappe.throw("Cannot update once set!")
	# 	if self.party_type:
	# 		frappe.throw("Cannot update once set!")

	def on_submit(self):
		pass

	def on_update_after_submit(self):
		rts = frappe.db.sql("""SELECT name FROM `tabRevised Technical Sanction` WHERE technical_sanction = '{}' AND docstatus = 1""".format(self.name),as_dict=1)
		if rts: 
			query = """ UPDATE `tabRevised Technical Sanction` set party_type = '{}', party='{}' WHERE name='{}'""".format(self.party_type, self.party, rts[0].name)
			frappe.db.sql(query)
			frappe.msgprint("Updated the party and party type in Revised Technical Sanction")
			
	def update_maf(self):
		if self.docstatus == 2:
			frappe.db.sql("update `tabMaintenance Application Form` set technical_sanction = NULL where name ='{1}'".format(self.name, self.maf))
		else:
			if self.maf and self.name:
				frappe.db.sql("update `tabMaintenance Application Form` set technical_sanction = '{0}' where name ='{1}'".format(self.name, self.maf))
			else:
				frappe.throw("Not able to update MAF")


	def get_technical_sanction_items(self):
		items = frappe.db.sql("select se.name as stock_entry, sed.name as stock_entry_detail, sed.item_code as item, sed.item_name as item_name, sed.stock_uom as uom, sed.qty as quantity, sed.amount from `tabStock Entry Detail` sed, `tabStock Entry` se where se.docstatus = 1 and sed.parent = se.name and se.purpose = 'Material Issue' and se.technical_sanction = \'"+ str(self.name) +"\'", as_dict=True)
		material_amount = 0.00
		if items:
			if self.material_items:
				for d in items:
					material_amount += d.amount
					for a in self.material_items:
						check = 0
						if a.stock_entry != d.stock_entry and d.stock_entry_detail != a.stock_entry_detail:
							check = 1
					if check:
						row = self.append('material_items', {})
						row.update(d)	
			else:
				for d in items:
					material_amount += d.amount
					row = self.append('material_items', {})
					row.update(d)	
			self.material_charges = material_amount
		else:
			frappe.msgprint("No stock entries related to the Technical Sanction found. Entries might not have been submitted?")

# @frappe.whitelist()
# def make_payment(source_name, target_doc=None):
# 	def update_docs(obj, target, source_parent):
# 		target.posting_date = nowdate()
# 		target.payment_for = "Maintenance Payment"
# 		payable_amount = flt(obj.total_amount) - flt(obj.material_charges)
# 		target.total_amount = payable_amount
# 		target.net_amount = payable_amount
# 		target.actual_amount = payable_amount

# 		target.append("maintenance_payment_item", {
# 			"technical_sanction": obj.name,
# 			"service_charges": obj.total_amount,
# 			"material_charges": obj.material_charges,
# 			"payable_amount": payable_amount
# 		})

#         doc = get_mapped_doc("Technical Sanction", source_name, {
#                         "Technical Sanction": {
#                                 "doctype": "Mechanical Payment",
# 				"field_map":{
# 				},	
#                                 "postprocess": update_docs,
#                                 "validation": {"docstatus": ["=", 1]}
#                         },
#                 }, target_doc)
#         return doc

@frappe.whitelist()
def prepare_rts(source_name, target_doc=None):
	def update_docs(obj, target, source_parent):
		target.technical_sanction = obj.name
        doc = get_mapped_doc("Technical Sanction", source_name, {
                        "Technical Sanction": {
                                "doctype": "Revised Technical Sanction","field_map":{},	
                                "postprocess": update_docs,
                                "validation": {"docstatus": ["=", 1]}
                        },
                }, target_doc)
        return doc

@frappe.whitelist()
def prepare_bill(source_name, target_doc=None):
	def update_docs(obj, target, source_parent):
		target.technical_sanction = obj.name
        doc = get_mapped_doc("Technical Sanction", source_name, {
                        "Technical Sanction": {
                                "doctype": "Technical Sanction Bill",
								"field_map":{
									"total_amount" : "total_gross_amount"
								},	
                                "postprocess": update_docs,
                                "validation": {"docstatus": ["=", 1]}
                        },
                }, target_doc)
        return doc


# added by phuntsho on july 12th, 2021
@frappe.whitelist()
def make_advance(source_name, target_doc=None):
	def update_master(source_doc, target_doc, source_partent):
		#target_doc.customer = source_doc.customer
		pass
	
	doclist = get_mapped_doc("Technical Sanction", source_name, {
		"Technical Sanction": {
				"doctype": "Technical Sanction Advance",
				"field_map":{
					"name": "technical_sanction",
					"party_type": "party_type",
					"party": "party",
					"party_address": "party_address"
				},
				"postprocess": update_master
			}
	}, target_doc)
	return doclist
