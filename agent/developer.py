from typing import Optional

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.agent_toolkits import FileManagementToolkit
from langchain_core.runnables import RunnableConfig
from langchain_openai import AzureChatOpenAI

from agent.azure_devops_comment_tool import AzureDevOpsCommentTool
from agent.azure_devops_pr_tool import AzureDevOpsPRTool
from agent.run_shell_command_tool import RunShellCommandTool


class DeveloperAgent:
    def __init__(
        self,
        codebase_path: str = "codebase",
        azure_devops_org: Optional[str] = None,
        azure_devops_project: Optional[str] = None,
        azure_devops_repo_id: Optional[str] = None,
        azure_devops_pat: Optional[str] = None
    ):
        """
        Initializes the DeveloperAgent with a specified codebase path and Azure DevOps PR tool parameters.
        :param codebase_path: Path to the codebase directory.
        :param azure_devops_org: Azure DevOps organization name.
        :param azure_devops_project: Azure DevOps project name.
        :param azure_devops_repo_id: Azure DevOps repository ID.
        :param azure_devops_pat: Azure DevOps Personal Access Token.
        """
        toolkit = FileManagementToolkit(
            root_dir=str(codebase_path)
        )
        # Load tools for file management and shell commands
        file_tools = toolkit.get_tools()
        self.tools = file_tools
        self.tools.append(RunShellCommandTool())
        self.tools.append(AzureDevOpsCommentTool())
        # Add AzureDevOpsPRTool if all required parameters are provided
        if all([azure_devops_org, azure_devops_project, azure_devops_repo_id, azure_devops_pat]):
            self.tools.append(AzureDevOpsPRTool())
        self.system_prompt = "You are a developer agent. Your task is to assist with software development tasks."
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )
        self.llm = AzureChatOpenAI(
            azure_deployment="gpt-4.1",
            api_version="2024-12-01-preview",
            stream_usage=True
        )
        self.agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt,
        )
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=40,
            return_intermediate_steps=True,
            max_execution_time=300,  # Set a maximum execution time of 300 seconds
        )

    def develop_feature(self, specification):
        """
        Develops a feature based on the provided specification.
        :param specification: The feature specification as a string.
        :return: The response from the agent after processing the specification.
        """
        print(f"Agent is developing feature with specification:\n{specification}")
        # Initiating LangChain agent execution...
        config: RunnableConfig = {
            "configurable": {"session_id": "developer_agent"}, 
            "max_concurrency": 1
        }
        result = self.agent_executor.invoke(
            {"input": specification}, config=config)
        
        # Check if token usage is available and print if it exists
        if 'token_usage' in result and result['token_usage']:
            token_usage = result['token_usage']
            print(f"Prompt tokens used    : {token_usage.get('prompt_tokens', 'N/A')}")
            print(f"Completion tokens used: {token_usage.get('completion_tokens', 'N/A')}")
            print(f"Total tokens used     : {token_usage.get('total_tokens', 'N/A')}")
        else:
            print("Token usage information not available in result")
            print(f"Available result keys: {list(result.keys())}")
        
        response = result["output"]
        return response
