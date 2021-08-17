# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from erpnext.accounts.doctype.business_activity.business_activity import get_default_ba
from erpnext.accounts.general_ledger import make_gl_entries
from erpnext.controllers.accounts_controller import AccountsController
from erpnext.custom_utils import check_budget_available
import json
from frappe import _
from frappe.utils import flt, cint, nowdate, getdate, formatdate


class PolAdvance(AccountsController):
	def validate(self):
		self.set_branch_cost_center()
		self.validate_cheque_info()
		if self.workflow_state == "Waiting For Payment"	:
			if "Accounts Manager" not in frappe.get_roles(frappe.session.user):
					self.approved_by = frappe.session.user

	def set_branch_cost_center(self):
		self.fuelbook_branch = frappe.db.get_value('Fuelbook',self.fuelbook,['branch'])
		self.cost_center = frappe.db.get_value('Branch',self.fuelbook_branch,['cost_center'])
		self.company = frappe.defaults.get_defaults().company
		self.branch = self.fuelbook_branch

	def on_submit(self):
		advance_account = frappe.db.get_single_value("Maintenance Accounts Settings", "pol_advance_account")
		check_budget_available(self.cost_center,advance_account,self.entry_date,self.amount,self.business_activity)
		self.make_gl_entries()
		self.consume_budget(advance_account)
  
	def on_cancel(self):
		self.make_gl_entries()
		self.cancel_budget_entry()

	def validate_cheque_info(self):
		if self.cheque_date and not self.cheque_no:
			msgprint(_("Cheque No is mandatory if you entered Cheque Date"), raise_exception=1)

	def consume_budget(self,advance_account):
		consume = frappe.get_doc({
			"doctype": "Consumed Budget",
			"account": advance_account,
			"cost_center": self.cost_center,
			"po_no": self.name,
			"po_date": self.entry_date,
			"amount": self.amount,
			"pii_name": self.name,
			# "com_ref": bud_obj.name,
			"business_activity": self.business_activity,
			"date": frappe.utils.nowdate()})
		consume.flags.ignore_permissions = 1
		consume.submit()
  
	def cancel_budget_entry(self):
		frappe.db.sql(
			"delete from `tabConsumed Budget` where po_no = %s", self.name) 
		
	def make_gl_entries(self):
		from erpnext.accounts.general_ledger import make_gl_entries
		if not self.amount:
			frappe.throw(_("Amount should be greater than zero"))
			
		gl_entries = []
		self.posting_date = self.entry_date
		ba = self.business_activity
		
		# payable_account = frappe.db.get_value("Company", self.company, "default_payable_account")
		credit_account = self.expense_account
		advance_account = frappe.db.get_single_value("Maintenance Accounts Settings", "pol_advance_account")
		
		if not credit_account:
			frappe.throw("Expense Account is mandatory")
		if not advance_account:
			frappe.throw("Setup POL Advance Account in Maintenance Accounts Settings")
			
		''' CBS Integration Begins'''
		partylist_json = {}
		if frappe.db.exists('Company', {'abbr': 'BOBL'}):
			partylist_json = {self.party_type: [{"party_type": self.party_type, "party": self.party, "amount": flt(self.amount)}]}
		''' CBS Integration Ends'''

		r = []
		if self.cheque_no:
			if self.cheque_date:
				r.append(_('Reference #{0} dated {1}').format(self.cheque_no, formatdate(self.cheque_date)))
			else:
				msgprint(_("Please enter Cheque Date date"), raise_exception=frappe.MandatoryError)
		if self.user_remark:
			r.append(_("Note: {0}").format(self.user_remark))

		if r:
			remarks = ("\n").join(r) #User Remarks is not mandatory
		gl_entries.append(
			self.get_gl_dict({
				"account":  credit_account,
				"against": self.supplier,
				"credit": self.amount,
				"credit_in_account_currency": self.amount,
				"against_voucher": self.name,
				"against_voucher_type": self.doctype,
				"cost_center": self.cost_center,
				"business_activity": ba,
				"remarks": remarks
			}, self.currency)
		)
		
		gl_entries.append(
			self.get_gl_dict({
				"account": advance_account,
				"party_type": self.party_type,
				"party": self.supplier,
				"against": self.supplier,
				"debit": self.amount,
				"debit_in_account_currency": self.amount,
				"business_activity": ba,
				"cost_center": self.cost_center,
			}, self.currency)
		)
		make_gl_entries(gl_entries, cancel=(self.docstatus == 2),update_outstanding="Yes", merge_entries=False)

