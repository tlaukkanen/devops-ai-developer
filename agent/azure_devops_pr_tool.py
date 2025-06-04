import os
import requests
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field
from typing import Optional

class AzureDevOpsPRInput(BaseModel):
    source_branch: str = Field(..., description="The name of the source branch (e.g., 'feature-branch').")
    target_branch: str = Field(..., description="The name of the target branch (e.g., 'main').")
    title: str = Field(..., description="The title of the pull request.")
    description: Optional[str] = Field("", description="The description of the pull request.")

def create_azure_devops_pull_request(
    source_branch: str,
    target_branch: str,
    title: str,
    description: Optional[str] = None,
    org: Optional[str] = None,
    project: Optional[str] = None,
    repo_id: Optional[str] = None,
    pat: Optional[str] = None,
) -> str:
    # Take org, project, pat, repo_id from environment 
    # variables if not provided, just like the comment tool
    org = org or os.environ.get("AZURE_DEVOPS_ORG")
    project = project or os.environ.get("AZURE_DEVOPS_PROJECT")
    pat = pat or os.environ.get("AZURE_DEVOPS_PAT")
    repo_id = repo_id or os.environ.get("AZURE_DEVOPS_REPO_ID")
    if not all([org, project, pat, repo_id]):
        return "Azure DevOps org, project, repo_id, or PAT not set."
    api_url = f"https://dev.azure.com/{org}/{project}/_apis/git/repositories/{repo_id}/pullrequests?api-version=7.2-preview.2"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {pat}' if pat else '',
    }
    auth = ("", str(pat) if pat is not None else "")
    data = {
        "sourceRefName": f"refs/heads/{source_branch}",
        "targetRefName": f"refs/heads/{target_branch}",
        "title": title,
        "description": description or "",
    }
    try:
        response = requests.post(api_url, json=data, headers=headers, auth=auth, timeout=30)
        response.raise_for_status()
    except Exception as e:
        return f"Failed to create pull request: {e}"
    return f"Pull request created: {response.json().get('url', 'No URL returned')}"

class AzureDevOpsPRTool(StructuredTool):
    """
    StructuredTool for creating a pull request in Azure DevOps.
    """
    def __init__(self, org=None, project=None, repo_id=None, pat=None):
        super().__init__(
            func=lambda source_branch, target_branch, title, description="": create_azure_devops_pull_request(
                source_branch, target_branch, title, description, org=org, project=project, repo_id=repo_id, pat=pat
            ),
            name="create_azure_devops_pull_request",
            description=(
                "Create a pull request in Azure DevOps. "
                "Requires source_branch (str), target_branch (str), title (str), and optional description (str). "
                "Uses org, project, repo_id, and PAT from environment variables or constructor."
            ),
            args_schema=AzureDevOpsPRInput,
        )
