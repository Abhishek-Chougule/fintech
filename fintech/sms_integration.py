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

@frappe.whitelist(allow_guest=True)
def send_sms():
    code = 'H6lnqBShv5t'
    phone = "8308204658"
    reset_otp = "1234"
    #msg = 'Your verification code is '+otp+' Team CapitalVia'
    msg = '<%23> Your OTP (One Time Password) is '+reset_otp+'. Kindly do not share it with anyone '+code+' -Team FintastIQ'
    headers={'Accept': "text/plain, text/html, */*"}

    headers={'Accept': "text/plain, text/html, */*"}
    #gateway_url = 'http://smsapp.alertsindia.in/smpp/index.php?&text='+msg+'&to='+str(phone)+'&username=cvgrin&password=rohgad456&from=CAPVIA'
    gateway_url ='https://nimbusit.co.in/api/swsendSingle.asp?username=t1capitalvia&password=italviaCAP@1&sender=FNSTIQ&sendto=+91'+str(phone)+'&entityID=1701158150282015972&templateID=1707163523141616932&message='+msg+''

    try:
        requests.post(gateway_url, headers=headers)

    except:
        return {"success_key":0, "message":"Something is wrong with your mobile number."}
    return {"success_key":1, "message":"Verification code is sent to phone number."}