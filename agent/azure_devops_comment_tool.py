import os
import requests
from langchain.tools import BaseTool

class AzureDevOpsCommentTool(BaseTool):
    name = "add_azure_devops_work_item_comment"
    description = (
        "Add a comment to an Azure DevOps work item. "
        "Requires work_item_id (str) and comment (str) as arguments. "
        "Uses org, project, and PAT from environment variables or constructor."
    )

    def __init__(self, org=None, project=None, pat=None):
        super().__init__()
        self.org = org or os.environ.get("AZURE_DEVOPS_ORG")
        self.project = project or os.environ.get("AZURE_DEVOPS_PROJECT")
        self.pat = pat or os.environ.get("AZURE_DEVOPS_PAT")

    def _run(self, work_item_id: str, comment: str):
        if not all([self.org, self.project, self.pat]):
            return "Azure DevOps org, project, or PAT not set."
        url = (
            f"https://dev.azure.com/{self.org}/{self.project}/_apis/wit/workItems/"
            f"{work_item_id}/comments?api-version=7.0-preview.3"
        )
        data = {"text": comment}
        response = requests.post(
            url,
            json=data,
            auth=("", self.pat)
        )
        try:
            response.raise_for_status()
        except Exception as e:
            return f"Failed to add comment: {e}"
        return f"Comment added to work item {work_item_id}."

    def _arun(self, *args, **kwargs):
        raise NotImplementedError("Async not supported.")
