# Development Review Skill

Performs a comprehensive code quality review based on engineering best practices including SOLID principles, KISS, DRY, and more. This skill helps ensure code changes meet high engineering standards before they're merged.

## Usage

```
/dev-review [file_pattern]
```

### Examples

```bash
# Review all changed files in working directory
/dev-review

# Review specific file
/dev-review src/core/generator.py

# Review all Python files in a directory
/dev-review "src/**/*.py"

# Review specific pattern
/dev-review "src/agents/*.py"
```

## What It Does

### 1. Git Status & Diff Analysis
- Identifies all modified, added, and deleted files
- Analyzes the actual code changes (not just file names)
- Determines scope of review based on changes

### 2. SOLID Principles Review
Reviews each file against SOLID principles:

**S - Single Responsibility Principle**
- Does each class/function have one clear purpose?
- Are concerns properly separated?
- Can you describe what it does in one sentence?

**O - Open/Closed Principle**
- Is code open for extension but closed for modification?
- Are abstractions used appropriately?
- Can new behavior be added without changing existing code?

**L - Liskov Substitution Principle**
- Can derived classes replace base classes seamlessly?
- Are inheritance hierarchies logical and safe?
- Do subclasses honor base class contracts?

**I - Interface Segregation Principle**
- Are interfaces focused and minimal?
- Do clients depend only on methods they use?
- Are large interfaces broken into smaller, specific ones?

**D - Dependency Inversion Principle**
- Do high-level modules depend on abstractions?
- Are dependencies injected rather than hardcoded?
- Can implementations be swapped without changing dependents?

### 3. KISS (Keep It Simple, Stupid)
- Is the solution as simple as possible?
- Are there unnecessary abstractions or patterns?
- Could a simpler approach work just as well?
- Is the code easy to understand at first glance?

### 4. DRY (Don't Repeat Yourself)
- Is there duplicated code that could be extracted?
- Are there repeated patterns that could use abstraction?
- Is configuration/data duplicated across files?
- Are magic numbers/strings defined once?

### 5. Additional Best Practices

**YAGNI (You Aren't Gonna Need It)**
- Is everything in the code actually needed now?
- Are there features for hypothetical future requirements?
- Is there speculative generalization?

**Separation of Concerns**
- Are different concerns in separate modules/classes?
- Is business logic separated from infrastructure?
- Are presentation, domain, and data layers distinct?

**Composition Over Inheritance**
- Is inheritance used appropriately?
- Could composition be used instead?
- Are class hierarchies shallow and logical?

**Defensive Programming**
- Are inputs validated at boundaries?
- Are error cases handled appropriately?
- Are null/None values handled safely?
- Are resources properly cleaned up?

**Code Clarity**
- Are names descriptive and meaningful?
- Is the code self-documenting?
- Are comments used only when necessary?
- Is the code formatted consistently?

**Performance & Scalability**
- Are there obvious performance issues (N+1 queries, etc.)?
- Will the code scale with data growth?
- Are expensive operations avoided in loops?
- Are resources used efficiently?

**Security**
- Are there injection vulnerabilities (SQL, XSS, command)?
- Are secrets/credentials properly handled?
- Is user input sanitized?
- Are authentication/authorization checks present?

**Testability**
- Can the code be easily unit tested?
- Are dependencies mockable?
- Is test coverage adequate?
- Are tests present for new functionality?

**Error Handling**
- Are exceptions caught at appropriate levels?
- Are error messages helpful and actionable?
- Is error handling consistent across codebase?
- Are edge cases considered?

## Output Format

The skill produces a structured report:

```markdown
# Code Review Report

## Summary
- Files reviewed: X
- Issues found: Y (Z critical, A moderate, B minor)
- Overall assessment: [PASS/NEEDS_WORK/FAIL]

## Critical Issues
[Issues that must be fixed before merging]

## Moderate Issues
[Issues that should be addressed but don't block merging]

## Minor Issues
[Suggestions for improvement]

## Positive Observations
[Things done well, patterns to continue]

## Recommendations
[Specific actionable changes to make]
```

## Prerequisites

- Git repository initialized
- Changes present in working directory or specific files to review
- Code must be syntactically valid (parses without errors)

## Arguments

| Argument | Required | Description | Example |
|----------|----------|-------------|---------|
| `file_pattern` | No | Glob pattern or specific file to review. If omitted, reviews all changed files | `"src/**/*.py"` |

## Review Criteria

Each issue is rated by severity:

- **CRITICAL**: Violates core principles, has security issues, or will cause bugs
- **MODERATE**: Reduces code quality, maintainability, or performance
- **MINOR**: Style issues, missed optimizations, or minor improvements

## What It Doesn't Do

- Does not automatically fix issues (provides recommendations)
- Does not run tests (recommends testing)
- Does not modify code (read-only analysis)
- Does not enforce specific formatting (suggests improvements)

## Integration with Workflow

Typical workflow:
1. Write code and make changes
2. `/dev-review` - Review changes before commit
3. Address critical and moderate issues
4. `/complete-task SOC-X "description"` - Commit when review passes

Or integrate into pull request workflow:
1. Create PR
2. `/dev-review` on PR branch
3. Address issues
4. Push fixes
5. Re-review if needed

## Customization

The skill adapts to your codebase:
- Recognizes language-specific patterns (Python, JavaScript, Go, etc.)
- Considers existing architectural patterns
- Respects project conventions found in codebase
- Focuses on consistency with existing code style

## Examples of Issues Caught

**SOLID Violations**
```python
# Before: Class doing too much (SRP violation)
class UserManager:
    def create_user(self): ...
    def send_email(self): ...
    def log_to_database(self): ...
    def generate_report(self): ...

# After: Single responsibilities
class UserService:
    def create_user(self): ...

class EmailService:
    def send_email(self): ...
```

**DRY Violations**
```python
# Before: Repetition
result1 = requests.get(url, headers={'Authorization': f'Bearer {token}'}, timeout=30)
result2 = requests.get(url2, headers={'Authorization': f'Bearer {token}'}, timeout=30)

# After: Extract common pattern
def make_request(url):
    return requests.get(url, headers={'Authorization': f'Bearer {token}'}, timeout=30)
```

**KISS Violations**
```python
# Before: Over-engineered
class UserFactoryBuilder:
    def with_strategy(self): ...
    def build_factory(self): ...

# After: Simple and direct
def create_user(name, email):
    return User(name, email)
```

**Security Issues**
```python
# Before: SQL injection risk
query = f"SELECT * FROM users WHERE id = {user_id}"

# After: Parameterized query
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))
```

## Notes

- Review is based on code analysis and established patterns
- Some suggestions may not apply to all contexts
- Use judgment when applying recommendations
- Focus on critical issues first
- Minor issues can be addressed over time
- The goal is improvement, not perfection

## Philosophy

Good code is:
- **Simple**: Easy to understand and modify
- **Focused**: Each part has one clear purpose
- **Consistent**: Follows established patterns
- **Tested**: Verified to work correctly
- **Secure**: Protected against common vulnerabilities
- **Maintainable**: Can be modified by others easily

This skill helps you achieve these qualities systematically.
