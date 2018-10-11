# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt
from erpnext.custom_utils import get_branch_cc

class FundRequisition(Document):
	def validate(self):
		self.assign_cost_center()
		total = 0
		for a in self.items:
			total += flt(a.amount)

		self.total_amount = total

	def assign_cost_center(self):
                self.cost_center = get_branch_cc(self.branch)
                if not self.cost_center:
                        frappe.throw("Cost Center is Mandatory")

	def before_cancel(self):
		
		cl_status = frappe.db.get_value("Journal Entry", self.reference, "docstatus")
		if cl_status != 2:
			frappe.throw("You need to cancel the journal entry related to this fund requsition first!")
		
		self.db_set('reference', "")

	def on_submit(self):
		if(self.reference):
			frappe.throw("Cannot update.The same Jounal needs to be canceled first.")
		self.post_journal_entry()

	"""def on_submit(self):
		if(self.reference):
			frappe.throw("Cannot update.")
		self.post_journal_entry()
	"""

	def post_journal_entry(self):
		expense_bank_account = self.bank
	 	expense_bank_account1 =self.bank_account
		ic_account = frappe.db.get_single_value("Accounts Settings", "intra_company_account")

		je = frappe.new_doc("Journal Entry")
		je.flags.ignore_permissions = 1 
		je.title = "Fund Requisition (" + self.name + ")"
		je.voucher_type = 'Journal Entry'
		je.naming_series = 'Journal Entry'
		je.remark = 'Payment against : ' + self.name;
		je.posting_date = self.posting_date
		je.branch = self.branch

		if self.cost_center != self.issuing_cost_center:	
			je.append("accounts", {
				"account":expense_bank_account,
				
				"reference_name": self.name,
				"reference_type": "Fund Requisition",
				"cost_center": self.cost_center,
				"debit_in_account_currency": flt(self.total_amount),
				"debit": flt(self.total_amount),
					})
			je.append("accounts", {
				"account": expense_bank_account1,
				"reference_type": "Fund Requisition",
				"reference_name": self.name,
				"cost_center": self.issuing_cost_center,
				"credit_in_account_currency": flt(self.total_amount),
				"credit": flt(self.total_amount),
					})

			je.append("accounts", {
				"account": ic_account,
				"reference_name": self.name,
				"reference_type": "Fund Requisition",
				"cost_center": self.cost_center,
				"credit_in_account_currency": flt(self.total_amount),
				"credit": flt(self.total_amount),
					})

			je.append("accounts", {
				"account": ic_account,	
				"reference_name": self.name,
				"reference_type": "Fund Requisition",
				"cost_center": self.issuing_cost_center,
				"debit_in_account_currency": flt(self.total_amount),
				"debit": flt(self.total_amount),
					})

			je.save()
		else:
			je.append("accounts", {
                                "account":expense_bank_account,

                                "reference_name": self.name,
                                "reference_type": "Fund Requisition",
                                "cost_center": self.cost_center,
                                "debit_in_account_currency": flt(self.total_amount),
                                "debit": flt(self.total_amount),
                                        })
                        je.append("accounts", {
                                "account": expense_bank_account1,
                                "reference_type": "Fund Requisition",
                                "reference_name": self.name,
                                "cost_center": self.issuing_cost_center,
                                "credit_in_account_currency": flt(self.total_amount),
                                "credit": flt(self.total_amount),
                                        })
			je.save()
		self.db_set("reference", je.name)

