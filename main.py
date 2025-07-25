from redmine_service import fetch_issues_from_redmine
from report_generator import (
    load_issues_from_json, prepare_dataframe,
    summarize, generate_custom_table,
    generate_html_report, create_issue_csv,
    summarize_issue_type_vs_team, generate_responsible_team_table, create_responsible_team_csv  # ✅ newly added
)
from email_sender import send_email
from resolved_by_report import generate_resolved_by_table  # ✅ existing

def main():
    # Step 1: Fetch issues from Redmine and load
    fetch_issues_from_redmine()
    df = load_issues_from_json()
    df = prepare_dataframe(df)

    # Step 2: Summarize Transactional and Non-Transactional issues
    trx_summary = summarize(df[df["category"] == "Transactional"])
    non_trx_summary = summarize(df[df["category"] == "Non-Transactional"])

    # Step 3: Generate styled HTML tables
    html_trx = generate_custom_table(trx_summary, "Transactional")
    html_non_trx = generate_custom_table(non_trx_summary, "Non-Transactional")
    resolved_by_html = generate_resolved_by_table()

    # Step 4: Generate responsible team summary table
    responsible_team_df = summarize_issue_type_vs_team()
    responsible_team_html = generate_responsible_team_table(responsible_team_df)
    responsible_team_csv = create_responsible_team_csv(responsible_team_df)

    # Step 5: Combine all HTML parts into one email body
    html_content = generate_html_report(html_trx, html_non_trx, responsible_team_html)
    html_content += f"<br><br>{resolved_by_html}"

    # Step 6: Create CSV files for attachments
    trx_csv = create_issue_csv(df, "Transactional", "transactional_issues.csv")
    non_trx_csv = create_issue_csv(df, "Non-Transactional", "non_transactional_issues.csv")

    # Step 7: Send the email with report and attachments
    send_email(html_content, [trx_csv, non_trx_csv, responsible_team_csv])


if __name__ == "__main__":
    main()
