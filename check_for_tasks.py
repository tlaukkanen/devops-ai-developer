import os
import requests

# Configuration (set these as environment variables in your pipeline)
AZURE_DEVOPS_ORG = os.environ.get("AZURE_DEVOPS_ORG")
AZURE_DEVOPS_PROJECT = os.environ.get("AZURE_DEVOPS_PROJECT")
AZURE_DEVOPS_PAT = os.environ.get("AZURE_DEVOPS_PAT")  # Personal Access Token
AI_DEVELOPER_TAG = "AI Developer"  # Tag used to identify work items for the agent


def get_next_work_item():
    url = f"https://dev.azure.com/{AZURE_DEVOPS_ORG}/{AZURE_DEVOPS_PROJECT}/_apis/wit/wiql?api-version=7.0"
    query = {
        "query": f"""
        SELECT [System.Id], [System.Title]
        FROM WorkItems
        WHERE [System.TeamProject] = '{AZURE_DEVOPS_PROJECT}'
          AND [System.Tags] CONTAINS '{AI_DEVELOPER_TAG}'
          AND [System.State] = 'New'
        ORDER BY [System.CreatedDate] ASC
        """
    }
    response = requests.post(
        url,
        json=query,
        auth=("", AZURE_DEVOPS_PAT)
    )
    response.raise_for_status()
    work_items = response.json().get("workItems", [])
    if not work_items:
        return 0  # No new work items
    return work_items[0]["id"]


def main():
    work_item_id = get_next_work_item()
    with open("task_id.txt", "w") as f:
        f.write(str(work_item_id))


if __name__ == "__main__":
    main()
