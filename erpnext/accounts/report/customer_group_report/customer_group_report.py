# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from erpnext.accounts.utils import get_child_cost_centers

def execute(filters=None):
	columns =get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	return  [
		("Branch") + ":Data:100",
		("Domestic")+ ":Currency:100",
		("Internal") + ":Currency:100",
		("Government Organization") +":Currency:100",
		("All Customer Group") + ":Currency:100",
		("AWBI")+ ":Currency:100",
		("Corporate Agency") + ":Currency:100",
		("International") +":Currency:100",
		("Dzongs") +":Currency:100",
		("Arm Force") + ":Currency:100",
		("Furniture Units")+ ":Currency:100",
		("Royal & VVIP") + ":Currency:100",
		("Rural") +":Currency:100",
		("Lhakhangs & Goendey") +":Currency:100",
	]


def get_data(filters):
	query ="""select branch, 
		case when customer_group = 'Domestic' then sum(grand_total) end as 'Domestic', 
		case when customer_group ='Internal-NRDCL' then sum(grand_total) end as 'Internal', 
		case when customer_group ='Government Organization' then sum(grand_total) end as 'Government Organization', 
		case when customer_group ='Exporters' then sum(grand_total) end as 'Exporters', 
		case when customer_group ='AWBI' then sum(grand_total) end as 'AWBI', 
		case when customer_group ='Corporate Agency' then sum(grand_total) end as 'Corporate Agency', 
		case when customer_group ='International Agency' then sum(grand_total) end as 'International',
		case when customer_group ='Dzongs' then sum(grand_total) end as 'Dzongs', 
        case when customer_group ='Armed Force' then sum(grand_total) end as 'Arm Force', 
        case when customer_group ='Furniture Units' then sum(grand_total) end as 'Furniture Units', 
        case when customer_group ='Dzongs & Lhakhang Constructions' then sum(grand_total) end as 'Dzongs & Lhakhang Constructions', 
        case when customer_group ='Government Institutions' then sum(grand_total) end as 'Rural', 
		case when customer_group ='Government Organizations/Institutions' then sum(grand_total) end as 'Government Organizations/Institutions', 
        case when customer_group ='International Agency' then sum(grand_total) end as 'Furniture Units', 
        case when customer_group ="People's Project" then sum(grand_total) end as 'Royal & VVIP', 
        case when customer_group ='Rural' then sum(grand_total) end as 'Rural', 
        case when customer_group ='Lhakhangs & Goendey' then sum(grand_total) end as 'Lhakhangs'  
	from `tabSales Invoice` where docstatus = 1 """
	
	if not filters.cost_center:
		return ""

	if not filters.branch:	
		all_ccs = get_child_cost_centers(filters.cost_center)
		query += " and branch in (select name from `tabBranch` b where b.cost_center in {0} )".format(tuple(all_ccs))
	else:
		branch = str(filters.get("branch"))
		branch = branch.replace(' - NRDCL','')
		query += " and branch = \'"+branch+"\'"

	if filters.get("from_date") and filters.get("to_date"):
		query += " and posting_date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'"

	query += " group by branch"

	return frappe.db.sql(query)		
