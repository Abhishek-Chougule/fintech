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
import datetime
from datetime import datetime, timedelta
import pytz


@frappe.whitelist(allow_guest=True)
def lead_insertion():
	lead_email = frappe.form_dict.get('email_id')
	lead_name = frappe.form_dict.get('lead_name')
	mobile = frappe.form_dict.get('primary_mobile')
	trim_mob = mobile.replace(" ", "").lstrip('+')
	lead_mob = frappe.db.exists("Lead", {"primary_mobile": trim_mob})
# saad 23 may 22
	UTC = pytz.utc
	IST = pytz.timezone('Asia/Kolkata')

	conversion_status = False

	url = "https://hash.capitalvia.com/api/method/lead_validation"

	payload = json.dumps({
	"email_id": lead_email,
	"status": "Converted",
	"pan_number": "pan"
	})

	headers = {
	'Content-Type': 'application/json',
	'Cookie': 'full_name=Guest; sid=Guest; system_user=no; user_id=Guest; user_image='
	}

	response = requests.request("GET", url, headers=headers, data=payload)
	resp = json.loads(response.text)

	conversion_status = resp['messages']
	if conversion_status ==True:
		return "Already converted"
# saad 23 may 22


	
	if not lead_mob:
		if conversion_status == False:
			LeadInsert = frappe.get_doc({
				"doctype": "Lead",
				"lead_name": frappe.form_dict.get('lead_name') or "",
				"last_name": frappe.form_dict.get('last_name') or "",
				"email_id": frappe.form_dict.get('email_id') or "",
				"primary_mobile": frappe.form_dict.get('primary_mobile') or "",
				"grade": frappe.form_dict.get('grade'),
				"status": "Lead",
				"campaign_name": frappe.form_dict.get('cam_id'),
				"country": frappe.form_dict.get('country'),
				"assign_time": datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S'),
				"temperature": "Very Hot",
				"language": frappe.form_dict.get('language'),
				# "ip_address": frappe.form_dict.get('ip_address') or "",
				"sales_person": "",
				"lead_owner": ""
				# "sms_otp_verified": 1,
				# "utm_source": frappe.form_dict.get('utm_source') or "",
				# "utm_medium": frappe.form_dict.get('utm_medium') or "",
				# "utm_campaign_date": frappe.form_dict.get('utm_campaign_date') or "",
				# "utm_content": frappe.form_dict.get('utm_content') or "",
				# "lead_property": frappe.form_dict.get('lead_property') or "",
				# "investment_type": frappe.form_dict.get('investment_type') or ""
			}).insert(ignore_permissions=True)
			LeadInsert.save()
			frappe.db.commit()
			return LeadInsert
		elif conversion_status == True:
			return "Already converted"
	else:
		return "Already Exists"


@frappe.whitelist(allow_guest=True)
def lead_routing(lead_name, primary_mobile, email_id):
	campaign_name = frappe.form_dict.get('campaign_name')
	# return campaign_name
	lead_rule = frappe.db.sql(""" select name, lead_length, lead_counter from `tabLead Rules` where new_campaign = '{0}';""".format(campaign_name), as_dict= True)
	csm_list = frappe.db.sql(""" select user.sales_person, user.user_id, user.last_active from `tabUser Rule`user where user.parent = '{0}';""".format(lead_rule[0].name), as_dict= True)
	# return csm_list
	counter = int(lead_rule[0].lead_counter)
	lenght = int(lead_rule[0].lead_length)
	# return lead_rule[0].lead_length
	# for d in lenght:
	active_time = lead_rule[0].last_active
	cur_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	trim_mob = primary_mobile.replace(" ", "").lstrip('+')
	lead_mob = frappe.db.exists("Lead", {"primary_mobile": trim_mob})
	# return cur_time, active_time
	UTC = pytz.utc
	IST = pytz.timezone('Asia/Kolkata')
	if not lead_mob:

		if counter < lenght:
			sales_person = csm_list[counter].sales_person
			lead_owner = csm_list[counter].user_id
			
			frappe.db.set_value('Lead Rules', lead_rule[0].name, {
				'lead_counter': counter + 1
				})
			frappe.db.commit()
		else:
			sales_person = csm_list[0].sales_person
			lead_owner = csm_list[0].user_id
			frappe.db.set_value('Lead Rules', lead_rule[0].name, {
				'lead_counter': 1
				})
			frappe.db.commit()


		# LeadInsert = frappe.new_doc("Lead")
		# LeadInsert.primary_mobile = trim_mob
		# LeadInsert.email_id = email_id
		# LeadInsert.lead_name = lead_name
		# LeadInsert.temperature = "Very Hot"
		# LeadInsert.status = "Lead"
		# LeadInsert.lead_status = "Not Contacted"
		# LeadInsert.sales_person = sales_person
		# LeadInsert.lead_owner = lead_owner
		# LeadInsert.campaign_name = campaign_name
		# LeadInsert.insert(ignore_permissions = True)

		# return frappe.form_dict.get('campaign_name')
		LeadInsert = frappe.get_doc({
			"doctype": "Lead",
			"lead_name": frappe.form_dict.get('lead_name') or "",
			"last_name": frappe.form_dict.get('last_name') or "",
			"email_id": email_id,
			"primary_mobile": trim_mob,
			"grade": frappe.form_dict.get('grade'),
			"status": "Lead",
			# "campaign_name": campaign_name,
			"country": frappe.form_dict.get('country'),
			"assign_time": datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S'),
			"temperature": "Very Hot",
			"language": frappe.form_dict.get('language'),
			# "ip_address": frappe.form_dict.get('ip_address') or "",
			"sales_person": sales_person,
			"lead_owner": lead_owner
			# "sms_otp_verified": 1,
			# "utm_source": frappe.form_dict.get('utm_source') or "",
			# "utm_medium": frappe.form_dict.get('utm_medium') or "",
			# "utm_campaign_date": frappe.form_dict.get('utm_campaign_date') or "",
			# "utm_content": frappe.form_dict.get('utm_content') or "",
			# "lead_property": frappe.form_dict.get('lead_property') or "",
			# "investment_type": frappe.form_dict.get('investment_type') or ""
		}).insert(ignore_permissions=True)
		LeadInsert.save()
		return "Success"
	
	else:
		return "Already Exists"