# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt, getdate, nowdate
from frappe import msgprint, _
from frappe.model.document import Document

form_grid_templates = {
	"journal_entries": "templates/form_grid/bank_reconciliation_grid.html"
}

class BankReconciliation(Document):
	def get_payment_entries(self):
		if not (self.bank_account and self.from_date and self.to_date):
			msgprint("Bank Account, From Date and To Date are Mandatory")
			return

		condition = ""
		if not self.include_reconciled_entries:
			condition = "and (clearance_date is null or clearance_date='0000-00-00')"


		journal_entries = frappe.db.sql("""
			select 
				"Journal Entry" as payment_document, t1.name as payment_entry, 
				t1.cheque_no as cheque_number, t1.cheque_date, 
				abs(t2.debit_in_account_currency - t2.credit_in_account_currency) as amount, 
				t1.posting_date, t2.against_account, t1.clearance_date
			from
				`tabJournal Entry` t1, `tabJournal Entry Account` t2
			where
				t2.parent = t1.name and t2.account = %s and t1.docstatus=1
				and t1.posting_date >= %s and t1.posting_date <= %s 
				and ifnull(t1.is_opening, 'No') = 'No' {0}
			order by t1.posting_date ASC, t1.name DESC
		""".format(condition), (self.bank_account, self.from_date, self.to_date), as_dict=1)

		direct_payment_entries = frappe.db.sql("""
                        select
                                "Direct Payment" as payment_document, name as payment_entry,
                                cheque_no as cheque_number, cheque_date,
                                net_amount as amount,
                                posting_date, branch as against_account, clearance_date
                        from `tabDirect Payment`
                        where '{0}' IN (credit_account, debit_account)
                        	and docstatus = 1
                        	and posting_date between '{1}' and '{2}'
                        {3}
                """.format(self.bank_account, self.from_date, self.to_date, condition), as_dict=1)
		frappe.msgprint(len(direct_payment_entries))	
		
		payment_entries = frappe.db.sql("""
			select 
				"Payment Entry" as payment_document, name as payment_entry, 
				reference_no as cheque_number, reference_date as cheque_date, 
				if(paid_from=%s, paid_amount, received_amount) as amount, 
				posting_date, party as against_account, clearance_date
			from `tabPayment Entry`
			where
				(paid_from=%s or paid_to=%s) and docstatus=1
				and posting_date >= %s and posting_date <= %s {0}
			order by 
				posting_date ASC, name DESC
		""".format(condition), 
		(self.bank_account, self.bank_account, self.bank_account, self.from_date, self.to_date), as_dict=1)

                ##### Ver 1.0.190304 Begins, following added by SHIV on 2019/03/04
                hsd_entries = frappe.db.sql("""
                        select
                                "HSD Payment" as payment_document, name as payment_entry,
                                cheque__no as cheque_number, cheque_date,
                                amount,
                                posting_date, supplier as against_account, clearance_date
                        from `tabHSD Payment`
                        where bank_account = '{0}'
                        and docstatus = 1
                        and posting_date >= '{1}' and posting_date <= '{2}'
                        {3}
                """.format(self.bank_account, self.from_date, self.to_date, condition), as_dict=1)

                transporter_payment_entries = frappe.db.sql("""
                        select
                                "Transporter Payment" as payment_document, name as payment_entry,
                                cheque_no as cheque_number, cheque_date,
                                amount_payable as amount,
                                posting_date, registration_no as against_account, clearance_date
                        from `tabTransporter Payment`
                        where credit_account = '{0}'
                        and docstatus = 1
                        and posting_date >= '{1}' and posting_date <= '{2}'
                        {3}
                """.format(self.bank_account, self.from_date, self.to_date, condition), as_dict=1)
                ##### Ver 1.0.190304 Ends
	


		tds_remittance_entries = frappe.db.sql("""
                        select 
                                "TDS Remittance" as payment_document, name as payment_entry,
                                cheque_no as cheque_number, cheque_date,
                                total_tds as amount, posting_date, branch as against_account, clearance_date
                        from `tabTDS Remittance`
                        where account = '{0}'
                        and docstatus = 1
                        and posting_date between '{1}' and '{2}'
                        {3}
                """.format(self.bank_account, self.from_date, self.to_date, condition), as_dict =1)
	
		entries = sorted(list(payment_entries)+list(journal_entries)+list(direct_payment_entries)+list(hsd_entries)+list(transporter_payment_entries)+list(tds_remittance_entries), 
			key=lambda k: k['posting_date'] or getdate(nowdate()))
				
		self.set('payment_entries', [])
		self.total_amount = 0.0

		for d in entries:
			clearing_date = frappe.db.get_value("BRS Entries", {"cheque_no": d.cheque_number, "amount": d.amount, "docstatus": 1}, "clearing_date")
			if clearing_date:
				d.clearance_date = clearing_date

			row = self.append('payment_entries', {})
			row.update(d)
			self.total_amount += flt(d.amount)

	def update_clearance_date(self):
		clearance_date_updated = False
		for d in self.get('payment_entries'):
			if d.clearance_date:
				if d.cheque_date and getdate(d.clearance_date) < getdate(d.cheque_date):
					frappe.throw(_("Row #{0}: Clearance date {1} cannot be before Cheque Date {2}")
						.format(d.idx, d.clearance_date, d.cheque_date))

			if d.clearance_date or self.include_reconciled_entries:
				if not d.clearance_date:
					d.clearance_date = None

				frappe.db.set_value(d.payment_document, d.payment_entry, "clearance_date", d.clearance_date)
				frappe.db.sql("""update `tab{0}` set clearance_date = %s, modified = %s 
					where name=%s""".format(d.payment_document), 
				(d.clearance_date, nowdate(), d.payment_entry))
				
				clearance_date_updated = True

		if clearance_date_updated:
			self.get_payment_entries()
			msgprint(_("Clearance Date updated"))
		else:
			msgprint(_("Clearance Date not mentioned"))
