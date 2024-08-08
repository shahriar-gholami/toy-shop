import requests
import json


def send_domain_warn_msg(phone_number, owner_name):
    url = "https://api2.ippanel.com/api/v1/sms/pattern/normal/send"

    payload = json.dumps({
    "code": "lyp3pvrmj2sw81l",
    "sender": "+983000505",
    "recipient": phone_number,
    "variable": {
        "name": owner_name
    }
    })
    headers = {
    'apikey': 'q41yDW73vhtH5Xr63XYQ39DTo96yavuxGRiA9g4a79A=',
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)



def send_gw_warn_msg(phone_number, owner_name):
    url = "https://api2.ippanel.com/api/v1/sms/pattern/normal/send"

    payload = json.dumps({
    "code": "fsjb9kghsqoilaf",
    "sender": "+983000505",
    "recipient": phone_number,
    "variable": {
        "name": owner_name
    }
    })
    headers = {
    'apikey': 'q41yDW73vhtH5Xr63XYQ39DTo96yavuxGRiA9g4a79A=',
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)

def send_otp_code(phone_number, code):
    url = "https://api2.ippanel.com/api/v1/sms/pattern/normal/send"

    payload = json.dumps({
    "code": "u5ulsafx5ymser2",
    "sender": "+983000505",
    "recipient": phone_number,
    "variable": {
        "verification-code": code

    }
    })
    headers = {
    'apikey': 'q41yDW73vhtH5Xr63XYQ39DTo96yavuxGRiA9g4a79A=',
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)

def diopars_register(name,family,phone,code,email,state,insta,day1,clock1,begin1,day2,clock2,begin2):
    url = "https://api2.ippanel.com/api/v1/sms/pattern/normal/send"
    

    payload = json.dumps({
    "code": "0ff1e8329ekmjdd",
    "sender": "+983000505",
    "recipient": '0'+ phone,
    "variable": {
        "name": f'{name.replace("+", " ")} {family.replace("+", " ")}',
        # "first_day": f'{day1.replace("+", " ")}',
        # "first_clock": f'{clock1.replace("+", " ")}',
        # "first_begin": f'{begin1.replace("+", " ")}',
        # "second_day": f'{day2.replace("+", " ")}',
        # "second_clock": f'{clock2.replace("+", " ")}',
        # "second_begin": f'{begin2.replace("+", " ")}',
    }
    })
    headers = {
    'apikey': 'q41yDW73vhtH5Xr63XYQ39DTo96yavuxGRiA9g4a79A=',
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)

def site_req_inform(phone_number, name):
    url = "https://api2.ippanel.com/api/v1/sms/pattern/normal/send"

    payload = json.dumps({
    "code": "asvyx199bprr92n",
    "sender": "+983000505",
    "recipient": phone_number,
    "variable": {
        "name": name
    }
    })
    headers = {
    'apikey': 'q41yDW73vhtH5Xr63XYQ39DTo96yavuxGRiA9g4a79A=',
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)


    payload = json.dumps({
    "code": "jsnfbvmt5lmn7pz",
    "sender": "+983000505",
    "recipient": '09910412672',
    "variable": {
        "name": name
    }
    })
    headers = {
    'apikey': 'q41yDW73vhtH5Xr63XYQ39DTo96yavuxGRiA9g4a79A=',
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)












