# Complete Task Skill

Automates the complete workflow for finishing a development task:

1. Updates the Jira ticket with work summary
2. Transitions the Jira ticket to appropriate status
3. Generates a suitable git commit message
4. Commits the work to Git
5. Pushes to remote

## Usage

```
/05-complete-task <JIRA-KEY> "<summary>"
```

### Examples

```bash
# Basic usage
/05-complete-task SOC-5 "Implemented Streamlit review interface"

# With more detail
/05-complete-task SOC-8 "Added LinkedIn API integration with OAuth2 flow and post scheduling"
```

## What It Does

### 1. Git Status Check

- Runs `git status` to see what files changed
- Runs `git diff` to review the actual changes

### 2. Jira Update

- Fetches the current Jira issue details using the Atlassian MCP Server
- Adds a comprehensive comment with (using the Atlassian MCP Server):
  - Work summary and file changes
  - Scope changes (if any) with rationales
  - Follow-up work identified
  - Known limitations
  - Metrics (LOC, test coverage, architectural decisions)
- Determines the appropriate transition (e.g., "In Progress" → "Done")
- Transitions the ticket accordingly using the Atlassian MCP Server

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

| Argument   | Required | Description                             | Example            |
| ---------- | -------- | --------------------------------------- | ------------------ |
| `jira_key` | Yes      | The Jira issue key (e.g., SOC-5)        | `SOC-5`            |
| `summary`  | Yes      | Brief description of the work completed | `"Implemented UI"` |

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

## Enhanced Jira Comment Format

The skill creates a comprehensive Jira comment with the following sections:

```markdown
## ✅ Completion Summary

[High-level summary of work completed]

### What Was Delivered

- [Key deliverable 1]
- [Key deliverable 2]
- [Key deliverable 3]

### Technical Implementation

[Brief description of approach]

## 📊 Scope Changes

[This section is optional - only included if there were scope changes]

✅ **Within Ticket Scope:**

- Task A: Completed as specified
- Task B: Completed with minor enhancement

⚠️ **Beyond Ticket Scope (Added):**

- Feature X: Brief rationale for addition
- Enhancement Y: Brief rationale for addition

🚫 **Deferred from Ticket:**

- Task Z: Reason for deferral

[If no scope changes]: "No scope changes - implemented exactly as specified in ticket."

## 🔄 Follow-up Work Identified

[Optional - only if follow-up work was discovered]

- [Item 1]: Suggested future ticket
- [Item 2]: Suggested future ticket

## ⚠️ Known Limitations

[Optional - only if there are known limitations]

- [Limitation 1]: Description
- [Limitation 2]: Description

## 📈 Metrics

- Lines of code: +XXX / -YYY
- Test coverage: XX tests, YY% coverage
- Files changed: N files created, M files modified
- Architectural decisions: N documented in code
- [Other relevant metrics]

## Files Changed

- file1.py: [Brief description]
- file2.py: [Brief description]
```

## Notes

- Always review changes with `git status` and `git diff` before running
- The skill adds a co-authored-by line for Claude in commits
- Jira comments include comprehensive completion details for traceability
- Scope changes are highlighted with clear rationales
- The commit message includes a link back to the Jira ticket
- Architectural decisions are counted and referenced
