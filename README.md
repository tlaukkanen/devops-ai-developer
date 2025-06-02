# Description

This is a AI Developer Agent for Azure DevOps. You can tag a work item in Azure DevOps for AI Developer. AI Developer will pickup that work item and implement the required change and create pull request.

If AI Developer needs more information before being able to implement the feature then it will add a new comment on the work item and wait for reply.

# Security Note

The AI Agent is given file system tools to list, read, write files. It also has full shell command tool so that it can run any shell commands on the build agent to compile, test, add packages etc.

...so be aware where you run it.