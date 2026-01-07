# Development Execution Skill

Guides the development of software features following engineering best practices including SOLID principles, KISS, DRY, and more. This skill ensures code is built correctly from the start, not fixed after the fact.

## Usage

```
/dev-execute "<task_description>" [jira_key]
```

### Examples

```bash
# Execute a feature development
/dev-execute "Add user authentication with JWT tokens" SOC-15

# Execute a bug fix
/dev-execute "Fix race condition in post generation" SOC-22

# Execute a refactoring
/dev-execute "Extract email service from UserManager class"

# Execute with more context
/dev-execute "Implement LinkedIn API integration with OAuth2 flow and post scheduling" SOC-8
```

## What It Does

This skill guides you through disciplined software development by:

### Phase 1: Understanding & Planning (BEFORE any code)

**1.1 Requirement Analysis**
- What is the actual problem to solve?
- What are the acceptance criteria?
- What are the edge cases?
- What should NOT be built (YAGNI)?

**1.2 Architecture Review**
- Read relevant existing code to understand patterns
- Identify where new code fits in the architecture
- Determine which existing abstractions to use
- Plan how to maintain separation of concerns

**1.3 Design Planning**
- Apply SOLID principles to the design:
  - **Single Responsibility**: What is the ONE thing each class/function does?
  - **Open/Closed**: How can this be extended without modification?
  - **Liskov Substitution**: Are any inheritance hierarchies safe?
  - **Interface Segregation**: What minimal interfaces are needed?
  - **Dependency Inversion**: What abstractions should dependencies use?

- Apply KISS: What's the simplest solution that works?
- Apply DRY: What existing code can be reused?
- Apply YAGNI: What can be left out?

**1.4 Test Planning**
- What unit tests are needed?
- What integration points need testing?
- What edge cases must be covered?

### Phase 2: Implementation (Writing the code)

**2.1 Create Implementation Plan**
Generate a step-by-step implementation plan:
```markdown
1. Create interfaces/abstractions first (Dependency Inversion)
2. Implement smallest working piece (KISS)
3. Add one responsibility at a time (Single Responsibility)
4. Write tests as you go (TDD when appropriate)
5. Refactor duplication only when it appears (Rule of Three for DRY)
6. Keep classes/functions focused and small
```

**2.2 Write Code Following Principles**

For each file created/modified:

**SOLID Compliance**
- Each class has ONE clear responsibility
- Each function does ONE thing
- Dependencies are injected, not hardcoded
- Abstractions are used where appropriate
- Interfaces are minimal and focused

**KISS Compliance**
- Use the simplest approach that works
- Avoid premature optimization
- Avoid unnecessary patterns or abstractions
- Prefer clear code over clever code
- Don't build for hypothetical futures

**DRY Compliance**
- Extract duplication after third occurrence (Rule of Three)
- Reuse existing utilities and helpers
- Define constants once
- Share common logic through composition

**Additional Practices**
- Defensive programming at boundaries
- Clear, descriptive naming
- Minimal comments (self-documenting code)
- Proper error handling
- Security considerations (input validation, no injection risks)
- Resource cleanup (context managers, try/finally)

**2.3 Write Tests**
- Unit tests for each new function/class
- Integration tests for component interactions
- Edge case coverage
- Mock external dependencies

### Phase 3: Verification (Ensuring quality)

**3.1 Self-Review Checklist**
- [ ] Does each class/function have a single, clear purpose?
- [ ] Can I describe what each part does in one sentence?
- [ ] Are there any YAGNI violations (unused features)?
- [ ] Is the code as simple as possible?
- [ ] Is there any duplication that should be extracted?
- [ ] Are all dependencies injected?
- [ ] Are names clear and descriptive?
- [ ] Are tests written and passing?
- [ ] Are edge cases handled?
- [ ] Are there any security concerns?
- [ ] Would a new developer understand this code easily?

**3.2 Run Tests**
- Execute all new tests
- Run existing test suite to ensure no regressions
- Check code coverage

**3.3 Integration Check**
- Does new code integrate cleanly with existing code?
- Are existing patterns followed?
- Is the codebase more maintainable than before?

### Phase 4: Documentation & Completion

**4.1 Update Documentation**
- Add docstrings for public APIs
- Update README if needed
- Document any new patterns or decisions
- Add examples if introducing new interfaces

**4.2 Final Commit**
- Prepare commit with clear message
- Link to Jira ticket if provided
- Include summary of changes and principles applied

## Output Format

The skill produces an execution plan and guides implementation:

```markdown
# Development Execution Plan: [Task Description]

## Phase 1: Analysis & Design

### Requirements
- Core requirement: [...]
- Acceptance criteria: [...]
- Edge cases: [...]
- Out of scope (YAGNI): [...]

### Architecture
- Files to create: [...]
- Files to modify: [...]
- Existing patterns to follow: [...]
- Dependencies needed: [...]

### Design
- Classes/Functions needed:
  - `ClassName`: Responsibility - [single clear purpose]
  - `function_name`: Does [one thing]

- SOLID considerations:
  - SRP: [how responsibilities are separated]
  - OCP: [extension points]
  - DIP: [abstractions to use]

- KISS approach: [simplest solution]
- DRY opportunities: [what to reuse]

### Test Plan
- Unit tests: [...]
- Integration tests: [...]
- Edge cases: [...]

## Phase 2: Implementation

### Step 1: [First step]
[Code to write]
Principles applied: [...]

### Step 2: [Second step]
[Code to write]
Principles applied: [...]

[Continue for each step...]

## Phase 3: Verification

### Self-Review Results
[Checklist with results]

### Test Results
[Test output and coverage]

## Phase 4: Completion

### Changes Summary
- Files created: [...]
- Files modified: [...]
- Tests added: [...]

### Principles Applied
- SOLID: [how each was applied]
- KISS: [how simplicity was maintained]
- DRY: [what was reused/extracted]
- Security: [considerations addressed]

### Commit Message
[Generated commit message]
```

## Prerequisites

- Git repository initialized
- Understanding of the task requirements
- Access to existing codebase
- Testing framework available

## Arguments

| Argument | Required | Description | Example |
|----------|----------|-------------|---------|
| `task_description` | Yes | Clear description of what to build | `"Add JWT auth"` |
| `jira_key` | No | Jira ticket reference | `SOC-15` |

## Execution Principles

### Start Simple, Evolve Carefully
1. Build the simplest thing that works first
2. Add complexity only when needed
3. Refactor only when duplication is clear (Rule of Three)
4. Test as you go

### Focus on One Thing at a Time
1. One responsibility per class/function
2. One change per commit (when possible)
3. One level of abstraction per function
4. One reason to change

### Make It Work, Make It Right, Make It Fast
1. **Make it work**: Get functionality working simply
2. **Make it right**: Apply principles, refactor duplication
3. **Make it fast**: Optimize only if needed (measure first)

### Communicate Intent
1. Names should reveal intent
2. Code should read like prose
3. Comments explain WHY, not WHAT
4. Tests document expected behavior

## Examples of Guided Development

### Example 1: Adding a Feature

**Task**: "Add email notification when post is published"

**Phase 1 - Analysis**:
```markdown
Requirements:
- Send email when post status = "published"
- Include post details in email
- Handle email failures gracefully

SOLID Design:
- SRP: Separate EmailService from publishing logic
- DIP: Depend on IEmailService interface, not concrete implementation
- OCP: Allow different notification types to be added

KISS: Just email for now, don't build notification framework
YAGNI: No need for email templates yet, simple text is fine
```

**Phase 2 - Implementation**:
```python
# Step 1: Create interface (DIP)
class IEmailService(Protocol):
    def send_email(self, to: str, subject: str, body: str) -> bool:
        """Send email. Returns True if successful."""
        ...

# Step 2: Implement simple email service (SRP, KISS)
class EmailService:
    def __init__(self, smtp_config: SMTPConfig):
        self.config = smtp_config

    def send_email(self, to: str, subject: str, body: str) -> bool:
        try:
            # Simple implementation using smtplib
            ...
            return True
        except Exception as e:
            logger.error(f"Email failed: {e}")
            return False

# Step 3: Inject into publisher (DIP)
class PostPublisher:
    def __init__(self, email_service: IEmailService):
        self.email_service = email_service

    def publish(self, post: Post) -> None:
        post.status = "published"
        post.save()

        # Notify but don't fail publish if email fails
        self.email_service.send_email(
            to=post.author.email,
            subject=f"Post published: {post.title}",
            body=f"Your post '{post.title}' is now live!"
        )
```

### Example 2: Refactoring

**Task**: "Extract email logic from UserManager (SRP violation)"

**Phase 1 - Analysis**:
```markdown
Current problem:
- UserManager has 3 responsibilities: users, emails, logging
- Violates SRP
- Hard to test
- Hard to reuse email logic

SOLID Design:
- SRP: Create EmailService, LoggingService
- DIP: Inject services into UserManager
- OCP: Services can be swapped/extended

KISS: Just extract services, don't over-engineer
DRY: Consolidate duplicate email code found in 3 places
```

**Phase 2 - Implementation**:
```python
# Step 1: Extract EmailService (existing email code)
class EmailService:
    def send_welcome_email(self, user: User) -> None: ...
    def send_reset_email(self, user: User, token: str) -> None: ...

# Step 2: Simplify UserManager (remove email code)
class UserManager:
    def __init__(self, email_service: EmailService):
        self.email_service = email_service

    def create_user(self, name: str, email: str) -> User:
        user = User(name=name, email=email)
        user.save()
        self.email_service.send_welcome_email(user)  # Delegate
        return user
```

## What This Skill Prevents

- **Big Ball of Mud**: Unstructured code that's hard to maintain
- **God Classes**: Classes that do too much
- **Spaghetti Code**: Tangled dependencies and unclear flow
- **Copy-Paste Programming**: Duplication instead of reuse
- **Premature Optimization**: Complex solutions to simple problems
- **Feature Creep**: Building unnecessary functionality
- **Fragile Code**: Code that breaks when extended
- **Technical Debt**: Shortcuts that cost more later

## Philosophy

Build software that is:
- **Intentional**: Every design choice has a reason
- **Simple**: No unnecessary complexity
- **Focused**: Each part does one thing well
- **Tested**: Verified to work correctly
- **Secure**: Protected by design
- **Maintainable**: Easy for others to understand and change
- **Extensible**: Can grow without breaking

This skill helps you build it right the first time.

## Integration with Workflow

Complete workflow:
1. `/start-task SOC-15` - Begin work on ticket
2. `/dev-execute "Add JWT authentication" SOC-15` - Build the feature using best practices
3. Review the implementation against checklist
4. Run tests
5. `/complete-task SOC-15 "Added JWT auth"` - Commit and close

This ensures disciplined development from start to finish.

## Notes

- The skill is a guide, not a rigid process
- Adapt principles to your context
- Simple problems don't need complex solutions
- Sometimes "good enough" is good enough
- Consistency with existing codebase matters
- Ask questions if requirements are unclear
- Iterate and refine as you go
- **Most importantly**: Think before you code

Good software is **designed**, not just **written**.
