# Atlassian MCP Connection Details

## Connection Status: ✓ Connected

### Atlassian Account Information
- **Name:** Christian Fitz-Gibbon
- **Email:** christianfitzgibbonpersonal@gmail.com
- **Account ID:** 712020:1f2217b8-346f-417f-bcbf-8a6b8a3d9c29
- **Instance:** [christianfitzgibbonpersonal.atlassian.net](https://christianfitzgibbonpersonal.atlassian.net)
- **Account Status:** Active
- **Locale:** en-GB

### MCP Configuration
The MCP server is configured in [.mcp.json](.mcp.json):
```json
{
  "mcpServers": {
    "Atlassian": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote@latest",
        "https://mcp.atlassian.com/v1/sse"
      ]
    }
  }
}
```

### Permissions
- **Cloud ID:** f697d2b7-9442-444e-b462-e3a9b835734f
- **Scopes:**
  - `read:jira-work`
  - `write:jira-work`

## Project: SOC - Social Media Posts

### Project Details
- **Project Name:** Social Media Posts
- **Project Key:** SOC
- **Project ID:** 10232
- **Project UUID:** 4997d596-0faa-4709-a489-7b02e44a3430
- **Project Type:** Software (Next-gen/Simplified)
- **Visibility:** Public
- **Status:** Active and accessible

### Available Issue Types

1. **Task** (ID: 10300)
   - Description: A small, distinct piece of work
   - Hierarchy Level: 0

2. **Epic** (ID: 10301)
   - Description: A collection of related bugs, stories, and tasks
   - Hierarchy Level: 1

3. **Subtask** (ID: 10302)
   - Description: Subtasks track small pieces of work that are part of a larger task
   - Hierarchy Level: -1

## Usage

The Atlassian MCP provides access to:
- View and search Jira issues
- Create and update issues
- Add comments and worklogs
- Transition issues through workflows
- Access Confluence spaces and pages
- Search across Jira and Confluence using Rovo Search

## Quick Links
- **Project URL:** https://christianfitzgibbonpersonal.atlassian.net/jira/software/projects/SOC
- **API Base:** https://api.atlassian.com/ex/jira/f697d2b7-9442-444e-b462-e3a9b835734f
