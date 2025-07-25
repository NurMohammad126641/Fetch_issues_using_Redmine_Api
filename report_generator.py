import pandas as pd
from credentials import UPDATED_OWNER_MAPPING_WITH_CODES

transactional_keywords = [
    "Cashback Failed", "Mobile recharge failed", "Bank-Money Out (NPSB)",
    "Bank - Money out", "Nagad - Add money", "Nagad - Credit collection",
    "Nagad - Money out", "Rocket - Add money", "Rocket - Money out",
    "Card - Add money", "SQR - Transactional Issues", "VISA Fund Transfer"
]


def load_issues_from_json():
    return pd.read_json("redmine_issues.json", encoding="utf-8")


def prepare_dataframe(df):
    df['created_on'] = pd.to_datetime(df['created_on'])
    df['week_num'] = ((df['created_on'].max() - df['created_on']).dt.days // 7).astype(int)
    df['week_label'] = df['week_num'].apply(lambda x: f"W{str(x).zfill(2)}")

    df = df[df['Assigned to'].str.lower().str.strip() == "tech ops"]

    df['category'] = df['issue_type'].apply(
        lambda x: "Transactional" if any(
            kw.lower() in str(x).lower() for kw in transactional_keywords) else "Non-Transactional"
    )
    return df


def summarize(df):
    if df.empty:
        return pd.DataFrame(columns=['Assigned to', 'issue_type', 'Grand Total'])

    g = df.groupby(['Assigned to', 'issue_type', 'week_label']).size().unstack(fill_value=0)
    g = g.reindex(sorted(g.columns, key=lambda x: int(x[1:])), axis=1)  # Sort week columns
    g['Grand Total'] = g.sum(axis=1)
    g = g.reset_index()
    return g


def generate_custom_table(df, title="Transactional"):
    if df.empty:
        return "<p>No data available.</p>"

    weeks = sorted([col for col in df.columns if col.startswith("W")], key=lambda x: int(x[1:]))

    html = f"""
    <p><strong>{title}:</strong></p>
    <table>
        <thead>
            <tr>
                <th>Category</th><th>Owner</th><th>Issue Type</th>"""
    for week in weeks:
        html += f"<th>{week}</th>"
    html += "<th>Grand Total</th></tr></thead><tbody>"

    total_rows = sum(len(df[df['issue_type'].isin([issue_name for code, issue_name in issues])])
                     for owner, issues in UPDATED_OWNER_MAPPING_WITH_CODES.items())
    first_category_row = True

    for owner, issues in UPDATED_OWNER_MAPPING_WITH_CODES.items():
        issue_names = [issue_name for code, issue_name in issues]
        owner_df = df[df['issue_type'].isin(issue_names)]

        if owner_df.empty:
            continue

        first_owner_row = True

        for idx, row in owner_df.iterrows():
            html += "<tr>"

            # Only once for category
            if first_category_row:
                html += f"<td class='category-cell' rowspan='{total_rows}'>{title}</td>"
                first_category_row = False

            # Only once for owner
            if first_owner_row:
                html += f"<td class='owner-cell' rowspan='{len(owner_df)}'>{owner}</td>"
                first_owner_row = False

            # Issue Type
            if row['Grand Total'] > 50:
                html += f"<td style='color:red'><b>{row['issue_type']}</b></td>"
            else:
                html += f"<td>{row['issue_type']}</td>"

            for week in weeks:
                html += f"<td>{row.get(week, 0)}</td>"

            # Grand Total
            if row['Grand Total'] > 50:
                html += f"<td style='color:red'><b>{row['Grand Total']}</b></td>"
            else:
                html += f"<td>{row['Grand Total']}</td>"

            html += "</tr>"

    # ✅ Grand Total Row
    html += "<tr class='grand-total'>"
    html += "<td colspan='2'><b>Grand Total</b></td><td><b>All Issues</b></td>"
    for week in weeks:
        html += f"<td><b>{df[week].sum()}</b></td>"
    html += f"<td><b>{df['Grand Total'].sum()}</b></td>"
    html += "</tr>"

    html += "</tbody></table><br>"
    return html


def generate_html_report(transactional_table, non_transactional_table, responsible_team_table):
    html = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Calibri, sans-serif;
                font-size: 14px;
                color: #000;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                text-align: center;
                font-size: 14px;
            }}
            th, td {{
                border: 1px solid #555555;
                padding: 5px;
                color: #000; /* Ensuring table text color is black */
            }}
            th {{
                background-color: #dedfe0;
                font-weight: bold;
            }}
            tr:nth-child(even) td {{
                background-color: #fdf8ff;
            }}
            .section-title {{
                font-weight: bold;
                color: #00bfff;
                padding-top: 20px;
                padding-bottom: 10px;
                font-size: 16px;
            }}
            .grand-total {{
                font-weight: bold;
                background-color: #dedfe0;
            }}
            td[colspan], th[colspan] {{
                text-align: center;
            }}
            .category-cell {{
                font-weight: bold;
                background-color: #dedfe0;
                writing-mode: vertical-lr;
                text-align: center;
                vertical-align: middle;
            }}
            .owner-cell {{
                font-style: italic;
                font-weight: bold;
                background-color: #fdf8ff;
                text-align: center;
                vertical-align: middle;
            }}
            td:nth-child(3) {{
                text-align: left;
            }}
        </style>
    </head>
    <body>
        <p>Please see the summary of weekly based pending issues.</p>

        {transactional_table}

        <br><br>

        {non_transactional_table}

        <br><br>

        {responsible_team_table}
    </body>
    </html>
    """
    return html


def create_issue_csv(df, category, filename):
    df = df[df["category"] == category].copy()
    df["Link"] = df["id"].apply(lambda x: f"http://redmine.surecash.net/issues/{x}")
    df.to_csv(filename, columns=["week_label", "Link", "issue_type", "Assigned to", "start_date", "created_on"],
              index=False, encoding="utf-8-sig")
    print(f"✅ CSV saved as {filename}")
    return filename


# ---------------------------responsible_team_issues---------------


def summarize_issue_type_vs_team():
    df = load_issues_from_json()

    if df.empty or not all(col in df.columns for col in ['status', 'issue_type', 'Responsible Team']):
        print("⚠️ Required fields are missing or no data available.")
        return pd.DataFrame(columns=["Issue Type", "Responsible Team", "Count"])

    # ✅ Step 1: Filter for specific statuses
    valid_statuses = {"New", "In Progress", "Open"}
    df = df[df["status"].isin(valid_statuses)]

    # ✅ Step 2: Keep only rows where Responsible Team is not null, not blank, and not 'N/A'
    df = df[
        df["Responsible Team"].notna() &
        (df["Responsible Team"].str.strip() != "") &
        (df["Responsible Team"].str.upper() != "N/A")
    ]

    # ✅ Step 3: Group and summarize
    grouped = (
        df[["issue_type", "Responsible Team"]]
        .groupby(["issue_type", "Responsible Team"])
        .size()
        .reset_index(name="Count")
        .sort_values("Count", ascending=False)
    )

    print("📊 Summary of Issue Type vs Responsible Team (Status: New/In Progress/Open):")
    print(grouped)

    return grouped



def generate_responsible_team_table(df):
    if df.empty:
        return "<p><strong>Responsible Team Summary:</strong> No data available.</p>"

    html = """
    <p><strong>Responsible Team Summary (New / In Progress / Open):</strong></p>
    <table style="border-collapse: collapse; width: 100%; font-size: 13px;">
        <thead>
            <tr style="background-color:#e7e6e6;">
                <th style="border: 1px solid #999; padding: 4px;">Issue Type</th>
                <th style="border: 1px solid #999; padding: 4px;">Responsible Team</th>
                <th style="border: 1px solid #999; padding: 4px;">Total Count</th>
            </tr>
        </thead>
        <tbody>
    """

    for _, row in df.iterrows():
        html += f"""
            <tr>
                <td style="border: 1px solid #999; padding: 4px;">{row['issue_type']}</td>
                <td style="border: 1px solid #999; padding: 4px;">{row['Responsible Team']}</td>
                <td style="border: 1px solid #999; padding: 4px;">{row['Count']}</td>
            </tr>
        """

    grand_total = df["Count"].sum()
    html += f"""
        <tr style="background-color:#e7e6e6; font-weight:bold;">
            <td style="border: 1px solid #999; padding: 4px;">Grand Total</td>
            <td style="border: 1px solid #999; padding: 4px;"></td>
            <td style="border: 1px solid #999; padding: 4px;">{grand_total}</td>
        </tr>
    """

    html += """
        </tbody>
    </table>
    <br>
    """
    return html




def create_responsible_team_csv(df, filename="responsible_team_issues.csv"):
    if df.empty:
        print("⚠️ No responsible team data to save.")
        return None

    # Load full issue list to find IDs
    full_df = load_issues_from_json()

    # Filter for same statuses and valid teams
    valid_statuses = {"New", "In Progress", "Open"}
    full_df = full_df[
        full_df["status"].isin(valid_statuses)
        & full_df["Responsible Team"].notna()
        & (full_df["Responsible Team"].str.strip().str.upper() != "N/A")
        & (full_df["Responsible Team"].str.strip() != "")
    ]

    # Build output rows
    result_df = full_df[["id", "issue_type", "Responsible Team"]].copy()
    result_df["TICKET ID"] = result_df["id"].apply(lambda x: f"https://redmine.surecash.net/issues/{x}")
    result_df.rename(columns={
        "issue_type": "ISSUE_TYPE",
        "Responsible Team": "RESPONSIBLE TEAM"
    }, inplace=True)

    result_df = result_df[["TICKET ID", "ISSUE_TYPE", "RESPONSIBLE TEAM"]]

    # Save to CSV
    result_df.to_csv(filename, index=False, encoding="utf-8-sig")
    print(f"✅ Responsible Team CSV saved as {filename}")
    return filename