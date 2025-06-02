from langchain_openai import AzureChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.pydantic_v1 import BaseModel, Field
from langchain_community.agent_toolkits.load_tools import load_tools

from langchain_community.agent_toolkits import FileManagementToolkit
from agent.azure_devops_comment_tool import AzureDevOpsCommentTool
from agent.run_shell_command_tool import RunShellCommandTool

class DeveloperAgent:
    def __init__(self, codebase_path: str = "codebase"):
        """
        Initializes the DeveloperAgent with a specified codebase path.
        :param codebase_path: Path to the codebase directory.
        """
        toolkit = FileManagementToolkit(
            root_dir=str(codebase_path)
        )
        # Load tools for file management and shell commands
        file_tools = toolkit.get_tools()
        self.tools = file_tools
        self.tools.append(RunShellCommandTool())
        self.tools.append(AzureDevOpsCommentTool())
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
            api_version="2024-12-01-preview"
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
        )

    def develop_feature(self, specification):
        print(f"Agent is developing feature with specification:\n{specification}")
        # Initiating LangChain agent execution...
        config = {"configurable": {"session_id": "developer_agent"}, "max_concurrency": 1}
        result = self.agent_executor.invoke(
            {"input": specification}, config=config)
        response = result["output"]
        return response
        return response
