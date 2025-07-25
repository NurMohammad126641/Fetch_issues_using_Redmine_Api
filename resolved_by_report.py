import requests
import time
import json
import urllib3
from datetime import datetime, timedelta
from collections import defaultdict
from credentials import API_KEY, REDMINE_URL, TIMEZONE_OFFSET_HOURS

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PROJECT_ISSUES_URL = f'{REDMINE_URL}'
LIMIT = 100
TOTAL_ISSUES_TO_FETCH = 30000

headers = {
    'X-Redmine-API-Key': API_KEY,
    'Content-Type': 'application/json'
}

local_today_date = (datetime.utcnow() + timedelta(hours=TIMEZONE_OFFSET_HOURS)).date()


def fetch_today_resolved_issues():
    filtered_issues = []
    all_issues = []

    for offset in range(0, TOTAL_ISSUES_TO_FETCH, LIMIT):
        print(f"🔄 Fetching issues {offset} to {offset + LIMIT - 1}")
        params = {
            'include': 'custom_fields',
            'limit': LIMIT,
            'offset': offset
        }

        try:
            response = requests.get(PROJECT_ISSUES_URL, headers=headers, params=params, verify=False)
            response.raise_for_status()
            issues = response.json().get("issues", [])

            if not issues:
                print("🚫 No more issues found.")
                break

            all_issues.extend(issues)
            time.sleep(0.5)

        except requests.exceptions.RequestException as e:
            print(f"❌ Error: {e}")
            break

    print(f"✅ Total issues fetched: {len(all_issues)}")

    for issue in all_issues:
        status = issue.get('status', {}).get('name', '').strip().lower()
        updated_on = issue.get('updated_on', '')

        # print(f"🔍 Checking issue {issue.get('id')} - status: {status}, updated_on: {updated_on}")

        if status == 'resolved' and updated_on:
            try:
                updated_dt_utc = datetime.strptime(updated_on, "%Y-%m-%dT%H:%M:%SZ")
                updated_dt_local = updated_dt_utc + timedelta(hours=TIMEZONE_OFFSET_HOURS)
                updated_date_local = updated_dt_local.date()

                # print(f"🕒 Redmine updated_on: {updated_on}, Local adjusted: {updated_dt_local}, Today: {local_today_date}")

                if updated_date_local == local_today_date:
                    filtered_issues.append(issue)

            except ValueError:
                print(f"⚠️ Date parsing error for issue ID: {issue.get('id')}")

    print(f"✅ Total 'Resolved' today: {len(filtered_issues)}")
    return filtered_issues


def get_issue_resolved_by(issue_id):
    url = f"https://redmine.surecash.net/issues/{issue_id}.json"
    params = {'include': 'journals'}

    try:
        response = requests.get(url, headers=headers, params=params, verify=False)
        response.raise_for_status()
        issue_data = response.json()
        journals = issue_data.get('issue', {}).get('journals', [])

        for journal in reversed(journals):
            for detail in journal.get('details', []):
                if detail.get('name') == 'status_id' and detail.get('new_value'):
                    return journal.get('user', {}).get('name', 'Unknown')

        return "Unknown"

    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching issue {issue_id}: {e}")
        return "Error"


def generate_resolved_by_table():
    today_resolved_issues = fetch_today_resolved_issues()

    final_result = []
    resolved_by_count = defaultdict(int)

    for issue in today_resolved_issues:
        issue_id = issue.get('id')
        subject = issue.get('subject', 'No Subject')
        resolved_by = get_issue_resolved_by(issue_id)

        resolved_by_count[resolved_by] += 1

        final_result.append({
            "issue_id": issue_id,
            "subject": subject,
            "resolved_by": resolved_by
        })

        print(f"✅ Issue {issue_id} resolved by: {resolved_by}")

    table_rows = ""
    total_count = 0

    for user, count in resolved_by_count.items():
        total_count += count
        table_rows += f"""
        <tr>
            <td style='border:1px solid #ccc;padding:2px 4px;font-size:12px'>{user}</td>
            <td style='border:1px solid #ccc;padding:2px 4px;text-align:center;font-size:12px'>{count}</td>
        </tr>
        """

    table_rows += f"""
    <tr style='background-color:#e0ebf5;font-weight:bold'>
        <td style='border:1px solid #ccc;padding:2px 4px;font-size:12px'>Total</td>
        <td style='border:1px solid #ccc;padding:2px 4px;text-align:center;font-size:12px'>{total_count}</td>
    </tr>
    """

    html_table = f"""
    <h3 style='font-size:14px;margin-bottom:5px;'>Resolved Issues Summary by User for {local_today_date}</h3>
    <table style='border-collapse:collapse;width:60%;font-size:12px;'>
        <tr style='background-color:#d9d9d9;font-weight:bold'>
            <th style='border:1px solid #ccc;padding:2px 4px;'>Resolved By</th>
            <th style='border:1px solid #ccc;padding:2px 4px;'>Today Total Resolved Count</th>
        </tr>
        {table_rows}
    </table>
    """
    return html_table
