from __future__ import unicode_literals
import frappe
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
import datetime
from datetime import datetime
import pytz


# saad 30-04-22
import random


@frappe.whitelist(allow_guest=True)
def lead_dispose_rerouting():
	lead_rule = frappe.db.sql(f""" select name, lead_length, lead_counter, assign_count_to from `tabLead Rules` where name = "LR-00029";""", as_dict= True)
	lead_list = frappe.db.sql(f""" select name,dnd,primary_mobile,assign_count,dnd,sales_person,lead_owner,disposed_by,campaign_name,email_id from `tabLead` where assign_count <= 25 and sales_person = ''and campaign_name = 'CAM00267' and dnd = 0 and disposed_by IS NOT NULL and status != 'Converted' ORDER BY modified ASC  LIMIT 2500 ;""",as_dict=1)	
	csm_list = frappe.db.sql(f""" select user.sales_person, user.user_id,daily_status, user.daily_limit, count(*) as count from `tabUser Rule`user where user.parent = '{lead_rule[0].name}' group by user.sales_person;""", as_dict= True)
	frappe.log_error(csm_list, "CSM List Rerouting 1")
	main_count = 2500

	main_length = int(lead_rule[0].lead_length)
	assign_value = int(main_count/main_length) +1
	frappe.log_error(assign_value,"Assign Value Rerouting 1")
	cc =0
	assign_limt =  0
	print("assign value..",assign_value)

	d = 1
	UTC = pytz.utc
	IST = pytz.timezone('Asia/Kolkata')
	log = []
	
	ff = 0
	for i in csm_list:
		sales_person = csm_list[ff].sales_person
		lead_owner = csm_list[ff].user_id
		print(sales_person)
		frappe.db.set_value('User Rule', {"parent":"LR-00029","sales_person":sales_person}, 'daily_status',0)
		frappe.db.commit()
		ff = ff + 1

	for i in lead_list:
		csm_list = frappe.db.sql(f""" select user.sales_person, user.user_id,daily_status, user.daily_limit, count(*) as count from `tabUser Rule`user where user.parent = '{lead_rule[0].name}' group by user.sales_person;""", as_dict= True)
		length = int(lead_rule[0].lead_length)
		trim_mob = i.primary_mobile.replace(" ", "").lstrip('+')
		check_in_time = frappe.utils.now()
		lead_mob = frappe.db.exists("Lead", {"primary_mobile": trim_mob})
		lead_email = frappe.db.exists("Lead", {"email_id": i.email_id})
		old_count = frappe.db.sql(f"select check_in_count from `tabLead` where name = '{lead_email}' or name = '{lead_mob}'",as_dict = True)
		lead_assign_count = frappe.db.sql(f"select assign_count from `tabLead` where name = '{lead_email}' or name = '{lead_mob}'",as_dict = True)
		last_active_user =frappe.db.sql(""" select last_active from `tabUser`user where name = '{0}';""".format(csm_list[d].user_id), as_dict= True)

		sales_person = csm_list[d].sales_person
		lead_owner = csm_list[d].user_id

		if sales_person == i.disposed_by:
			pass
		else:
			lead_owner = csm_list[d].user_id
			last_active = last_active_user[0].last_active
			monthly_status= csm_list[d].daily_status
			frappe.log_error(monthly_status, "Monthly Status before If statement Rerouting 1")
			overall_limit=csm_list[d].daily_limit
			frappe.log_error(overall_limit, "Overall Limit Rerouting 1")
			later_time = datetime.now()
			difference = ((later_time - last_active).total_seconds())/3600
			if overall_limit/3 > monthly_status and last_active.date() == later_time.date():
				print(f" {sales_person}__________________ in ")
				# print(last_active.date())
				# print(datetime.now())
				# print(datetime.now(IST))
				# print(lead_count_saleperson[0]['limt'])
				frappe.log_error(monthly_status, "Monthly Status after if statement Rerouting 1")
				print(monthly_status)

				frappe.db.set_value('Lead', lead_mob, {
					# 'assign_time': check_in_time,
					# 'check_in_time': check_in_time,
					"sales_person": sales_person,
					"lead_owner": lead_owner,
					'assign_count': lead_assign_count[0].assign_count + 1,
					'assign_time': datetime.now(IST),
					# 'check_in_count': old_count[0].check_in_count + 1,
					# "lead_status": "Not Contacted",
					# "campaign_name": i.campaign_name,
				})
                                #print(monthly_status)
                                #log.append(f "monthly staatus {monthly_status}")
				frappe.db.set_value('User Rule', {"parent":"LR-00029","sales_person":sales_person}, 'daily_status', monthly_status + 1 )
				frappe.db.commit()
				log.append(f" {i.name} --- assign to {sales_person} ")

		d = d + 1
		if d >= len(csm_list):
			d=0

	now = datetime.now()
	dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
	log.append(f" last call on {dt_string}")

	return log

# saad 30-04-22


@frappe.whitelist(allow_guest=True)
def lead_dispose_rerouting2():
	lead_rule = frappe.db.sql(f""" select name, lead_length, lead_counter, assign_count_to from `tabLead Rules` where name = "LR-00030";""", as_dict= True)
	lead_list = frappe.db.sql(f""" select name,dnd,primary_mobile,assign_count,dnd,sales_person,lead_owner,disposed_by,campaign_name,email_id from `tabLead` where assign_count <= 25 and dnd = 0 and sales_person = ''and campaign_name = 'CAM00038' and disposed_by IS NOT NULL and status != 'Converted' ORDER BY modified ASC  LIMIT 2500 ;""",as_dict=1)	
	frappe.log_error(lead_list, "Lead List Rerouting 2")
	csm_list = frappe.db.sql(f""" select user.sales_person, user.user_id,daily_status, user.daily_limit, count(*) as count from `tabUser Rule`user where user.parent = '{lead_rule[0].name}' group by user.sales_person;""", as_dict= True)
	frappe.log_error(csm_list, "CSM List Rerouting 2")
	main_count = 2500

	main_length = int(lead_rule[0].lead_length)
	assign_value = int(main_count/main_length) +1
	frappe.log_error(assign_value,"Assign Value Rerouting 2")
	cc =0
	assign_limt =  0
	print(assign_value)
	UTC = pytz.utc
	IST = pytz.timezone('Asia/Kolkata')
	d = 1
	log = []

	ff = 0 
	for i in csm_list:
		sales_person = csm_list[ff].sales_person
		lead_owner = csm_list[ff].user_id
		print(sales_person)
		frappe.db.set_value('User Rule', {"parent":"LR-00030","sales_person":sales_person}, 'daily_status',0)
		frappe.db.commit()
		ff = ff + 1


	for i in lead_list:
		# print(d)
		csm_list = frappe.db.sql(f""" select user.sales_person, user.user_id,daily_status, user.daily_limit, count(*) as count from `tabUser Rule`user where user.parent = '{lead_rule[0].name}' group by user.sales_person;""", as_dict= True)
		length = int(lead_rule[0].lead_length)
		trim_mob = i.primary_mobile.replace(" ", "").lstrip('+')
		check_in_time = frappe.utils.now()
		lead_mob = frappe.db.exists("Lead", {"primary_mobile": trim_mob})
		lead_email = frappe.db.exists("Lead", {"email_id": i.email_id})
		old_count = frappe.db.sql(f"select check_in_count from `tabLead` where name = '{lead_email}' or name = '{lead_mob}'",as_dict = True)
		lead_assign_count = frappe.db.sql(f"select assign_count from `tabLead` where name = '{lead_email}' or name = '{lead_mob}'",as_dict = True)
		last_active_user =frappe.db.sql(""" select last_active from `tabUser`user where name = '{0}';""".format(csm_list[d].user_id), as_dict= True)
		sales_person = csm_list[d].sales_person
		lead_owner = csm_list[d].user_id
		# print(sales_person)

		if sales_person == i.disposed_by:
			pass
		else:
			lead_owner = csm_list[d].user_id
			last_active = last_active_user[0].last_active
			monthly_status= csm_list[d].daily_status
			frappe.log_error(monthly_status, "Monthly Status before If statement Rerouting 2")
			overall_limit=csm_list[d].daily_limit
			frappe.log_error(overall_limit, "Overall Limit Rerouting 2")
			later_time = datetime.now()
			difference = ((later_time - last_active).total_seconds())/3600
			
			if overall_limit/3 > monthly_status and last_active.date() == later_time.date():
				print(f" {sales_person}__________________ in ")
				print(monthly_status)
				frappe.log_error(monthly_status, "Monthly Status after if statement Rerouting 2")
				frappe.db.set_value('Lead', lead_mob, {
					# 'assign_time': check_in_time,chanu@123
					# 'check_in_time': check_in_time,
					"sales_person": sales_person,
					"lead_owner": lead_owner,
					'assign_count': lead_assign_count[0].assign_count + 1,
					'assign_time': datetime.now(IST)
					# "lead_status": "Not Contacted",
					# "campaign_name": i.campaign_name,
				})
				print(monthly_status)
				frappe.log_error(monthly_status, "second Monthly Status after if statement Rerouting 2")
				frappe.db.set_value('User Rule', {"parent":"LR-00030","sales_person":sales_person}, 'daily_status', monthly_status + 1 )
				frappe.db.commit()
				log.append(f" {i.name} --- assign to {sales_person} ")


		d = d + 1
		if d >= len(csm_list):
			d=0

	now = datetime.now()
	dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
	log.append(f" last call on {dt_string}")

	return log

# saad 30-04-22



# @frappe.whitelist(allow_guest=True)
# def lead_dispose_rerouting():
# 	lead_rule = frappe.db.sql(f""" select name, lead_length, lead_counter, assign_count_to from `tabLead Rules` where name = "LR-00029";""", as_dict= True)
# 	lead_list = frappe.db.sql(f""" select name,primary_mobile,assign_count,dnd,sales_person,lead_owner,disposed_by,campaign_name,email_id from `tabLead` where assign_count > 1 and dnd = 1 and disposed_by IS NOT NULL  LIMIT {lead_rule[0].assign_count_to} ;""",as_dict=1)
# 	cc =0

# 	for i in lead_list:
# 		print(i.name)
# 		lead_rule = frappe.db.sql(f""" select name, lead_length, lead_counter from `tabLead Rules` where name = "LR-00029";""", as_dict= True)
# 		csm_list = frappe.db.sql(f""" select user.sales_person, user.user_id,daily_status, user.daily_limit, count(*) as count from `tabUser Rule`user where user.parent = '{lead_rule[0].name}' group by user.sales_person;""", as_dict= True)
# 		counter = cc
# 		length = int(lead_rule[0].lead_length)
# 		trim_mob = i.primary_mobile.replace(" ", "").lstrip('+')
# 		check_in_time = frappe.utils.now()
# 		lead_mob = frappe.db.exists("Lead", {"primary_mobile": trim_mob})
# 		lead_email = frappe.db.exists("Lead", {"email_id": i.email_id})
# 		old_count = frappe.db.sql(f"select check_in_count from `tabLead` where name = '{lead_email}' or name = '{lead_mob}'",as_dict = True)
# 		last_active_user =frappe.db.sql(""" select last_active from `tabUser`user where name = '{0}';""".format(csm_list[counter].user_id), as_dict= True)

# 		sales_person = csm_list[counter].sales_person
# 		lead_owner = csm_list[counter].user_id

# 		if sales_person == i.disposed_by:
# 			sales_person = csm_list[counter+1].sales_person
# 			lead_owner = csm_list[counter+1].user_id


# 		lead_owner = csm_list[counter].user_id
# 		last_active = last_active_user[0].last_active
# 		monthly_status= csm_list[counter].daily_status
# 		overall_limit=csm_list[counter].daily_limit
# 		later_time = datetime.now()
# 		difference = ((later_time - last_active).total_seconds())/3600

# 		frappe.db.set_value('Lead', lead_mob, {
# 			'assign_time': check_in_time,
# 			'check_in_time': check_in_time,
# 			"sales_person": sales_person,
# 			"lead_owner": lead_owner,
# 			'check_in_count': old_count[0].check_in_count + 1,
# 			"lead_status": "Not Contacted",
# 			"campaign_name": i.campaign_name,
# 			"dnd": 0
# 		})
# 		frappe.db.set_value('User Rule', {"parent": lead_rule[0].name,"sales_person":sales_person}, 'daily_status', monthly_status + 1 )
# 		frappe.db.set_value('Lead',"LEAD-2022-11244",{
# 						'company_name':str(random.randint(0,9854561465))})
# 		cc = cc + 1
# 		print(cc)
# 		if cc >= len(csm_list):
# 			cc=0

# 	return 	'Success'

# saad 30-04-22








# @frappe.whitelist(allow_guest=True)
# def lead_routing(lead_name, primary_mobile, email_id,campaign_name):
# 	# campaign_name="CAM00267"
# 	lead_rule = frappe.db.sql(""" select name, lead_length, lead_counter from `tabLead Rules` where new_campaign = '{0}';""".format(campaign_name), as_dict= True)
# 	csm_list = frappe.db.sql(""" select user.sales_person, user.user_id,daily_status, user.daily_limit  from `tabUser Rule`user where user.parent = '{0}';""".format(lead_rule[0].name), as_dict= True)
# 	counter = int(lead_rule[0].lead_counter)
# 	length = int(lead_rule[0].lead_length)
# 	trim_mob = primary_mobile.replace(" ", "").lstrip('+')
# 	check_in_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
# 	lead_mob = frappe.db.exists("Lead", {"primary_mobile": trim_mob})
# 	lead_email = frappe.db.exists("Lead", {"email_id": email_id})
# 	old_count = frappe.db.sql("select check_in_count from `tabLead` where name = '{0}' or name = '{1}'".format(lead_email, lead_mob),as_dict = True)
# 	try:
# 		lead_from = frappe.form_dict.get('leadfrom')
# 		parsed_url = urlparse(lead_from)
# 		utm_content = parse_qs(parsed_url.query)['utm_content'][0]
# 		utm_source = parse_qs(parsed_url.query)['utm_source'][0]
# 		utm_medium = parse_qs(parsed_url.query)['utm_medium'][0]
# 		utm_campaign_date = parse_qs(parsed_url.query)['utm_campaign'][0]
# 		# # saad 23-04-22
# 		# source_list = ['Adgebra', 'App', 'Facebook', 'Google', 'Organic', 'Direct', 'Crisp', 'Quora', 'Whatsapp', 'Email', 'PN', 'Native', 'PR', 'Reddit', 'Blogs', 'Twitter', 'Taboola', 'Telegram', 'LinkedIn', 'Internal', 'Alliance', 'Bing', 'Yahoo', 'Youtube', 'Offers', 'Messenger', 'Subscriber_List', 'Webinar']
# 		# if utm_source not in source_list:
# 		# 	original_lead = frappe.db.get_value('Customer',utm_source , 'lead_name')
# 		# 	utm_source = 'Internal'
# 		# # saad 23-04-22
# 	except:
# 		utm_content = ""
# 		utm_source = ""
# 		utm_medium = ""
# 		utm_campaign_date = ""
# 		# # saad 23-04-22
# 		# original_lead = None
# 		# # saad 23-04-22
# 	if not lead_mob:
# 		# return counter,length,lead_rule,csm_list,trim_mob,lead_mob,campaign_name,lead_name, primary_mobile, email_id,utm_source,utm_content,utm_medium,utm_campaign_date,original_lead
# 		response = assign_lead(counter,length,lead_rule,csm_list,trim_mob,lead_mob,campaign_name,lead_name, primary_mobile, email_id,lead_email)
# 		return response
# 	else:
		
# 		# return "Already Exist"
# 		if lead_email:
# 			frappe.db.set_value('Lead', lead_mob, {
# 				'assign_time': check_in_time,
# 				'check_in_time': check_in_time,
# 				'check_in_count': old_count[0].check_in_count + 1,
#                 "lead_status": "Not Contacted",
# 				"campaign_name": campaign_name,
#                 "dnd": 0
# 			})
# 		else:
# 			frappe.db.set_value('Lead', lead_mob, {
				
# 				'assign_time': check_in_time,
# 				'check_in_time': check_in_time,
# 				'check_in_count': old_count[0].check_in_count + 1,
#                 "lead_status": "Not Contacted",
#                 "email_id": email_id or "",
# 				"campaign_name": campaign_name,
#                 "dnd": 0
# 			})
# 		frappe.db.commit()
# 		return "Check In Updated"
    	
# def assign_lead(counter,length,lead_rule,csm_list,trim_mob,lead_mob,campaign_name,lead_name, primary_mobile, email_id,lead_email) :
# 	# return counter,length,lead_rule,csm_list,trim_mob,lead_mob,campaign_name,lead_name, primary_mobile, email_id,utm_source,utm_content,utm_medium
# 	current_index=frappe.db.sql(""" select current_index from `tabLead Rules` where new_campaign = '{0}';""".format(campaign_name), as_dict= True)
# 	if(current_index[0].current_index<length):	
# 		if counter <= length-1:
# 			# return csm_list
# 			last_active_user =frappe.db.sql(""" select last_active from `tabUser`user where name = '{0}';""".format(csm_list[counter].user_id), as_dict= True)
# 			sales_person = csm_list[counter].sales_person
# 			lead_owner = csm_list[counter].user_id
# 			last_active = last_active_user[0].last_active
# 			monthly_status= csm_list[counter].daily_status
# 			overall_limit=csm_list[counter].daily_limit
# 			later_time = datetime.now()
# 			difference = ((later_time - last_active).total_seconds())/3600

# 			if monthly_status <= overall_limit -1 and difference <= 3 :
# 				if lead_email:
# 					LeadInsert = frappe.get_doc({
# 						"doctype": "Lead",
# 						"lead_name": frappe.form_dict.get('lead_name') or "",
# 						"last_name": frappe.form_dict.get('last_name') or "",
# 						#  "email_id": "",
# 						"primary_mobile": trim_mob,
# 						"grade": frappe.form_dict.get('grade'),
# 						"status": "Lead",
# 						"lead_status": "Not Contacted",
# 						"campaign_name": campaign_name,
# 						"country": frappe.form_dict.get('country'),
# 						"assign_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
# 						"temperature": "Very Hot",
# 						"language": frappe.form_dict.get('language'),
# 						# "ip_address": frappe.form_dict.get('ip_address') or "",
# 						"sales_person": sales_person,
# 						"lead_owner": lead_owner,
# 						# "sms_otp_verified": 1,
# 						# "utm_source": utm_source,
# 						# "utm_medium":utm_medium,
# 						# "utm_campaign_date":utm_campaign_date,
# 						# "utm_content": utm_content,
# 						# "original_lead": original_lead,
# 						# "lead_property": frappe.form_dict.get('lead_property') or "",
# 						# "investment_type": frappe.form_dict.get('investment_type') or ""
# 						}).insert(ignore_permissions=True)
# 					LeadInsert.save()
# 				else:
# 					LeadInsert = frappe.get_doc({
# 						"doctype": "Lead",
# 						"lead_name": frappe.form_dict.get('lead_name') or "",
# 						"last_name": frappe.form_dict.get('last_name') or "",
# 						"email_id": email_id,
# 						"primary_mobile": trim_mob,
# 						"grade": frappe.form_dict.get('grade'),
# 						"status": "Lead",
# 						"lead_status": "Not Contacted",
# 						"campaign_name": campaign_name,
# 						"country": frappe.form_dict.get('country'),
# 						"assign_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
# 						"temperature": "Very Hot",
# 						"language": frappe.form_dict.get('language'),
# 						# "ip_address": frappe.form_dict.get('ip_address') or "",
# 						"sales_person": sales_person,
# 						"lead_owner": lead_owner,
# 						# "sms_otp_verified": 1,
# 						# "utm_source": utm_source,
# 						# "utm_medium": utm_medium,
# 						# "utm_campaign_date":utm_campaign_date,
# 						# "utm_content":utm_content,
# 						# "original_lead": original_lead,
# 						# "lead_property": frappe.form_dict.get('lead_property') or "",
# 						# "investment_type": frappe.form_dict.get('investment_type') or ""
# 						}).insert(ignore_permissions=True)
# 					LeadInsert.save()
				
# 				frappe.db.set_value('User Rule', {"parent": lead_rule[0].name,"sales_person":csm_list[counter].sales_person}, 'daily_status', monthly_status + 1 )	
				
# 				if counter+1==length:
# 					frappe.db.set_value('Lead Rules', lead_rule[0].name, {
# 					'lead_counter':0,
# 					'current_index':0
# 					})
# 				else :
# 					frappe.db.set_value('Lead Rules', lead_rule[0].name, {
# 					'lead_counter':counter+1,
# 					'current_index':0
# 					})
# 				frappe.db.commit()
# 				return sales_person,lead_owner,last_active,monthly_status,overall_limit,later_time,difference,original_lead
# 			else :
# 				if counter+1==length:
# 					frappe.db.set_value('Lead Rules', lead_rule[0].name, {
# 					'lead_counter':0,
# 					'current_index':current_index[0].current_index+1
# 					})
# 					assign_lead(0,length,lead_rule,csm_list,trim_mob,lead_mob,campaign_name,lead_name, primary_mobile, email_id,lead_email)
					
					
# 				else :
# 					frappe.db.set_value('Lead Rules', lead_rule[0].name, {
# 					'lead_counter':counter+1,
# 					'current_index':current_index[0].current_index+1
# 					})
# 					assign_lead(counter+1,length,lead_rule,csm_list,trim_mob,lead_mob,campaign_name,lead_name, primary_mobile, email_id,lead_email)
			
# 			return counter,length,lead_rule,csm_list,trim_mob,lead_mob,campaign_name,lead_name, primary_mobile, email_id,sales_person,lead_owner,last_active,monthly_status,overall_limit,difference

		
# 		else :
# 			return "Errorrrrrrrrr"
# 	else:
# 		if lead_email:
# 			LeadInsert = frappe.get_doc({
# 				"doctype": "Lead",
# 				"lead_name": frappe.form_dict.get('lead_name') or "",
# 				"last_name": frappe.form_dict.get('last_name') or "",
# 				# "email_id": "",
# 				"primary_mobile": trim_mob,
# 				"grade": frappe.form_dict.get('grade'),
# 				"status": "Lead",
# 				"lead_status": "Not Contacted",
# 				"campaign_name": campaign_name,
# 				"country": frappe.form_dict.get('country'),
# 				"assign_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
# 				"temperature": "Very Hot",
# 				# "utm_source": utm_source,
# 				# "utm_medium": utm_medium,
# 				# "utm_campaign_date":utm_campaign_date,
# 				# "utm_content":utm_content,
# 				# "original_lead": original_lead,
# 				"language": frappe.form_dict.get('language')
# 				}).insert(ignore_permissions=True)
# 			LeadInsert.save()
# 		else:
# 			LeadInsert = frappe.get_doc({
# 				"doctype": "Lead",
# 				"lead_name": frappe.form_dict.get('lead_name') or "",
# 				"last_name": frappe.form_dict.get('last_name') or "",
# 				"email_id": email_id,
# 				"primary_mobile": trim_mob,
# 				"grade": frappe.form_dict.get('grade'),
# 				"status": "Lead",
# 				"lead_status": "Not Contacted",
# 				"campaign_name": campaign_name,
# 				"country": frappe.form_dict.get('country'),
# 				"assign_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
# 				"temperature": "Very Hot",
# 				# "utm_source": utm_source,
# 				# "utm_medium": utm_medium,
# 				# "utm_campaign_date":utm_campaign_date,
# 				# "utm_content": utm_content,
# 				# "original_lead": original_lead,
# 				"language": frappe.form_dict.get('language')
# 				}).insert(ignore_permissions=True)
# 			LeadInsert.save()
# 		frappe.db.set_value('Lead Rules', lead_rule[0].name, {
# 			# 'lead_counter':counter+1,
# 			'current_index':0
# 			})
# 		frappe.db.commit()
# 		return "Limit exceeded, Lead inserted"

		
					
