import getpass
import requests
import json

requests.packages.urllib3.disable_warnings()

print("**************** FETCH SAFE ACCOUNTS ON CYBERARK ****************")

CYBERARK_LOGIN_URL = ""

def loginRequest(login_url,credentials):
    try:
        response = requests.post(login_url,data=credentials, verify=False)
        return response
    except requests.exceptions.RequestException as err:
        print ("Request Error",err)
def validateOtp(login_url, credentials,first_response):
    first_response_json = first_response.json()

    if first_response_json.get("ErrorCode") == "ITATS542I":
        otp = input("Please enter OTP Code:")
        credentials["password"] = otp
        try:
            response = requests.post(login_url,data=credentials, verify=False, cookies=first_response.cookies)
            return response
        except requests.exceptions.RequestException as err:
            print ("Request Error",err)
    else:
        print("Wrong Credentials")
def getSafeAccounts(cookies):
  safes = ["EXAMPLE_SAFE_A","EXAMPLE_SAFE_B","EXAMPLE_SAFE_C"]
  try:
        all_results = []
        for safe in safes:
            offset = 0
            limit = 1000
            while True:
                params = {
                    "offset": offset,
                    "limit": limit
                    }
                print(f"FETCHING {safe}")
                get_vaults = requests.get(f"https://YOUR_CYBERARK_URL/PasswordVault/api/Accounts?filter=safeName%20eq%20{safe}",cookies=cookies, verify=False, params = params)
                if get_vaults.status_code != 200:
                    if get_vaults.json().get("ErrorCode") == "CAWS00001E":
                        print("Wrong Offset")
                        break
                    else:
                        print("Unexpected Error")
                        break
                accounts = get_vaults.json()
                all_results.append(accounts)  
                offset += limit
        with open("cyberark_pas_accounts.json", "w") as json_file:
            json.dump(all_results, json_file)
            print("Safe Accounts Saved as 'cyberark_pas_accounts.json' Successfully ")
  except requests.exceptions.RequestException as err:
           print ("Cannot Get",err)

if __name__ == '__main__':
    
    username = input("Please enter your Username on PAS: ")
    password =  getpass.getpass()

    login_data = {
    'username' : username,
    'password': password,
    'concurrentSession': 'true'
   }
    
    #FETCH SERVERS ON CYBERARK PAS SAFES
    first_response = loginRequest(CYBERARK_LOGIN_URL,login_data)
    second_response = validateOtp(CYBERARK_LOGIN_URL,login_data,first_response)
    session_cookies = requests.cookies.merge_cookies(first_response.cookies, second_response.cookies)
    getSafeAccounts(session_cookies)
