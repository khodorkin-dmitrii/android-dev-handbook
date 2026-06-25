# Code Review

Code review is a quality practice for correctness, maintainability, shared ownership, knowledge sharing and production risk reduction. It is not about finding someone to blame.

Code review applies many ideas from [Code Quality](code-quality.md): readability, maintainability, code smells, unnecessary abstractions and safe refactoring.

## What is code review for?

Code review helps the team catch problems before they reach production and keep the codebase understandable for more than one person. It also spreads context: reviewers learn the change, and authors receive feedback before the code becomes part of the shared system.

A good review checks both behavior and maintainability. The code may work today but still be hard to change tomorrow if it hides state, mixes layers or adds premature abstractions.

**In short:** code review reduces production risk and keeps code ownership shared across the team.

## A practical code review workflow

Experienced engineers usually review a pull request in several passes, moving from high-level concerns to implementation details.

1. Understand the change
    - What problem is being solved?
    - Is the scope appropriate?
    - Is this the right solution?

2. Evaluate the design
    - Does it fit the existing architecture?
    - Are responsibilities well separated?
    - Is the abstraction level appropriate?

3. Verify correctness
    - Bugs
    - Edge cases
    - Thread safety
    - Lifecycle
    - Error handling

4. Evaluate maintainability
    - Readability
    - Simplicity
    - Testability
    - Ease of future modifications

5. Review style
    - Naming
    - Formatting
    - Minor language idioms
    - Consistency

**Key idea:** experienced reviewers spend most of their effort understanding the problem, validating the design and ensuring correctness. Style issues still matter, but they should usually be reviewed last, and many of them can be enforced automatically with formatting and static analysis tools.

## What to check in a pull request?

A pull request should be reviewed from several angles:

- correctness - does the change solve the intended problem?
- readability - can another developer understand it quickly?
- maintainability - can this code be changed safely later?
- architecture boundaries - does logic stay in the right layer?
- state and lifecycle - is state owned and collected safely?
- error handling - are failures represented and handled clearly?
- tests - are important cases covered?
- performance - does the change avoid unnecessary work on hot paths?
- security and privacy - are sensitive data and permissions handled safely?
- UX states - loading, empty, error and disabled states.

Not every PR needs deep discussion of every item. The review depth should match the risk and scope of the change.

**Practical note:** review observable behavior and contracts first, then implementation details.

## How to review Android code?

Android code review needs attention to platform-specific risks:

- lifecycle safety;
- avoiding `Activity` / `Context` leaks;
- work accidentally running on the main thread;
- coroutine scope and cancellation;
- `Flow` collection and lifecycle awareness;
- Compose recomposition and state issues;
- navigation and one-off events;
- resource handling;
- configuration changes;
- error, empty and loading states.

For `ViewModel`, check that UI state is explicit and side effects are not mixed with durable state. For Compose, check state ownership, stable inputs and unnecessary recomposition. For data layer, check error mapping, threading, cancellation and DTO/domain separation.

**Important:** Android bugs often come from lifecycle and state ownership, not only from incorrect business logic.

## How to give good review feedback?

Good review feedback is specific, respectful and actionable. It explains why something matters and separates required changes from suggestions.

Useful habits:

- point to the concrete problem;
- explain the risk or trade-off;
- ask questions when intent is unclear;
- avoid personal tone;
- prefer small actionable comments;
- mark optional ideas as suggestions;
- acknowledge when a decision is a judgment call.

Examples of tone:

- Required: "This can leak `Activity` because the object is Singleton-scoped. Can we use `@ApplicationContext` or move this dependency closer to the screen scope?"
- Suggestion: "This mapper is getting large. Maybe we can split formatting from API mapping?"
- Question: "Is this event expected to survive configuration change?"

**Key idea:** review comments should help improve the code, not make the author defend themselves.

## Common code review comments

Neutral review comments are easier to act on when they describe the concern clearly:

- "Can we move this logic out of the UI layer?"
- "This looks like state rather than a one-off event."
- "This may run on the main thread."
- "Can we add a test for this edge case?"
- "This abstraction seems premature. Is there a real second use case?"
- "Can we map this DTO before exposing it outside the data layer?"
- "What happens here on retry or configuration change?"
- "Can we make the error state explicit in `UiState`?"

These comments are starting points. The best review feedback includes the reason and the expected direction, not only the requested change.

## What makes a good pull request?

A good pull request is small enough to review, focused on one topic and explained by a clear description. It should not mix unrelated refactoring with feature changes unless the refactoring is required for the feature.

Useful PR description usually includes:

- what changed;
- why it changed;
- how it was tested;
- screenshots or recordings for UI changes;
- known limitations or follow-up work.

Good PRs reduce reviewer guesswork. They make the important decisions visible and keep the diff focused.

**In short:** a good PR is focused, explained, tested and small enough for a meaningful review.
