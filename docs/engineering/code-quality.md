# Code Quality

Code quality is about making code correct, readable, maintainable, testable and safe to change. Good code is not just "beautiful" code. It should help the team understand, modify and evolve the system without unnecessary risk.

These ideas are also useful during [Code Review](code-review.md), where reviewers check not only whether the code works, but whether it can be safely maintained.

## What is code quality?

Code quality describes how well code supports its purpose over time. High-quality code is understandable, predictable, covered by meaningful tests, and aligned with the architecture of the project.

Quality is contextual. A small script, a one-off migration and a long-lived Android feature do not need the same level of structure. The goal is to choose the simplest design that keeps the current behavior clear and future changes safe.

**In short:** code quality is the ability to change code confidently without constantly creating new bugs or slowing future work.

## Readability

Readability means the intent of the code is clear. A reader should be able to understand what the code does, why it exists and where the state is owned without reconstructing everything from low-level details.

Important parts of readability:

- clear names for classes, functions, variables and state;
- small functions with one main responsibility;
- predictable control flow;
- low surprise in side effects;
- explicit ownership of mutable state;
- code organized around meaningful domain or feature concepts.

Readability is not about making code verbose. It is about making the important decisions visible and removing noise that hides behavior.

**Practical note:** if a comment has to explain what every line does, the code probably needs better names, smaller functions or clearer structure.

## Maintainability

Maintainability means future changes can be made without breaking unrelated behavior. Maintainable code has clear boundaries, limited coupling, useful tests and explicit contracts between layers.

In Android, maintainability often depends on whether UI, state management, domain logic and data access are separated well enough. A change in API mapping should not require rewriting UI. A UI state change should not leak into repository internals.

Maintainable code also avoids hiding important behavior in global state, base classes, magic callbacks or implicit lifecycle assumptions.

**Key idea:** maintainability is not only about today's implementation. It is about reducing the cost and risk of tomorrow's change.

## Technical debt

Technical debt is a trade-off or accumulated complexity that makes future work slower or riskier. It can appear from rushed decisions, old requirements, missing tests, temporary workarounds, outdated dependencies or design that no longer fits the product.

Not every debt is bad. Sometimes taking a small debt is a reasonable business decision, especially when the scope is clear and the team plans to revisit it. The risk starts when debt is invisible, undocumented or spread across critical paths.

Common signs of unmanaged debt:

- changes take much longer than expected;
- small fixes break unrelated behavior;
- tests are missing or hard to write;
- important logic is duplicated;
- nobody knows which layer owns a decision;
- a "temporary" workaround becomes part of the architecture.

**Important:** technical debt should be named and managed. Ignored debt turns into a tax on every future feature.

## YAGNI

YAGNI means "You Aren't Gonna Need It". Do not add functionality, abstractions or extension points before there is a real need.

Premature abstraction often makes code harder to read and change. A generic interface, plugin system or strategy layer can be useful when there are real variations, but harmful when there is only one implementation and no concrete second use case.

YAGNI does not mean avoiding design. It means designing for known requirements and keeping the code easy to extend when a real need appears.

**Common pitfall:** adding an abstraction "just in case" can create more maintenance cost than the future change it was supposed to simplify.

## Code smells

Code smells are signs that code may have design, readability or maintainability problems. They are not always bugs, and they do not always require immediate refactoring.

Common examples:

- long method;
- large class / god object;
- duplicated code;
- feature envy;
- primitive obsession;
- shotgun surgery;
- deep nesting;
- too many boolean flags;
- hidden side effects;
- unnecessary abstraction.

A smell is a signal to inspect context. Sometimes the right answer is a small cleanup. Sometimes it is better to leave the code alone until there is a real reason to change it.

**In short:** code smells are useful warning signs, not automatic rewrite instructions.

## Refactoring

Refactoring is changing the internal structure of code without changing external behavior. It improves readability, maintainability, testability or architecture while preserving what users and callers observe.

Good refactoring is usually incremental. It starts from a small boundary, keeps behavior stable and is supported by tests or clear manual checks. Large rewrites are riskier because they change structure and behavior at the same time.

Practical refactoring examples:

- extract a mapper from `ViewModel`;
- split a large function into named steps;
- move data access out of UI layer;
- replace duplicated logic with a shared function;
- introduce a small interface when a real second implementation appears;
- make state ownership explicit.

**Important:** refactoring should reduce complexity. If it only moves code around or adds layers without making change safer, it may not be worth doing.
