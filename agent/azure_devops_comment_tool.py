
import os
import requests
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

class AzureDevOpsCommentInput(BaseModel):
    work_item_id: str = Field(..., description="The ID of the Azure DevOps work item.")
    comment: str = Field(..., description="The comment text to add to the work item.")

def add_azure_devops_work_item_comment(
    work_item_id: str,
    comment: str,
    org: str | None = None,
    project: str | None = None,
    pat: str | None = None,
) -> str:
    org = org or os.environ.get("AZURE_DEVOPS_ORG")
    project = project or os.environ.get("AZURE_DEVOPS_PROJECT")
    pat = pat or os.environ.get("AZURE_DEVOPS_PAT")
    if not all([org, project, pat]):
        return "Azure DevOps org, project, or PAT not set."
    url = (
        f"https://dev.azure.com/{org}/{project}/_apis/wit/workItems/"
        f"{work_item_id}/comments?api-version=7.0-preview.3"
    )
    data = {"text": comment}
    response = requests.post(
        url,
        json=data,
        auth=("", str(pat) if pat is not None else "")
    )
    try:
        response.raise_for_status()
    except Exception as e:
        return f"Failed to add comment: {e}"
    return f"Comment added to work item {work_item_id}."

class AzureDevOpsCommentTool(StructuredTool):
    name = "add_azure_devops_work_item_comment"
    description = (
        "Add a comment to an Azure DevOps work item. "
        "Requires work_item_id (str) and comment (str) as arguments. "
        "Uses org, project, and PAT from environment variables or constructor."
    )
    args_schema = AzureDevOpsCommentInput

    def __init__(self, org=None, project=None, pat=None):
        super().__init__(
            func=lambda work_item_id, comment: add_azure_devops_work_item_comment(
                work_item_id, comment, org=org, project=project, pat=pat
            ),
            name=self.name,
            description=self.description,
            args_schema=self.args_schema,
        )
