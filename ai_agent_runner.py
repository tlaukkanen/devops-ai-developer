import os
import sys
import requests

# Configuration (set these as environment variables in your pipeline)
AZURE_DEVOPS_ORG = os.environ.get("AZURE_DEVOPS_ORG")
AZURE_DEVOPS_PROJECT = os.environ.get("AZURE_DEVOPS_PROJECT")
AZURE_DEVOPS_PAT = os.environ.get("AZURE_DEVOPS_PAT")  # Personal Access Token
AI_DEVELOPER_TAG = "AI Developer"  # Tag used to identify work items for the agent


def get_work_item_details(work_item_id):
    url = f"https://dev.azure.com/{AZURE_DEVOPS_ORG}/{AZURE_DEVOPS_PROJECT}/_apis/wit/workitems/{work_item_id}?api-version=7.0"
    response = requests.get(
        url,
        auth=("", AZURE_DEVOPS_PAT)
    )
    response.raise_for_status()
    return response.json()


def add_comment_to_work_item(work_item_id, comment):
    url = f"https://dev.azure.com/{AZURE_DEVOPS_ORG}/{AZURE_DEVOPS_PROJECT}/_apis/wit/workItems/{work_item_id}/comments?api-version=7.0-preview.3"
    data = {"text": comment}
    response = requests.post(
        url,
        json=data,
        auth=("", AZURE_DEVOPS_PAT)
    )
    response.raise_for_status()
    return response.json()


def implement_task_logic(work_item):
    # Placeholder: Implement your AI logic here
    # For now, just print the work item title and ID
    print(f"Implementing work item {work_item['id']}: {work_item['fields'].get('System.Title')}")
    # Example: If more info is needed, add a comment and exit
    # add_comment_to_work_item(work_item['id'], "Need more information to proceed.")
    # sys.exit(0)
    # Otherwise, implement the required change (not implemented here)
    pass

def main():
    if len(sys.argv) < 2:
        print("Usage: python ai_agent_runner.py <work_item_id>")
        sys.exit(1)
    work_item_id = sys.argv[1]
    if work_item_id == "0":
        print("No work item to process.")
        sys.exit(0)
    work_item = get_work_item_details(work_item_id)
    implement_task_logic(work_item)


if __name__ == "__main__":
    main()
