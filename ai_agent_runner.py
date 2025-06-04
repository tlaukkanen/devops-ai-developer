import os
import sys
import requests

from agent.developer import DeveloperAgent

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


def implement_task_logic(work_item, codebase_path='codebase'):
    # Placeholder: Implement your AI logic here
    # For now, just print the work item title and ID
    print(f"Implementing work item {work_item['id']}: {work_item['fields'].get('System.Title')}")
    # Example: If more info is needed, add a comment and exit
    # add_comment_to_work_item(work_item['id'], "Need more information to proceed.")
    # sys.exit(0)
    # Otherwise, implement the required change (not implemented here)
    # Accept codebase_path as a parameter (default to "codebase")
    import inspect
    frame = inspect.currentframe()
    args, _, _, values = inspect.getargvalues(frame)
    codebase_path = values.get('codebase_path', 'codebase')
    # Get Azure DevOps repo id from environment variable (must be set in pipeline)
    azure_devops_org = os.environ.get("AZURE_DEVOPS_ORG")
    azure_devops_project = os.environ.get("AZURE_DEVOPS_PROJECT")
    azure_devops_repo_id = os.environ.get("AZURE_DEVOPS_REPO_ID")
    azure_devops_pat = os.environ.get("AZURE_DEVOPS_PAT")
    agent = DeveloperAgent(
        codebase_path=codebase_path,
        azure_devops_org=azure_devops_org,
        azure_devops_project=azure_devops_project,
        azure_devops_repo_id=azure_devops_repo_id,
        azure_devops_pat=azure_devops_pat
    )
    feature_name = work_item['fields'].get('System.Title', 'Unnamed Feature')
    specification = f"""
    Develop the feature: {feature_name}
    
    Azure DevOps Work Item ID: {work_item['id']}
    Description: {work_item['fields'].get('System.Description', 'No description provided.')}
    Tags: {', '.join(work_item['fields'].get('System.Tags', '').split(';')) if 'System.Tags' in work_item['fields'] else 'No tags'}
    Priority: {work_item['fields'].get('Microsoft.VSTS.Common.Priority', 'No priority specified')}
    
    Please implement the feature in the codebase located at {codebase_path}.
    Ensure to follow best practices. Use the shell tool for any necessary shell commands.
    If you install packages, make sure that you don't list files recursively in the codebase.
    
    If you need to ask for more information, please add a comment to the work item.

    When you are done, commit and push your changes and create a pull request for review. Include 
    the work item number in the pull request description with `#` prefix. Add a comment to 
    the work item with the details of the implementation and include the pull request link 
    in the comment. The comments support markdown formatting.
    """
    response = agent.develop_feature(specification)
    #print(f"Agent response: {response}")
    pass

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run the AI Developer Agent on a work item.")
    parser.add_argument("work_item_id", help="Azure DevOps work item ID")
    parser.add_argument("--codebase-path", default="codebase", help="Path to the codebase directory (default: codebase)")
    args = parser.parse_args()

    work_item_id = args.work_item_id
    codebase_path = args.codebase_path

    if work_item_id == "0":
        print("No work item to process.")
        sys.exit(0)
    work_item = get_work_item_details(work_item_id)
    implement_task_logic(work_item, codebase_path=codebase_path)


if __name__ == "__main__":
    main()
