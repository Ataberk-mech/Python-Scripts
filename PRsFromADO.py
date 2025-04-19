
import http.client
import json
import csv
import base64
from datetime import datetime

# Azure DevOps Credentials
organization = "org"
project = "pro"
repository_id = "rep"

# Personal Access Token (PAT)
personal_access_token = "patkey"

# Encryption of PAT for Basic Auth
auth_token = base64.b64encode(f":{personal_access_token}".encode("utf-8")).decode("utf-8")

# Dynamic CSV file name based on current date and time
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
csv_file_name = f"pull_requests_{current_time}.csv"

# Getting pull requests from Azure DevOps
def fetch_pull_requests(status):
    # Create the endpoint URL
    api_version = "6.0"
    endpoint = f"/{organization}/{project}/_apis/git/repositories/{repository_id}/pullrequests?status={status}&api-version={api_version}"

    # HTTP Connection
    conn = http.client.HTTPSConnection("dev.azure.com")
    headers = {
        "Authorization": f"Basic {auth_token}",
        "Content-Type": "application/json"
    }

    # Sending GET request to the API
    conn.request("GET", endpoint, headers=headers)
    response = conn.getresponse()
    
    if response.status == 200:
        data = response.read()
        conn.close()
        return json.loads(data).get("value", [])
    else:
        print(f"Error: {response.status}, Message: {response.read().decode()}")
        conn.close()
        return []

# Getting completed and active pull requests
completed_prs = fetch_pull_requests("completed")
active_prs = fetch_pull_requests("active")
all_prs = completed_prs + active_prs

# Sorting pull requests by ID
all_prs_sorted = sorted(all_prs, key=lambda pr: pr["pullRequestId"])

# Creating CSV file and writing data
with open(csv_file_name, "w", newline="", encoding="utf-8") as csv_file:
    csv_writer = csv.writer(csv_file)
    
    # Writing CSV header
    headers = ["Pull Request ID", "Header", "State", "Creation Date", "User"]
    csv_writer.writerow(headers)
    
    # Writing pull request data in CSV File
    for pr in all_prs_sorted:
        pr_id = pr["pullRequestId"]
        title = pr["title"]
        status = pr["status"]
        creation_date = pr["creationDate"]  # Datetime format
        created_by = pr["createdBy"]["displayName"]  # Creator's name
        csv_writer.writerow([pr_id, title, status, creation_date, created_by])

print(f"Pull request data saved '{csv_file_name}' file succesfully.")

