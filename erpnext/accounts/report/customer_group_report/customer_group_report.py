# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns =get_columns()
	data = get_data()
	return columns, data

def get_columns():
	cols = [
		("Branch") + ":Data:100",
		]
		
