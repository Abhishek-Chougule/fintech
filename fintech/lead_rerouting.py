from __future__ import unicode_literals
# import frappe
# from frappe.utils import get_site_url, get_url_to_form, get_link_to_form
# from werkzeug.wrappers import Response
# from frappe.utils.response import build_response
# from datetime import datetime, timedelta
# import requests
# import json
# import time
# import requests
# import datetime
# from urllib.parse import urlparse
# from urllib.parse import parse_qs
# from datetime import datetime, timedelta

print("Test")
def lead_rerouting():
	print("!!!!!!!!!!!!!!!!")
	lead_rule = frappe.db.sql(""" select name, lead_length, lead_counter from `tabLead Rules` where new_campaign = '{0}';""".format('CAM00267'), as_dict= True)
	csm_list = frappe.db.sql(""" select user.sales_person, user.user_id,user.daily_status, user.daily_limit  from `tabUser Rule`user where user.parent = '{0}';""".format(lead_rule[0].name), as_dict= True)
	
	for x in csm_list:
		frappe.db.set_value('User Rule', {"parent": lead_rule[0].name,"sales_person":x["sales_person"]}, 'daily_status',0)
	frappe.db.commit()
	lead_list = frappe.db.sql("select * from `tabLead` where (lead_owner ='' or lead_owner is null) and (sales_person ='' or sales_person is null) and lead_status='Not Contacted';"  , as_dict = True)
	for x in lead_list:
		campaign_name=x["campaign_name"]
		lead_rule = frappe.db.sql(""" select name, lead_length, lead_counter from `tabLead Rules` where new_campaign = '{0}';""".format('CAM00267'), as_dict= True)
		csm_list = frappe.db.sql(""" select user.sales_person, user.user_id,user.daily_status, user.daily_limit  from `tabUser Rule`user where user.parent = '{0}';""".format(lead_rule[0].name), as_dict= True)
		counter = int(lead_rule[0].lead_counter)
		length = int(lead_rule[0].lead_length)
		current_index=frappe.db.sql(""" select current_index from `tabLead Rules` where new_campaign = '{0}';""".format('CAM00267'), as_dict= True)
		# return campaign_name,lead_rule,csm_list,counter,length,current_index
		response=lead_rerouting_by_csm(campaign_name,lead_rule,csm_list,counter,length,current_index,x,)
	return response



def lead_rerouting_by_csm(campaign_name,lead_rule,csm_list,counter,length,current_index,x):
	last_active_user =frappe.db.sql(""" select last_active from `tabUser`user where name = '{0}';""".format(csm_list[counter].user_id), as_dict= True)
	sales_person = csm_list[counter].sales_person
	lead_owner = csm_list[counter].user_id
	last_active = last_active_user[0].last_active
	monthly_status= csm_list[counter].daily_status
	overall_limit=csm_list[counter].daily_limit
	later_time = datetime.now()
	difference = ((later_time - last_active).total_seconds())/3600
	current_index=frappe.db.sql(""" select current_index from `tabLead Rules` where new_campaign = '{0}';""".format('CAM00267'), as_dict= True)
	
	# return last_active_user,sales_person,lead_owner,last_active,monthly_status,overall_limit,difference
	if(current_index[0].current_index<length):
		if monthly_status <= overall_limit -1 and difference <= 3 :
			
			frappe.db.set_value('Lead', x['name'], {
				'sales_person':sales_person,
				'lead_owner':lead_owner
				})
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
		else :
			if counter+1==length:
				frappe.db.set_value('Lead Rules', lead_rule[0].name, {
					'lead_counter':0,
					'current_index':current_index[0].current_index+1
					})
				
				lead_rerouting_by_csm(campaign_name,lead_rule,csm_list,0,length,current_index,x)
			else :
				frappe.db.set_value('Lead Rules', lead_rule[0].name, {
					'lead_counter':counter+1,
					'current_index':current_index[0].current_index+1
					})
				
				lead_rerouting_by_csm(campaign_name,lead_rule,csm_list,counter+1,length,current_index,x)
	else :
		return 'Error'
	return 200
			



















	# # campaign_name="CAM00267"
	# lead_list = frappe.db.sql("select * from `tabLead` where lead_owner ='' and sales_person ='';", as_dict = True)
	# for x in lead_list:
	# 	campaign_name=x["campaign_name"]
	# 	lead_rule = frappe.db.sql(""" select name, lead_length, lead_counter from `tabLead Rules` where new_campaign = '{0}';""".format(campaign_name), as_dict= True)
	# 	csm_list = frappe.db.sql(""" select user.sales_person, user.user_id, user.last_active,user.monthly_status, user.overall_limit  from `tabUser Rule`user where user.parent = '{0}';""".format(lead_rule[0].name), as_dict= True)
	# 	counter = int(lead_rule[0].lead_counter)
	# 	length = int(lead_rule[0].lead_length)
	# 	current_index=frappe.db.sql(""" select current_index from `tabLead Rules` where new_campaign = '{0}';""".format(campaign_name), as_dict= True)
	# 	if(current_index[0].current_index<length):
	# 		last_active_user =frappe.db.sql(""" select last_active from `tabUser`user where name = '{0}';""".format(csm_list[counter].user_id), as_dict= True)
	# 		sales_person = csm_list[counter].sales_person
	# 		lead_owner = csm_list[counter].user_id
	# 		last_active = last_active_user[0].last_active
	# 		monthly_status= csm_list[counter].monthly_status
	# 		overall_limit=csm_list[counter].overall_limit
	# 		later_time = datetime.now()
	# 		difference = ((later_time - last_active).total_seconds())/3600
	# 		# return sales_person,lead_owner,monthly_status,difference,overall_limit-1
	# 		if monthly_status <= overall_limit -1 and difference <= 3 :
	# 				frappe.db.set_value('Lead', x['name'], {
	# 				'sales_person':sales_person,
	# 				'lead_owner':lead_owner
	# 				})
	# 				frappe.db.set_value('User Rule', {"parent": lead_rule[0].name,"sales_person":csm_list[counter].sales_person}, 'monthly_status', monthly_status + 1 )	
				
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
	# 				# return sales_person,lead_owner,last_active,monthly_status,overall_limit,later_time,difference
			

	# return 200
			