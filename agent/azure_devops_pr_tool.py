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
    work_item_id: int = Field(..., description="The ID of the work item to link to the pull request.")
    auto_complete: Optional[bool] = Field(False, description="Whether to set the pull request to auto-complete.")

def create_azure_devops_pull_request(
    source_branch: str,
    target_branch: str,
    title: str,
    description: Optional[str] = None,
    work_item_id: int,
    auto_complete: Optional[bool] = False,
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
    # Attach work item via separate API call after PR creation, as workItemRefs is not a valid field for PR creation
    try:
        response = requests.post(api_url, json=data, headers=headers, auth=auth, timeout=30)
        response.raise_for_status()
        pr = response.json()
        pr_id = pr.get("pullRequestId")
        pr_url = pr.get("url", "No URL returned")
        pr_web_url = f"https://dev.azure.com/{org}/{project}/_git/{repo_id}/pullrequest/{pr_id}"
        # Attach work item if requested
        if work_item_id and pr_id:
            wi_url = f"https://dev.azure.com/{org}/{project}/_apis/git/repositories/{repo_id}/pullRequests/{pr_id}/workitems/{work_item_id}?api-version=7.2-preview.2"
            try:
                wi_response = requests.put(wi_url, headers=headers, auth=auth, timeout=30)
                wi_response.raise_for_status()
            except Exception as wie:
                return f"Pull request created: {pr_web_url} (work item link failed: {wie})"
        # Set auto-complete if requested
        if auto_complete and pr_id:
            auto_complete_url = f"https://dev.azure.com/{org}/{project}/_apis/git/repositories/{repo_id}/pullRequests/{pr_id}/autoComplete?api-version=7.2-preview.2"
            auto_complete_data = {
                "autoCompleteSetBy": {
                    "id": None  # Let the API use the current user
                }
            }
            try:
                ac_response = requests.patch(auto_complete_url, json=auto_complete_data, headers=headers, auth=auth, timeout=30)
                ac_response.raise_for_status()
                return f"Pull request created and set to auto-complete: {pr_web_url}"
            except Exception as ace:
                return f"Pull request created: {pr_web_url} (auto-complete failed: {ace})"
        return f"Pull request created: {pr_web_url}"
    except Exception as e:
        return f"Failed to create pull request: {e}"

class AzureDevOpsPRTool(StructuredTool):
    """
    StructuredTool for creating a pull request in Azure DevOps.
    """
    def __init__(self, org=None, project=None, repo_id=None, pat=None):
        super().__init__(
            func=lambda source_branch, target_branch, title, description="", work_item_ref=None, auto_complete=False: create_azure_devops_pull_request(
                source_branch, target_branch, title, description, work_item_ref, auto_complete, org=org, project=project, repo_id=repo_id, pat=pat
            ),
            name="create_azure_devops_pull_request",
            description=(
                "Create a pull request in Azure DevOps. "
                "Requires source_branch (str), target_branch (str), title (str), optional description (str), optional work_item_ref (int), and optional auto_complete (bool). "
                "Uses org, project, repo_id, and PAT from environment variables or constructor."
            ),
            args_schema=AzureDevOpsPRInput,
        )
