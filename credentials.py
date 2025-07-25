import requests

# Email credentials
EMAIL_ADDRESS = ''
EMAIL_PASSWORD = ""
TO_EMAIL = "mohammad.rabbi@tallykhata.com"

# ✅ CC list - multiple people can be included here
EMAIL_CC_LIST = [
    "mohammad.rabbi@tallykhata.com",
    # "product_eng@tallykhata.com"
]

# Redmine API
API_KEY = " "
REDMINE_URL = 'https://redmine.surecash.net/projects/09/issues.json'
TIMEZONE_OFFSET_HOURS = 1


# Redmine fetching limits
LIMIT = int(100)
TOTAL_ISSUES_TO_FETCH = int(50000)

# Issue type mapping
# OPTIONS_DICT= {
#     70: "Account blocked", 71: "Account suspend", 72: "Add money processing failed", 73: "Amount not found TP balance",
#     74: "Bank - Money out", 75: "Campaign/promotion", 76: "Card - Add money", 77: "Cashback Failed",
#     78: "Customer list not found", 79: "Data mismatch - TP", 80: "Data mismatch - TK", 81: "Data not found - TP",
#     115: "Data not found - TK", 82: "FO issues", 83: "GP MB pack not working", 84: "Incomplete call",
#     117: "Inquiries", 85: "Lenden edit is not working", 86: "Loan issue", 116: "Login problem - TP",
#     87: "Login problem -TK", 88: "Mobile recharge failed", 89: "Nagad - Add money", 90: "Nagad - Credit collection",
#     91: "Nagad - Money out", 92: "NID issue", 93: "NID photo problem", 94: "Offer recharge failed",
#     95: "Other", 96: "OTP issue", 97: "Payment not received from city touch", 98: "Pin reset problem",
#     99: "Registration problem - TP", 100: "Registration problem -TK", 101: "Reverse issue",
#     102: "Rocket - Add money", 103: "Rocket - Credit collection", 104: "Rocket - Money out",
#     105: "Send money - Binimoy (IDTP)", 106: "SMS issue", 107: "SQR - inquiries", 108: "SQR - transactional issues",
#     118: "SQR - non transactional issues", 109: "Statement not match", 110: "Suggestion",
#     111: "Transaction edit/delete related issue", 112: "Transaction mismatch", 113: "Transaction time mismatch",
#     114: "Wallet tab not working", 119: "Bug", 120: "SQR OTP Issue", 121: "VISA Fund Transfer",
#     122: "Bank-Money Out (NPSB)", 123: "TK_Premium-Purchase Package", 124: "TK_Premium-Stock",
#     125: "TK_Premium-Bulk Tagada SMS", 126: "TK_Premium-Business Type Change Problem",
#     286: "DPS Withdrawal Problem", 287: "DPS Transactional / Charge Problem",
#     288: "DPS Enquiry", 289: "Mobile Recharge Enquiry", 328: "Data Backup Problem"
# }

def fetch_issue_type_mapping(api_key= API_KEY):
    url = "https://redmine.surecash.net/custom_fields.json"
    headers = {'X-Redmine-API-Key': api_key}

    response = requests.get(url, headers=headers, verify=False)

    if response.status_code == 200:
        data = response.json()

        # Find the custom field named "Issue Type"
        issue_type_field = next((field for field in data["custom_fields"] if field["name"] == "Issue Type"), None)

        if issue_type_field and "possible_values" in issue_type_field:
            values_dict = {int(item["value"]): item["label"].strip() for item in issue_type_field["possible_values"]}
            return values_dict
        else:
            print("Issue Type field not found or missing possible values.")
            return {}
    else:
        print(f"Failed to fetch issue type mapping: {response.status_code} {response.text}")
        return {}


OPTIONS_DICT = fetch_issue_type_mapping()

UPDATED_OWNER_MAPPING_WITH_CODES = {
    "Nur": [
        (70, "Account blocked"), (71, "Account suspend"), (72, "Add money processing failed"),
        (73, "Amount not found TP balance"), (76, "Card - Add money"), (78, "Customer list not found"),
        (79, "Data mismatch - TP"), (80, "Data mismatch - TK"), (82, "FO issues"),
        (83, "GP MB pack not working"), (84, "Incomplete call"), (86, "Loan issue"),
        (92, "NID issue"), (93, "NID photo problem"), (96, "OTP issue"),
        (97, "Payment not received from city touch"), (101, "Reverse issue"),
        (107, "SQR - inquiries"), (108, "SQR - transactional issues"),
        (109, "Statement not match"), (110, "Suggestion"),
        (111, "Transaction edit/delete related issue"), (112, "Transaction mismatch"),
        (113, "Transaction time mismatch"), (117, "Inquiries"),
        (118, "SQR - non transactional issues"), (120, "SQR OTP Issue"),
        (122, "Bank-Money Out (NPSB)"), (126, "TK_Premium-Business Type Change Problem"),
        (289, "Mobile Recharge Enquiry"), (77, "Cashback Failed")
    ],
    "Javeed": [
        (87, "Login problem -TK"), (116, "Login problem - TP"), (119, "Bug"),
        (123, "TK_Premium-Purchase Package"), (124, "TK_Premium-Stock"),
        (125, "TK_Premium-Bulk Tagada SMS")
    ],
    "Shafiul": [
        (74, "Bank - Money out"), (85, "Lenden edit is not working"),
        (94, "Offer recharge failed"), (95, "Other"), (97, "Payment not received from city touch"),
        (102, "Rocket - Add money"), (103, "Rocket - Credit collection"),
        (104, "Rocket - Money out"), (105, "Send money - Binimoy (IDTP)"),
        (106, "SMS issue"), (114, "Wallet tab not working"), (121, "VISA Fund Transfer"),
        (81, "Data not found - TP"), (115, "Data not found - TK"),
        (98, "Pin reset problem"), (99, "Registration problem - TP"),
        (100, "Registration problem -TK"), (89, "Nagad - Add money"),
        (286, "DPS Withdrawal Problem"), (287, "DPS Transactional / Charge Problem"),
        (288, "DPS Enquiry"), (90, "Nagad - Credit collection"), (91, "Nagad - Money out")
    ],
    "Tamjid": [
        (88, "Mobile recharge failed"), (94, "Offer recharge failed"), (328, "Data Backup Problem"),
        (75, "Campaign/promotion")
    ],
    "Unassigned": []
}

# Fill in Unassigned
assigned_codes = set()
for entries in UPDATED_OWNER_MAPPING_WITH_CODES.values():
    for code, _ in entries:
        assigned_codes.add(code)

for code, desc in OPTIONS_DICT.items():
    if code not in assigned_codes:
        UPDATED_OWNER_MAPPING_WITH_CODES["Unassigned"].append((code, desc))



