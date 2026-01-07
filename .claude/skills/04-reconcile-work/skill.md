# Reconcile Work Skill

Audits completed work against Jira ticket requirements to verify alignment and completeness. Use this before creating a PR or completing a task to ensure all requirements were met.

## Usage

```
/reconcile-work <JIRA-KEY>
```

### Examples

```bash
# Reconcile before creating PR
/reconcile-work SOC-15

# Audit work on current branch
/reconcile-work SOC-22
```

## What It Does

This skill performs a comprehensive audit of work completed on the current branch against the Jira ticket requirements.

### 1. Fetch Ticket Requirements
- Retrieves Jira ticket with full description
- Extracts all tasks/checkboxes from description
- Lists acceptance criteria
- Identifies key deliverables

### 2. Analyze Git History
- Gets all commits on current branch since divergence
- Analyzes commit messages and changes
- Identifies files created, modified, deleted
- Calculates code metrics (LOC added/removed)

### 3. Compare & Reconcile
Matches ticket requirements against actual work:

**Task Completion:**
- ✅ Tasks completed as specified
- ⚠️ Tasks completed with scope expansion
- ❌ Tasks not completed
- ➕ Work done beyond ticket scope

**Acceptance Criteria:**
- ✅ Criteria met
- ⚠️ Criteria partially met
- ❌ Criteria not met

**Scope Analysis:**
- Features added beyond ticket
- Features deferred from ticket
- Architectural decisions made
- Technical debt introduced or resolved

### 4. Generate Reconciliation Report

Creates detailed report:

```markdown
# Reconciliation Report: [JIRA-KEY]

## Ticket Summary
- **Title**: [Ticket title]
- **Description**: [Brief summary]
- **Status**: [Current Jira status]

## Task Completion Analysis

### ✅ Completed Tasks (X/Y)
1. [Task 1]: Completed as specified
   - Files: file1.py, file2.py
   - Commits: abc123, def456

2. [Task 2]: Completed with enhancements
   - Files: file3.py
   - Commits: ghi789
   - Scope expansion: Added error handling not in ticket

### ❌ Incomplete Tasks (X/Y)
1. [Task 3]: Not started
   - Reason: [Why deferred]
   - Recommendation: Create follow-up ticket

### ➕ Additional Work (Beyond Scope)
1. [Feature X]: Added fallback placeholder system
   - Rationale: Graceful degradation
   - Files: file4.py
   - Impact: Low risk, improves UX

2. [Feature Y]: CLI expanded from basic to full argparse
   - Rationale: Better developer experience
   - Files: file5.py
   - Impact: Minimal, enhances usability

## Acceptance Criteria Analysis

### ✅ Met (X/Y)
1. Can generate content for all 4 platforms: ✅
2. Content respects character limits: ✅

### ⚠️ Partially Met (X/Y)
1. Images generated and saved locally: ⚠️ Fallback to placeholder
   - Note: Real Gemini generation implemented with fallback

### ❌ Not Met (X/Y)
1. [Criterion]: Not implemented
   - Recommendation: Address before merge

## Code Metrics
- **Total commits**: N
- **Files changed**: X created, Y modified, Z deleted
- **Lines of code**: +XXX / -YYY
- **Test coverage**: XX tests (estimated YY% coverage)
- **Architectural decisions**: N documented in code comments

## Divergence Analysis

### Alignment Score: XX%
Calculated as (completed tasks + met criteria) / (total tasks + total criteria)

### Scope Divergence: ±XX%
- Scope additions: XX% beyond ticket
- Scope reductions: XX% deferred

### Risk Assessment
- **Low risk divergence**: Enhancements with clear rationale
- **Medium risk divergence**: Significant scope additions
- **High risk divergence**: Missing critical requirements

## Recommendations

### Before Merging
1. [Action 1]: Address incomplete task X
2. [Action 2]: Document decision for scope addition Y
3. [Action 3]: Update ticket with actual scope

### Follow-up Tickets
1. [Item 1]: Create ticket for deferred work
2. [Item 2]: Create ticket for discovered follow-up

### Documentation
1. [Doc update 1]: Update README with new feature
2. [Doc update 2]: Add architecture decision records

## Summary

✅ **Ready for PR**: [Yes/No/With conditions]

**Rationale**: [Brief explanation of readiness]

**Next Steps**:
1. [Step 1]
2. [Step 2]
```

### 5. Post Report
Options for report output:
- Post as Jira comment
- Save to file (`RECONCILIATION_REPORT.md`)
- Display in terminal
- All of the above

## When to Use This Skill

### Use Before:
- Creating a pull request
- Marking ticket as complete
- Sprint demos or reviews
- Major feature branch merge

### Use After:
- Complex multi-day work
- Work spanning multiple commits
- Work with scope changes
- Work by multiple contributors

### Skip For:
- Simple bug fixes
- Single-commit changes
- Work already reviewed
- Obvious complete implementations

## Prerequisites

- Jira MCP server configured in `.mcp.json`
- Git repository initialized
- Working on a feature branch (not main)
- Jira ticket exists

## Arguments

| Argument | Required | Description | Example |
|----------|----------|-------------|---------|
| `jira_key` | Yes | The Jira issue key to reconcile | `SOC-15` |

## Output Options

Can be specified as optional flags:

```bash
# Post to Jira only
/reconcile-work SOC-15

# Save to file only
/reconcile-work SOC-15 --file

# Display in terminal only
/reconcile-work SOC-15 --terminal

# All outputs
/reconcile-work SOC-15 --all
```

## Benefits

- **Verify completeness** - Ensure no requirements were missed
- **Identify scope creep** - See where work diverged from ticket
- **Audit trail** - Document what was delivered vs requested
- **Risk assessment** - Understand impact of scope changes
- **Follow-up planning** - Identify work for future tickets
- **Sprint retrospective** - Analyze estimation accuracy

## Integration with Workflow

### Recommended Flow:

```
1. /start-task SOC-15
2. Do development work
3. /reconcile-work SOC-15         # Audit before completion
4. Review reconciliation report
5. Address any gaps or issues
6. /complete-task SOC-15 "Done"
```

### Sprint Retrospective:

```
# Reconcile all tickets from sprint
/reconcile-work SOC-12
/reconcile-work SOC-13
/reconcile-work SOC-14

# Analyze patterns:
- Which tickets had scope creep?
- Which had better estimates?
- What caused divergence?
```

## Error Handling

The skill will:
- Report if Jira ticket doesn't exist
- Handle branches without commits gracefully
- Note when ticket has no clear tasks/criteria
- Continue with partial data if some analysis fails
- Provide best-effort report even with incomplete data

## Notes

- This is an optional skill - not required for all tasks
- Most useful for complex or long-running work
- Helps identify patterns in estimation accuracy
- Valuable for sprint retrospectives and planning
- Can be run multiple times during development
- Report is a snapshot - rerun after additional commits
- Particularly useful for team leads and project managers

## Example Scenarios

### Scenario 1: Perfect Alignment
```
Alignment Score: 100%
All tasks completed as specified
All acceptance criteria met
No scope divergence
✅ Ready for PR
```

### Scenario 2: Scope Expansion
```
Alignment Score: 90%
All tasks completed
Acceptance criteria met
+20% scope additions (CLI enhancements)
⚠️ Ready for PR with documentation
Action: Document scope additions in ticket
```

### Scenario 3: Incomplete Work
```
Alignment Score: 75%
7/10 tasks completed
3 tasks deferred
Acceptance criteria mostly met
❌ Not ready for PR
Action: Complete remaining tasks or split ticket
```

## Advanced Usage

### Compare Multiple Branches
```bash
# Switch branches and reconcile each
git checkout feature-a
/reconcile-work SOC-10

git checkout feature-b
/reconcile-work SOC-11

# Compare alignment scores
```

### Historical Analysis
```bash
# Reconcile closed tickets for retrospective
/reconcile-work SOC-5  # Closed last sprint
/reconcile-work SOC-8  # Closed last sprint

# Identify estimation patterns
```
