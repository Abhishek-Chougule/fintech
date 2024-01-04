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
from urllib.parse import urlparse
from urllib.parse import parse_qs
from datetime import datetime, timedelta
import pytz

@frappe.whitelist(allow_guest=True)
def lead_routing(lead_name, primary_mobile, email_id,campaign_name):
	# campaign_name="CAM00267"
	lead_rule = frappe.db.sql(""" select name, lead_length, lead_counter from `tabLead Rules` where new_campaign = '{0}';""".format(campaign_name), as_dict= True)
	csm_list = frappe.db.sql(""" select user.sales_person, user.user_id,daily_status, user.daily_limit  from `tabUser Rule`user where user.parent = '{0}';""".format(lead_rule[0].name), as_dict= True)
	counter = int(lead_rule[0].lead_counter)
	length = int(lead_rule[0].lead_length)
	trim_mob = primary_mobile.replace(" ", "").lstrip('+')
	check_in_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	#check_in_time = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')
	lead_mob = frappe.db.exists("Lead", {"primary_mobile": trim_mob})
	lead_email = frappe.db.exists("Lead", {"email_id": email_id})
	old_count = frappe.db.sql("select check_in_count from `tabLead` where name = '{0}' or name = '{1}'".format(lead_email, lead_mob),as_dict = True)
# saad 23 may 22
	UTC = pytz.utc
	IST = pytz.timezone('Asia/Kolkata')
	conversion_status = False

	url = "https://hash.capitalvia.com/api/method/lead_validation"

	payload = json.dumps({
	"email_id": email_id,
	"status": "Converted",
	"pan_number": "pan"
	})

	headers = {
	'Content-Type': 'application/json',
	'Cookie': 'full_name=Guest; sid=Guest; system_user=no; user_id=Guest; user_image='
	}

	response = requests.request("GET", url, headers=headers, data=payload)
	resp = json.loads(response.text)

	# saad 23 may 22
	if not lead_mob:
		# return counter,length,lead_rule,csm_list,trim_mob,lead_mob,campaign_name,lead_name, primary_mobile, email_id
		response = assign_lead(counter,length,lead_rule,csm_list,trim_mob,lead_mob,campaign_name,lead_name, primary_mobile, email_id,lead_email)
		return response
	else:
		
		# return "Already Exist"
		if lead_email:
			frappe.db.set_value('Lead', lead_mob, {
				'assign_time': check_in_time,
				'check_in_time': check_in_time,
				'check_in_count': old_count[0].check_in_count + 1,
                "lead_status": "Not Contacted",
				"campaign_name": campaign_name,
                "dnd": 0
			})
		else:
			frappe.db.set_value('Lead', lead_mob, {
				
				'assign_time': check_in_time,
				'check_in_time': check_in_time,
				'check_in_count': old_count[0].check_in_count + 1,
                "lead_status": "Not Contacted",
                "email_id": email_id or "",
				"campaign_name": campaign_name,
                "dnd": 0
			})
		frappe.db.commit()
		return "Check In Updated"
    	

def assign_lead(counter,length,lead_rule,csm_list,trim_mob,lead_mob,campaign_name,lead_name, primary_mobile, email_id,lead_email) :
	# return counter,length,lead_rule,csm_list,trim_mob,lead_mob,campaign_name,lead_name, primary_mobile, email_id
	UTC = pytz.utc
	IST = pytz.timezone('Asia/Kolkata')
	current_index=frappe.db.sql(""" select current_index from `tabLead Rules` where new_campaign = '{0}';""".format(campaign_name), as_dict= True)
	if(current_index[0].current_index<length):	
		if counter <= length-1:
			# return csm_list
			last_active_user =frappe.db.sql(""" select last_active from `tabUser`user where name = '{0}';""".format(csm_list[counter].user_id), as_dict= True)
			sales_person = csm_list[counter].sales_person
			lead_owner = csm_list[counter].user_id
			last_active = last_active_user[0].last_active
			monthly_status= csm_list[counter].daily_status
			overall_limit=csm_list[counter].daily_limit
			later_time = datetime.now()
			difference = ((later_time - last_active).total_seconds())/3600

			if monthly_status <= overall_limit -1 and difference <= 3 :
				if lead_email:
					LeadInsert = frappe.get_doc({
						"doctype": "Lead",
						"lead_name": frappe.form_dict.get('lead_name') or "",
						"last_name": frappe.form_dict.get('last_name') or "",
						#  "email_id": "",
						"primary_mobile": trim_mob,
						"grade": frappe.form_dict.get('grade'),
						"status": "Lead",
						"lead_status": "Not Contacted",
						"campaign_name": campaign_name,
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
				else:
					LeadInsert = frappe.get_doc({
						"doctype": "Lead",
						"lead_name": frappe.form_dict.get('lead_name') or "",
						"last_name": frappe.form_dict.get('last_name') or "",
						"email_id": email_id,
						"primary_mobile": trim_mob,
						"grade": frappe.form_dict.get('grade'),
						"status": "Lead",
						"lead_status": "Not Contacted",
						"campaign_name": campaign_name,
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
				
				frappe.db.set_value('User Rule', {"parent": lead_rule[0].name,"sales_person":csm_list[counter].sales_person}, 'daily_status', monthly_status + 1 )	
				
				if counter+1==length:
					frappe.db.set_value('Lead Rules', lead_rule[0].name, {
					'lead_counter':0,
					'current_index':0
					})
				else :
					frappe.db.set_value('Lead Rules', lead_rule[0].name, {
					'lead_counter':counter+1,
					'current_index':0
					})
				frappe.db.commit()
				return sales_person,lead_owner,last_active,monthly_status,overall_limit,later_time,difference
			else :
				if counter+1==length:
					frappe.db.set_value('Lead Rules', lead_rule[0].name, {
					'lead_counter':0,
					'current_index':current_index[0].current_index+1
					})
					assign_lead(0,length,lead_rule,csm_list,trim_mob,lead_mob,campaign_name,lead_name, primary_mobile, email_id,lead_email)
					
					
				else :
					frappe.db.set_value('Lead Rules', lead_rule[0].name, {
					'lead_counter':counter+1,
					'current_index':current_index[0].current_index+1
					})
					assign_lead(counter+1,length,lead_rule,csm_list,trim_mob,lead_mob,campaign_name,lead_name, primary_mobile, email_id,lead_email)
			
			return counter,length,lead_rule,csm_list,trim_mob,lead_mob,campaign_name,lead_name, primary_mobile, email_id,sales_person,lead_owner,last_active,monthly_status,overall_limit,difference
		
		else :
			return "Errorrrrrrrrr"
	else:
		if lead_email:
			LeadInsert = frappe.get_doc({
				"doctype": "Lead",
				"lead_name": frappe.form_dict.get('lead_name') or "",
				"last_name": frappe.form_dict.get('last_name') or "",
				# "email_id": "",
				"primary_mobile": trim_mob,
				"grade": frappe.form_dict.get('grade'),
				"status": "Lead",
				"lead_status": "Not Contacted",
				"campaign_name": campaign_name,
				"country": frappe.form_dict.get('country'),
				"assign_time": datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S'),
				"temperature": "Very Hot",
				"language": frappe.form_dict.get('language')
				}).insert(ignore_permissions=True)
			LeadInsert.save()
		else:
			LeadInsert = frappe.get_doc({
				"doctype": "Lead",
				"lead_name": frappe.form_dict.get('lead_name') or "",
				"last_name": frappe.form_dict.get('last_name') or "",
				"email_id": email_id,
				"primary_mobile": trim_mob,
				"grade": frappe.form_dict.get('grade'),
				"status": "Lead",
				"lead_status": "Not Contacted",
				"campaign_name": campaign_name,
				"country": frappe.form_dict.get('country'),
				"assign_time": datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S'),
				"temperature": "Very Hot",
				"language": frappe.form_dict.get('language')
				}).insert(ignore_permissions=True)
			LeadInsert.save()
		frappe.db.set_value('Lead Rules', lead_rule[0].name, {
			# 'lead_counter':counter+1,
			'current_index':0
			})
		frappe.db.commit()
		return "Limit exceeded, Lead inserted"

		
					
