# Complete Task Skill

Automates the complete workflow for finishing a development task:
1. Updates the Jira ticket with work summary
2. Transitions the Jira ticket to appropriate status
3. Generates a suitable git commit message
4. Commits the work to Git
5. Pushes to remote

## Usage

```
/complete-task <JIRA-KEY> "<summary>"
```

### Examples

```bash
# Basic usage
/complete-task SOC-5 "Implemented Streamlit review interface"

# With more detail
/complete-task SOC-8 "Added LinkedIn API integration with OAuth2 flow and post scheduling"
```

## What It Does

### 1. Git Status Check
- Runs `git status` to see what files changed
- Runs `git diff` to review the actual changes

### 2. Jira Update
- Fetches the current Jira issue details
- Adds a comment with the work summary and file changes
- Determines the appropriate transition (e.g., "In Progress" → "Done")
- Transitions the ticket accordingly

### 3. Git Commit
- Generates a commit message following the format:
  ```
  [JIRA-KEY] Brief description

  Detailed changes:
  - Change 1
  - Change 2
  - Change 3

  Jira: https://[site].atlassian.net/browse/JIRA-KEY
  ```
- Commits all staged and unstaged changes
- Includes the Jira ticket link in the commit

### 4. Git Push
- Pushes the commit to the remote repository
- Reports the result

## Prerequisites

- Jira MCP server configured in [.mcp.json](../.mcp.json)
- Git repository initialized
- Git remote configured
- Working directory must have changes to commit

## Arguments

| Argument | Required | Description | Example |
|----------|----------|-------------|---------|
| `jira_key` | Yes | The Jira issue key (e.g., SOC-5) | `SOC-5` |
| `summary` | Yes | Brief description of the work completed | `"Implemented UI"` |

## Transition Logic

The skill automatically determines the appropriate Jira transition:
- If ticket is in "To Do" → transitions to "Done"
- If ticket is in "In Progress" → transitions to "Done"
- If ticket is in "Code Review" → transitions to "Done"
- Custom transitions will be detected from available transitions

## Error Handling

The skill will:
- Stop if there are no changes to commit
- Report if Jira ticket doesn't exist
- Report if git push fails
- Provide clear error messages at each step

## Notes

- Always review changes with `git status` and `git diff` before running
- The skill adds a co-authored-by line for Claude in commits
- Jira comments include file change summaries for traceability
- The commit message includes a link back to the Jira ticket
