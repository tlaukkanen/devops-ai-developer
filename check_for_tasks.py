import os
import requests

# Configuration (set these as environment variables in your pipeline)
AZURE_DEVOPS_ORG = os.environ.get("AZURE_DEVOPS_ORG")
AZURE_DEVOPS_PROJECT = os.environ.get("AZURE_DEVOPS_PROJECT")
AZURE_DEVOPS_PAT = os.environ.get("AZURE_DEVOPS_PAT")  # Personal Access Token
AI_DEVELOPER_TAG = "AI Developer"  # Tag used to identify work items for the agent
WORK_ITEM_STATUS = "To Do"  # Status to filter work items

def get_next_work_item():
    url = f"https://dev.azure.com/{AZURE_DEVOPS_ORG}/{AZURE_DEVOPS_PROJECT}/_apis/wit/wiql?api-version=7.0"
    query = {
        "query": f"""
        SELECT [System.Id], [System.Title]
        FROM WorkItems
        WHERE [System.TeamProject] = '{AZURE_DEVOPS_PROJECT}'
          AND [System.Tags] CONTAINS '{AI_DEVELOPER_TAG}'
          AND [System.State] = '{WORK_ITEM_STATUS}'
        ORDER BY [System.CreatedDate] ASC
        """
    }
    response = requests.post(
        url,
        json=query,
        auth=("", AZURE_DEVOPS_PAT)
    )
    response.raise_for_status()
    print("Query executed successfully. Processing results...")
    print(f"Raw JSON response: {response.text}")
    work_items = response.json().get("workItems", [])
    print(f"Found {len(work_items)} new work items.")
    if not work_items:
        print("No new work items found. Setting task ID to 0.")
        return 0  # No new work items
    print(f"Next work item ID: {work_items[0]['id']}")
    
    # Remove the AI_DEVELOPER_TAG from the work item
    work_item_id = work_items[0]["id"]
    update_url = f"https://dev.azure.com/{AZURE_DEVOPS_ORG}/{AZURE_DEVOPS_PROJECT}/_apis/wit/workitems/{work_item_id}?api-version=7.0"
    update_data = [
        {
            "op": "remove",
            "path": "/fields/System.Tags",
            "value": AI_DEVELOPER_TAG
        }
    ]

    response = requests.patch(
        update_url,
        json=update_data,
        auth=("", AZURE_DEVOPS_PAT)
    )
    response.raise_for_status()
    print(f"Removed tag '{AI_DEVELOPER_TAG}' from work item {work_item_id}.")
    return work_items[0]["id"]


def main():
    work_item_id = get_next_work_item()
    with open("task_id.txt", "w") as f:
        f.write(str(work_item_id))


if __name__ == "__main__":
    main()
