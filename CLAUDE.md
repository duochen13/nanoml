# CLAUDE.md - Project Coding Guidelines

These guidelines reduce common LLM coding errors by prioritizing caution over speed for non-trivial tasks.

## Core Principles

### 1. Think Before Coding

Surface assumptions and confusion rather than hiding them.

**Key instruction:** State your assumptions explicitly. If uncertain, ask.

- Present multiple interpretations when they exist
- Pause to clarify confusing elements before proceeding
- Don't guess at requirements or implementation details

### 2. Simplicity First

Write minimal code addressing only the stated problem.

**Key instruction:** No features beyond what was asked.

- Discourage speculative abstractions
- Avoid unrequested flexibility
- Don't add error handling for impossible scenarios
- If 200 lines could be 50, rewrite it
- No defensive programming for internal code that can't fail

### 3. Surgical Changes

When modifying existing code, make only necessary edits.

**Key instruction:** Match existing style, even if you'd do it differently.

- Changes should trace directly to user requests
- Remove only code made unused by your edits
- Don't refactor or clean up pre-existing code unless explicitly asked
- Preserve formatting, naming conventions, and patterns

### 4. Goal-Driven Execution

Transform requests into verifiable success criteria through multi-step planning.

**Example:** Convert "Add validation" into:
1. Write tests for invalid inputs
2. Make them pass

This approach:
- Enables independent iteration
- Reduces clarification needs
- Provides clear success metrics

## Success Metrics

These guidelines succeed when:
- Unnecessary diff changes decrease
- Clarifying questions precede implementation
- Code changes are minimal and focused
- Tests define the requirements before implementation

---

*Source: Adapted from [Andrej Karpathy's CLAUDE.md](https://github.com/multica-ai/andrej-karpathy-skills/blob/main/CLAUDE.md)*
