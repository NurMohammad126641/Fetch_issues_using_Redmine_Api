import requests
import time
import json
import urllib3
from credentials import API_KEY, REDMINE_URL, LIMIT, TOTAL_ISSUES_TO_FETCH, OPTIONS_DICT

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_custom_field_options(field_name="Responsible Team"):
    url = "https://redmine.surecash.net/custom_fields.json"
    headers = {'X-Redmine-API-Key': API_KEY}

    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        fields = response.json().get("custom_fields", [])

        for field in fields:
            if field.get("name") == field_name and "possible_values" in field:
                try:
                    return {
                        str(item["value"]): item.get("label", item["value"]).strip()
                        for item in field["possible_values"]
                    }
                except Exception as e:
                    print(f"❌ Error parsing mapping for '{field_name}': {e}")
        print(f"⚠️ Field '{field_name}' not found or missing values.")

    except requests.RequestException as e:
        print(f"❌ Failed to fetch custom field options: {e}")

    return {}


def fetch_issues_from_redmine():
    print("🔑 API Key:", API_KEY)
    headers = {'X-Redmine-API-Key': API_KEY}
    all_issues = []

    # 🔁 Load mapping for Responsible Team
    RESPONSIBLE_TEAM_DICT = get_custom_field_options("Responsible Team")
    print("📘 Loaded Responsible Team mapping:", RESPONSIBLE_TEAM_DICT)

    for offset in range(0, TOTAL_ISSUES_TO_FETCH, LIMIT):
        print(f"🔄 Fetching issues {offset} to {offset + LIMIT - 1}")
        params = {'include': 'custom_fields', 'limit': LIMIT, 'offset': offset}

        try:
            response = requests.get(REDMINE_URL, headers=headers, params=params, verify=False)
            response.raise_for_status()
            issues = response.json().get("issues", [])

            if not issues:
                print("❌ No more issues found.")
                break

            for issue in issues:
                issue_id = issue.get("id")
                status = issue.get("status", {}).get("name")
                start_date = issue.get("start_date")
                created_on = issue.get("created_on")
                assigned_to = issue.get("assigned_to", {}).get("name")
                custom_fields = issue.get("custom_fields", [])

                # Issue Type mapping
                issue_type_raw = next(
                    (f.get("value") for f in custom_fields if f.get("name") == "Issue Type"), None
                )
                issue_type = (
                    OPTIONS_DICT.get(int(issue_type_raw), issue_type_raw)
                    if issue_type_raw and issue_type_raw.isdigit()
                    else issue_type_raw
                )

                # Responsible Team mapping
                responsible_team_raw = next(
                    (f.get("value") for f in custom_fields if f.get("name") == "Responsible Team"), None
                )
                responsible_team = RESPONSIBLE_TEAM_DICT.get(str(responsible_team_raw), responsible_team_raw)

                all_issues.append({
                    "id": issue_id,
                    "status": status,
                    "issue_type": issue_type,
                    "start_date": start_date,
                    "created_on": created_on,
                    "Assigned to": assigned_to or "N/A",
                    "Responsible Team": responsible_team or "N/A"
                })

            time.sleep(0.3)

        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            break

    with open("redmine_issues.json", "w", encoding='utf-8') as f:
        json.dump(all_issues, f, ensure_ascii=False, indent=4)
        print("✅ Issues saved to redmine_issues.json")

    return all_issues
