# Pull Request Review Skill

**Automated PR code review with implementation of improvements and approval.**

This skill conducts comprehensive code review of a pull request, implements recommended improvements, and approves the PR when ready. It does NOT merge the PR - that's handled by `/07-complete-task`.

## Usage

```bash
# Review current branch's PR
/06-pr-review

# Review specific PR
/06-pr-review 42

# Review PR for specific Jira ticket
/06-pr-review SOC-5
```

## What This Skill Does

### Phase 1: Fetch PR Details

1. Identifies PR for current branch (or uses specified PR number) using GitHub MCP
2. Fetches PR details: title, description, status, checks
3. Retrieves diff and files changed using GitHub MCP
4. Gets linked Jira ticket details (if available) using Atlassian MCP

### Phase 2: Automated Code Review

Analyzes code changes comprehensively for:
- **Critical Issues**: Missing dependencies, breaking changes, security concerns
- **Code Quality**: Type safety, error handling, import organization
- **Documentation**: README updates, docstrings, comments
- **Testing**: Test coverage, edge cases, integration tests
- **Architecture**: Type definitions, code organization, patterns

Generates detailed review with categorized recommendations.

### Phase 3: Implement Recommendations

1. Creates todo list from review recommendations
2. Implements each recommendation systematically:
   - Type safety improvements
   - Error handling enhancements
   - Documentation updates
   - Test coverage additions
   - Code organization refactoring
3. Organizes changes into logical commits
4. Pushes commits to PR branch

### Phase 4: Approval & Finalization

1. Adds summary comment to PR with completion status using GitHub MCP
2. Approves PR (if all recommendations implemented) using GitHub MCP
3. **Does NOT merge** - merging happens in `/07-complete-task`
4. Reports PR is ready for final review and merge

## Parameters

| Parameter       | Required | Description                                 | Example           |
| --------------- | -------- | ------------------------------------------- | ----------------- |
| `pr_number`     | No       | PR number (auto-detected if not provided)   | `42`              |
| `jira_key`      | No       | Jira ticket key to provide context          | `SOC-5`           |

## Workflow Steps

### Step 1: Identify PR

```bash
# Check current branch
git branch --show-current

# Find PR for current branch
gh pr list --head current-branch
```

If PR not found:

- Reports error
- Suggests running `/05-create-pr` first

### Step 2: Conduct Code Review

Using GitHub MCP:

- Fetch PR diff and files changed
- Analyze each file for:
  - Missing dependencies
  - Type safety issues
  - Error handling gaps
  - Documentation needs
  - Test coverage
  - Code organization
- Generate categorized recommendations

### Step 3: Implement Recommendations

For each recommendation:

1. Add to todo list
2. Mark as in_progress
3. Implement the change:
   - Edit files
   - Add tests
   - Update documentation
4. Mark as completed
5. Create focused commit

Example implementation order:

1. Type safety (TypedDict, remove casts)
2. Error handling (try/catch, validation)
3. Code organization (imports, structure)
4. Documentation (README, docstrings)
5. Testing (unit tests, integration tests)

### Step 4: Finalize PR

- Push all commits
- Add summary comment to PR using GitHub MCP
- Run checks (if configured) using GitHub MCP
- Approve PR (if all recommendations met) using GitHub MCP
- **Report that PR is ready for merge** (does not merge automatically)

## Review Categories

### Critical Issues (Must Fix)

- Missing required files/dependencies
- Breaking changes
- Security vulnerabilities
- Type errors
- Test failures

### Code Quality (Should Fix)

- Type safety improvements
- Error handling
- Import organization
- Code duplication
- Performance concerns

### Documentation (Should Add)

- README updates for new features
- API documentation
- Usage examples
- Configuration documentation

### Testing (Should Add)

- Unit tests for edge cases
- Integration tests
- Error handling tests
- Mock/fixture improvements

### Architecture (Consider)

- Type definitions (TypedDict, etc.)
- Code organization
- Design patterns
- Separation of concerns

## Output Format

The skill generates a structured review:

```markdown
## PR Review for SOC-X

### Overall Assessment

[Summary of PR quality and readiness]

### Critical Issues (X found)

1. Issue description
   - Impact: [High/Medium/Low]
   - Files: [affected files]
   - Recommendation: [specific fix]

### Code Quality Issues (X found)

[Categorized improvements]

### Documentation Gaps (X found)

[Missing or needed docs]

### Testing Improvements (X found)

[Test coverage needs]

### Recommendations Summary

**Before merging:**

- [ ] MUST: Fix critical issue X
- [ ] SHOULD: Improve Y
- [ ] CONSIDER: Refactor Z

**Estimated effort:** X hours
```

## Implementation Example

### Scenario: Review and Fix PR

```bash
# Start workflow for current branch
/06-pr-review

# Skill fetches PR
Found PR #2 for current branch
Reviewing PR #2: [SOC-4] Implement Platform-Specific Templates

# Skill conducts review
Reviewing code changes...
Found 12 recommendations across 5 categories

# Skill creates todo list
✓ Added 12 todos for implementation

# Skill implements recommendations
[1/12] Adding TypedDict for PLATFORM_SPECS...
✓ Completed

[2/12] Removing cast() calls...
✓ Completed

[3/12] Adding YAML error handling...
✓ Completed

# ... continues through all recommendations

# Skill organizes commits
✓ Created 3 logical commits:
  - Refactor: Type safety improvements
  - Add: Comprehensive test coverage
  - Docs: Update README with new features

# Skill pushes and finalizes
✓ Pushed commits to PR
✓ Added summary comment
✓ All recommendations implemented
✓ PR approved

PR is ready for merge. Run /07-complete-task to merge and close ticket.
```

## Integration with Other Skills

### Works With:

- `/02-start-task` - Creates feature branch that PR will be based on
- `/03-dev-execute` - Implements features that go into the PR
- `/04-reconcile-work` - Validates work before PR creation
- `/05-create-pr` - Creates the PR that this skill reviews
- `/07-complete-task` - Merges the approved PR

### Typical Workflow:

```bash
1. /02-start-task SOC-5              # Start work
2. /03-dev-execute SOC-5             # Implement feature
3. /04-reconcile-work SOC-5          # Validate completeness
4. /05-create-pr SOC-5 "message"     # Commit and create PR
5. /06-pr-review                     # Review, fix, and approve PR ⬅ THIS SKILL
6. /07-complete-task                 # Merge PR and close Jira
```

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- GitHub MCP server configured in `.mcp.json`
- Git repository with remote configured
- PR must already exist (created by `/05-create-pr`)
- Proper branch naming convention (feature/JIRA-KEY-description)

## Configuration

Configure in `.mcp.json`:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_..."
      }
    }
  }
}
```

## Error Handling

The skill handles common errors:

- **No PR exists**: Reports error, suggests running `/05-create-pr`
- **PR already merged**: Informs user, exits gracefully
- **Merge conflicts**: Provides resolution guidance
- **Check failures**: Reports failing checks
- **API rate limits**: Implements exponential backoff
- **Permission errors**: Clear error messages with resolution steps

## Best Practices

### For Best Results:

1. **Run after `/05-create-pr`**: Ensures PR exists
2. **Review suggestions carefully**: Not all recommendations may apply
3. **Keep PRs focused**: Smaller PRs get better reviews
4. **Address critical issues first**: Prioritize security and breaking changes
5. **Update Jira context**: Helps provide better recommendations

### Review Quality Tips:

- Review considers existing codebase patterns
- Balances thoroughness with practicality
- Prioritizes critical issues over style
- Provides specific, actionable recommendations
- Includes code examples where helpful

## What This Skill Does NOT Do

- ❌ Does NOT merge the PR (that's `/07-complete-task`)
- ❌ Does NOT transition Jira to "Done" (that's `/07-complete-task`)
- ❌ Does NOT delete branches (that's `/07-complete-task`)
- ❌ Does NOT create the PR (that's `/05-create-pr`)

## What Happens Next

After this skill completes:

1. ✅ PR has been reviewed comprehensively
2. ✅ Recommendations have been implemented
3. ✅ PR is approved and ready for merge
4. ⏭️ **Next step**: Run `/07-complete-task` to merge PR and mark Jira as "Done"

## Limitations

- Requires GitHub MCP server access
- Only works with GitHub repositories
- Cannot review images or binary files in detail
- Limited to repositories user has write access to
- Review quality depends on code complexity

## Examples

### Example 1: Standard Review

```bash
# After creating PR with /05-create-pr
/06-pr-review

Found PR #2 for current branch
Reviewing PR #2: [SOC-4] Implement Platform-Specific Templates

Analyzing code...
Found 9 recommendations

Implementing recommendations...
✓ 1/9 Type safety improvements
✓ 2/9 Error handling
✓ 3/9 Documentation updates
✓ 4/9 Test coverage
# ... continues ...

✓ All recommendations implemented
✓ 3 commits pushed
✓ PR approved

PR is ready for merge. Run /07-complete-task when ready.
```

### Example 2: Review Specific PR

```bash
# Review a specific PR number
/06-pr-review 45

Reviewing PR #45: [SOC-6] Add Authentication

## Overall Assessment
Good implementation with minor improvements needed.

### Critical Issues (1)
❌ Missing JWT_SECRET environment variable validation
   Files: src/auth/jwt.py
   Fix: Add validation in startup

Implementing fixes...
✓ Fixed critical issue
✓ Added 5 improvements
✓ PR approved

PR is ready for merge.
```

### Example 3: Review with Context

```bash
# Review PR with Jira context
/06-pr-review SOC-6

Found PR #3 for SOC-6
Using Jira context for review...

Reviewing against acceptance criteria:
✓ JWT implementation complete
✓ Refresh token flow working
⚠️ Session management basic

Implementing enhancements...
✓ Improved session management
✓ Added comprehensive tests
✓ PR approved

PR is ready for merge.
```

## Troubleshooting

### Review Doesn't Find Issues

- Ensure PR has actual code changes
- Check file diff is accessible
- Verify GitHub MCP server is running

### Implementation Fails

- Check for merge conflicts
- Ensure working directory is clean
- Verify pre-commit hooks pass

### Cannot Approve PR

- Check user has approval permissions
- Verify not author of PR (can't self-approve in some repos)
- Ensure PR is not in draft state

## Success Criteria

A successful PR review completion includes:

✅ PR fetched and analyzed successfully
✅ Comprehensive review conducted
✅ All critical issues resolved
✅ Code quality improvements implemented
✅ Documentation updated
✅ Test coverage adequate
✅ Clean commit history
✅ PR summary comment added
✅ PR approved (if all checks pass)
✅ Ready for merge in `/07-complete-task`

## Notes

- This skill is designed for **automated review and improvement**
- It complements (doesn't replace) human code review
- Focuses on objective, automatable improvements
- Best used after `/05-create-pr`
- Ensures consistent code quality standards
- Does NOT merge the PR - that's the next step

## Difference from Old `/06-pr-workflow`

### Old Behavior:

```
/06-pr-workflow → Create PR → Review → Merge → Close Jira ✅
```

### New Behavior:

```
/05-create-pr → Create PR, Jira → "In Review" 🔍
/06-pr-review → Review and approve PR 🔧 (THIS SKILL)
/07-complete-task → Merge PR, Jira → "Done" ✅
```

**Key improvement**: Clear separation between PR review and PR merge, following standard code review practices where approval happens before merge.

---

**Built to ensure high-quality PRs with comprehensive automated review and improvement**
