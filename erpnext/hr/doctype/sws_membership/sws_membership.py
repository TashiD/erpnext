# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate

class SWSMembership(Document):
	def validate(self):
		for a in self.get("members"):
			if a.employee == "" or a.employee == None:
				a.employee = self.employee
		self.validate_duplicate_members()
		self.update_contribution()
		
	def update_contribution(self):
		settings 	 = frappe.get_single("SWS Settings")
		immediate 	 = [i.relation for i in settings.immediate]
		nonimmediate = [i.relation for i in settings.nonimmediate]
		for row in self.get("members"):
			if row.relationship not in immediate+nonimmediate:
				frappe.throw(_("Relationship <b>{}</b> is not part of any plan under <b>SWS Settings</b>").format(row.relationship))

			if row.relationship in immediate:
				# if not flt(settings.cont_immediate):
				# 	frappe.throw(_("Contribution/month for Immediate Family Members not defined under <b>SWS Settings</b>"))
				row.contribution = flt(settings.cont_immediate)
			elif row.relationship in nonimmediate:
				# if not flt(settings.cont_nonimmediate):
				# 	frappe.throw(_("Contribution/month for Non-Immediate Family Members not defined under <b>SWS Settings</b>"))
				row.contribution = flt(settings.cont_nonimmediate)
	def on_submit(self):
		self.update_employee_master_family()
		self.update_salary_structure()

	def validate_duplicate_members(self):
		members = []
		for a in self.members:
			members.append(a.full_name+"-"+a.relationship+"-"+self.employee)
			exists = frappe.db.sql("""
				select b.name as name from `tabSWS Membership Item` a, `tabSWS Membership` b where a.parent = b.name and b.docstatus < 2 and a.parent != '{0}' and relationship = '{1}' and full_name = '{2}' and b.employee = '{3}'
                          """.format(self.name, a.relationship, a.full_name, self.employee), as_dict = True)
			if exists:
				for b in exists:
					if b.name != None:
						frappe.throw("Duplicate member in another SWS Membership Document {0}"+format(b.name))
		members_unique = set(members)
		if len(members) != len(members_unique):
			frappe.throw("Duplicate members with same name and same relationship")
      
	def update_employee_master_family(self):
		employee_doc = frappe.get_doc("Employee",self.employee)
		for a in self.members:
			exists = frappe.db.sql("""
				select name from `tabEmployee Family Details` where (parent = '{0}'
				and name = '{1}') or (parent = '{0}' and relationship = '{2}' and lower(full_name) = '{3}')
                          """.format(self.employee, a.name, a.relationship, (a.full_name).lower()), as_dict=True)
			if exists:
				for d in exists:
					frappe.db.sql("""
						delete from `tabEmployee Family Details` where name = '{}'
                  	""".format(d.name))

			if a.relationship != 'Self':
				row = employee_doc.append("employee_family_details")
				row.name = a.name
				row.relationship = a.relationship
				row.full_name = a.full_name
				row.gender = a.gender
				row.date_of_birth = a.date_of_birth
				row.cid_no = a.cid_no
				row.district_name = a.district_name
				row.city_name = a.city_name
				row.village_name = a.village_name
				row.cid_attach = a.cid_attach
				row.deceased = a.deceased
		employee_doc.save(ignore_permissions=True)

	def update_salary_structure(self):
		# sws_amount = 0
		# for a in self.members:
		# 	if a.status != 'Claimed':
		# 		sws_amount += a.contribution
		# if sws_amount != 0:
		ss = frappe.db.sql("""
                    select name from `tabSalary Structure` where is_active = 'Yes' and employee = '{}'
                """.format(self.employee),as_dict=True)
		doc = frappe.get_doc("Salary Structure", ss[0].name)

		doc.save(ignore_permissions=True)

    
@frappe.whitelist()
def get_sws_contribution(employee, ason_date=getdate()):
	immediate_cont 	  = 0
	nonimmediate_cont = 0

	if frappe.db.get_single_value("HR Settings", "sws_type") != "Based on Grade":
		settings = frappe.get_single("SWS Settings")
		li = frappe.db.sql("""SELECT r.relationship_type, SUM(IFNULL(mi.contribution,0)) tot_contribution
							FROM `tabSWS Membership` m, `tabSWS Membership Item` mi, `tabRelationship` r
							WHERE m.employee = "{}"
							AND m.docstatus = 1
							AND m.registration_date <= "{}"
							AND mi.parent = m.name
							AND mi.status = 'Active'
							AND r.name = mi.relationship
						GROUP BY r.relationship_type""".format(employee, ason_date), as_dict=True)
        
		for i in li:
			if i.relationship_type == "Immediate":
				if settings.cont_type_immediate == "Per Head":
					immediate_cont += flt(i.tot_contribution)
				else:
					immediate_cont = flt(settings.cont_immediate)
			else:
				if settings.cont_type_nonimmediate == "Per Head":
					nonimmediate_cont += flt(i.tot_contribution)
				else:
					nonimmediate_cont = flt(settings.cont_nonimmediate)

	return immediate_cont+nonimmediate_cont