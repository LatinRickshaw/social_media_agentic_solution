# Start Task Skill

Automates the workflow for beginning a development task:
1. Checks git status to ensure working directory is clean
2. Pulls latest changes from remote (if needed)
3. Fetches the Jira ticket details
4. Transitions the Jira ticket to "In Progress"
5. Adds a comment to the Jira ticket indicating work has started

## Usage

```
/start-task <JIRA-KEY>
```

### Examples

```bash
# Basic usage
/start-task SOC-5

# Start work on a specific ticket
/start-task SOC-12
```

## What It Does

### 1. Git Status Check
- Runs `git status` to verify working directory is clean
- If there are uncommitted changes, warns the user and stops
- Ensures you're starting from a clean slate

### 2. Sync with Remote (Optional)
- Checks if current branch is behind remote
- If behind, prompts to pull latest changes
- Helps avoid merge conflicts later

### 3. Fetch Jira Ticket
- Retrieves the Jira issue details
- Displays the ticket summary and current status
- Confirms the ticket exists before proceeding

### 4. Transition to In Progress
- Fetches available transitions for the ticket
- Looks for "In Progress" transition
- Transitions the ticket from current status (e.g., "To Do") to "In Progress"
- Handles custom workflow transitions automatically

### 5. Add Jira Comment
- Adds a comment to the Jira ticket: "Started work on this task"
- Provides traceability of when work began
- Visible to the team in Jira

## Prerequisites

- Jira MCP server configured in `.mcp.json`
- Git repository initialized
- Git remote configured (optional, for sync check)
- Working directory should be clean (no uncommitted changes)

## Arguments

| Argument | Required | Description | Example |
|----------|----------|-------------|---------|
| `jira_key` | Yes | The Jira issue key to start working on | `SOC-5` |

## Transition Logic

The skill automatically determines the appropriate Jira transition:
- Looks for transition named "In Progress" (case-insensitive)
- If not found, looks for similar transitions (e.g., "Start Progress", "Begin")
- Reports an error if no suitable transition is found
- Shows current status and available transitions for debugging

## Error Handling

The skill will:
- Stop if working directory has uncommitted changes
- Report if Jira ticket doesn't exist
- Report if "In Progress" transition is not available
- Provide clear error messages at each step
- Suggest running `/complete-task` to commit pending work if needed

## Notes

- Always commit or stash pending work before starting a new task
- Use `git status` to check your working directory before running
- The skill ensures you don't accidentally mix work from multiple tickets
- Pairs well with `/complete-task` for a complete workflow
- Jira comments provide audit trail of when work started

## Workflow Integration

Typical workflow:
1. `/start-task SOC-5` - Begin work on ticket SOC-5
2. Make your code changes
3. `/complete-task SOC-5 "Implemented feature X"` - Finish and commit

This ensures clean separation between tasks and proper Jira tracking.
