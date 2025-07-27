# Fetch Issues using Redmine API

This project is a Python-based solution designed to fetch issues from Redmine, process them, generate comprehensive reports in both HTML and CSV formats, and distribute these reports via email. 
It automates the process of extracting critical issue data, summarizing it, and presenting it in an easily digestible format for various stakeholders.


## Features

- **Redmine Issue Fetching**: Connects to the Redmine API to retrieve issues based on configurable parameters.
- **Data Processing**: Transforms raw Redmine issue data into a structured format for analysis.
- **Transactional and Non-Transactional Issue Summaries**: Categorizes and summarizes issues into transactional and non-transactional types.
- **Responsible Team Summary**: Provides a summary of issues resolved by different teams.
- **HTML Report Generation**: Creates visually appealing HTML reports for easy viewing.
- **CSV Export**: Generates CSV files for detailed issue data, suitable for further analysis or record-keeping.
- **Email Distribution**: Automatically sends generated reports and CSV attachments via email.
- **Daily Resolved Issues Report**: Fetches and summarizes issues resolved on the current day, categorized by assignee and tracker.



## Project Structure

The project is organized into several Python modules, each responsible for a specific part of the workflow:

- `main.py`: The main entry point of the application. Orchestrates the fetching, processing, reporting, and emailing of Redmine issues.
- `redmine_service.py`: Handles all interactions with the Redmine API, including fetching issues and custom field options.
- `report_generator.py`: Contains functions for loading and preparing data, summarizing issues, and generating HTML tables and CSV files for various reports.
- `resolved_by_report.py`: Focuses on fetching and summarizing issues resolved on the current day, providing a breakdown by assignee and tracker.
- `credentials.py`: (Not provided in the repository, but inferred) This file is expected to hold sensitive information such as Redmine API keys, URLs, and email credentials. It should be created by the user and **not** committed to version control.
- `redmine_issues.json`: An intermediate file where fetched Redmine issues are stored in JSON format.
- `non_transactional_issues.csv`, `transactional_issues.csv`, `responsible_team_issues.csv`: CSV files generated as part of the reporting process, containing categorized issue data.



## Setup and Installation
To set up and run this project, follow these steps:

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/NurMohammad126641/Fetch_issues_using_Redmine_Api.git
    cd Fetch_issues_using_Redmine_Api
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```
    *(Note: A `requirements.txt` file was not present in the repository, but based on the imports, the following libraries are likely required: `requests`, `pandas`, `urllib3`.)*

4.  **Create `credentials.py`:**

    Create a file named `credentials.py` in the root directory of the project with the following content, replacing the placeholder values with your actual Redmine API key, URL, and email credentials:

    ```python
    # credentials.py

    API_KEY = "YOUR_REDMINE_API_KEY"
    REDMINE_URL = "YOUR_REDMINE_INSTANCE_URL" # e.g., "https://your-redmine.com"
    LIMIT = 100 # Number of issues to fetch per API call
    TOTAL_ISSUES_TO_FETCH = 30000 # Total number of issues to attempt to fetch
    OPTIONS_DICT = {}
    TIMEZONE_OFFSET_HOURS = 6 # Adjust for your timezone offset from UTC

    # Email Configuration
    EMAIL_SENDER = "your_email@example.com"
    EMAIL_PASSWORD = "your_email_password"
    EMAIL_RECEIVERS = ["recipient1@example.com", "recipient2@example.com"]
    EMAIL_SMTP_SERVER = "smtp.example.com"
    EMAIL_SMTP_PORT = 587 # or 465 for SSL
    ```

    **Important:** Do not commit `credentials.py` to your version control system due to sensitive information.


## Usage

To run the application and generate the reports, execute the `main.py` script:

```bash
python main.py
```

The script will perform the following actions:

1.  Fetch issues from your Redmine instance.
2.  Process and summarize transactional, non-transactional, and responsible team issues.
3.  Generate HTML reports and CSV files.
4.  Send the reports and CSV attachments to the configured email recipients.

### Customization

-   **Redmine API Configuration**: Modify `credentials.py` to update your Redmine API key, URL, and fetching limits.
-   **Email Configuration**: Adjust `EMAIL_SENDER`, `EMAIL_PASSWORD`, `EMAIL_RECEIVERS`, `EMAIL_SMTP_SERVER`, and `EMAIL_SMTP_PORT` in `credentials.py` to suit your email setup.
-   **Issue Categorization**: The `report_generator.py` file contains `transactional_keywords` which define how issues are categorized as 'Transactional'. You can modify this list to fit your specific needs.
-   **Responsible Team Mapping**: The `redmine_service.py` uses `get_custom_field_options("Responsible Team")` to load a mapping for responsible teams. Ensure your Redmine instance has a custom field named "Responsible Team" with appropriate values.
-   **Timezone Offset**: Adjust `TIMEZONE_OFFSET_HOURS` in `credentials.py` to correctly filter resolved issues based on your local timezone.




## Output Results

This project generates comprehensive and insightful reports, providing a clear overview of Redmine issues. The output is designed to be both informative and visually accessible, making it easy to track, analyze, and manage issues.

### HTML Report

The primary output is an HTML report that consolidates various summaries into a single, easy-to-read document. This report includes:

-   **Transactional and Non-Transactional Issue Summaries**: These detailed tables break down issues by category (Transactional/Non-Transactional), owner, and issue type, providing a weekly count and a grand total.
      This allows for a granular view of issue distribution and resolution over time.

-   **Responsible Team Summary**: This section offers a high-level overview of issues handled by different responsible teams, categorized by issue type and showing the total count. It helps in understanding team workload and efficiency.

-   **Today's Resolved Issues Summary**: A dynamic summary that highlights issues resolved on the current day, broken down by the assignee and the type of issue (tracker). This provides immediate insights into daily progress and individual contributions.

### CSV Exports

In addition to the HTML report, the project generates several CSV files for more in-depth data analysis and record-keeping:

-   `transactional_issues.csv`: Contains detailed data for all transactional issues.
-   `non_transactional_issues.csv`: Contains detailed data for all non-transactional issues.
-   `responsible_team_issues.csv`: Provides a comprehensive dataset of issues categorized by responsible team.

These CSV files can be easily imported into spreadsheet software or data analysis tools for further manipulation and custom reporting.

Below is a screenshot illustrating the structure and content of the generated HTML report:

<img width="1748" height="849" alt="image" src="https://github.com/user-attachments/assets/7eb0c713-843a-4ba6-bc9c-10a8f536e1c0" />


