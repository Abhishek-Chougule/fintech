# -*- coding: utf-8 -*-
# Copyright (c) 2020, GoElite and contributors
# For license information, please see license.txt
# Created By- Ashish Bankar

from __future__ import unicode_literals
import frappe, json
# from frappe.utils import get_site_url, get_url_to_form, get_link_to_form
from werkzeug.wrappers import Response
from frappe.utils.response import build_response
from datetime import datetime, timedelta
import requests
import json
import time
import requests
import binascii
from Crypto import Random
from Crypto.Cipher import AES
import base64
from binhex import binhex, hexbin
import string
import random
from frappe.utils.password import get_decrypted_password

#Lead Disposition API
@frappe.whitelist()
def lead_dispose(doctype, name, assign_count, sales_person, lead_owner, lead_status, login_user):
	person = ""
	owner = ""
	# store_cust = frappe.db.get_list('Customer',{'lead_name': name},'name')
	# if lead_status== 'Converted' or store_cust:
	# 	frappe.throw("This Lead can't be Dispose because Converted in Customer")
	# 	return "Not Dispose"

	# else:
	frappe.db.set_value('Lead', name, {
				'sales_person': person,
				'lead_owner': owner,
				'assign_count': assign_count,
				# 'assign_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
				# 'contact_date': "",
				# 'ends_on': "",
				'disposed_by': login_user
			})

	store_name = frappe.db.get_list('Opportunity',{'party_name': name},'name')
	for d in store_name:

		frappe.db.set_value('Opportunity',d.name, {
			'sales_person': ""
		})

		if not frappe.db.get_value('Opportunity', d.name, 'price_list'):
			frappe.db.set_value('Opportunity',d.name, {
			'price_list': "Monthly (INR)"
		})

	return "success"

#Do Not Disturb
@frappe.whitelist()
def mark_dnd_lead(doctype, name):
	person = ""
	owner = ""
	frappe.db.set_value('Lead', name, {
				'sales_person': person,
				'lead_owner': owner,
				'dnd': 1,
				# 'assign_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
				# 'contact_date': "",
				# 'ends_on': ""
			})
	frappe.db.commit()
	return "success"

#Lead Transfer
@frappe.whitelist()
def update_customer_lead(doctype, name, sales_person, assign_count):
	print("doctype", doctype)
	store_opp = frappe.db.get_list('Opportunity',{'party_name': name},'name')
	if store_opp:
		for g in store_opp:
			frappe.db.set_value('Opportunity',g.name, {
			'sales_person': sales_person
		})

		store_cust = frappe.db.get_list('Customer',{'lead_name': name},'name')
		if store_cust:
			for d in store_cust:
				frappe.db.set_value('Customer',d.name, {
					'sales_person': sales_person,
					'assign_count': assign_count,
					'assign_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
				})

				store_py_entry = frappe.db.get_list('Payment Entry',{'party': d.name},'name')
				if store_py_entry:
					for e in store_py_entry: 
						frappe.db.set_value('Payment Entry',e.name, {
							'sales_person': sales_person
				
						})
				
				store_sales_inv = frappe.db.get_list('Sales Invoice',{'customer': d.name},'name')
				if store_sales_inv:
					for f in store_sales_inv:
						frappe.db.set_value('Sales Invoice',e.name, {
							'sales_person': sales_person
				
						})

# #Delete Auto customer Creation
# @frappe.whitelist()
# def delete_auto_customer_creation(doctype, name):
# 	frappe.db.delete(doctype, {
#     	'name': name
# 	})

# 	return "Delete Success"


# @frappe.whitelist(allow_guest=True)
# def fee_request_consent(name, consent):
# 	store = frappe.db.exists("Fee Request", name, 'consent')
# 	if name and consent and store:
# 		opp_no = frappe.db.get_value("Fee Request", name, 'opportunity_number')
# 		cust_name = frappe.db.get_value("Opportunity", opp_no, 'customer_name')
# 		frappe.db.set_value('Fee Request', name, {
# 							'consent_store': consent,
# 							'approved_by': cust_name,
# 							'approved_on': datetime.now(),
# 							'ip_address' : frappe.local.request_ip
# 						})
# 		frappe.db.commit()
# 		# return "Thank You for your Consent"
# 		return frappe.redirect_to_message('Thank You',"Success Message")
# 	if not store:
# 		return frappe.redirect_to_message('Thank You',"Success Message")
# 		# "Your Consent already Store"
		

# @frappe.whitelist(allow_guest=True)
# def risk_profile_consent(name, consent):
# 	store = frappe.db.exists("Risk Profile", name, 'consent')
# 	if name and consent == "Yes, I Agree" and store:
# 		frappe.db.set_value('Risk Profile', name, {
# 							'consent': consent,
# 							'consent_time': datetime.now(),
# 							'ip_address' : frappe.local.request_ip,
# 							'workflow_state': "Consented"
# 						})
# 		frappe.db.commit()
# 		return frappe.redirect_to_message('Thank You',"Success Message")

# 	if name and consent == "Need Modification!" and store:
# 		frappe.db.set_value('Risk Profile', name, {
# 							'consent': consent,
# 							'consent_time': datetime.now(),
# 							'ip_address' : frappe.local.request_ip,
# 							'workflow_state': "No Consent"
# 						})
# 		frappe.db.commit()
# 		return frappe.redirect_to_message('Thank You',"Success Message")

# 	if not store:
# 		return frappe.redirect_to_message('Thank You',"Your Consent already Store")



# @frappe.whitelist(allow_guest=True)
# def outsider_employee_login(emp, time, log):
# 	request_url = 'https://geolocation-db.com/jsonp/' + frappe.local.request_ip
# 	response = requests.get(request_url)
# 	result = response.content.decode()
# 	result = result.split("(")[1].strip(")")
# 	result  = json.loads(result)
	
# 	checkin = frappe.get_doc({
# 		"doctype": "Employee Checkin",
# 		"employee": emp,
# 		"time": datetime.now(),
# 		'log_type': log,
# 		'ip_address': frappe.local.request_ip,
# 		'location': result['city']
# 	}).insert()
# 	frappe.db.commit()
	
# 	return 200

# @frappe.whitelist(allow_guest=True)
# def contact_email_mapping(name, email):
# 	si_list = frappe.db.get_list('Sales Invoice',
# 		filters={
# 			'customer': name,
# 			'contact_email': '' 
# 		},
# 		fields=['name']
# 	)
# 	for d in si_list:
# 		# raise frappe.PermissionError(name)
# 		# doc = frappe.db.set_value('sales Invoice', d.name, {
# 		# 		'contact_email': email})
# 		# doc.insert()
# 		frappe.db.sql("UPDATE `tabSales Invoice` SET contact_email = '{0}' WHERE customer = '{1}';".format(email, name))
# 		frappe.db.commit()
# 	return 200