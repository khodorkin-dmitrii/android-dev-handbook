# Code Quality

Code quality is the ability to understand, verify, and change code without unnecessary risk. Good code is not merely "clean" or stylistically attractive. It must behave correctly, express its intent, fit the architecture, and remain practical to test and maintain.

These ideas also guide [Code Review](code-review.md), where reviewers evaluate both the current behavior and the cost of future change.

## What is code quality?

Quality is contextual. A one-off migration, a small internal tool, and a long-lived Android feature do not need the same structure or test coverage. The goal is the simplest design that makes important behavior explicit and keeps likely changes safe.

Useful questions include:

- Is the behavior correct for normal, error, and lifecycle paths?
- Can another developer understand the intent without reconstructing hidden assumptions?
- Are responsibilities and ownership clear?
- Can the important behavior be tested without reproducing the whole application?
- Will a likely change stay local, or spread across unrelated modules?

No single metric answers all of these questions.

## Readability

Readable code makes intent visible. A reader should understand what the code does, why it exists, and where mutable state is owned without translating low-level operations into a mental model first.

Readability usually benefits from:

- names that describe domain meaning rather than implementation mechanics;
- functions with one coherent responsibility;
- predictable control flow and explicit side effects;
- limited nesting and early handling of invalid states;
- consistent Kotlin formatting and naming conventions;
- comments that explain constraints or decisions, not every line.

Small functions are not automatically readable. Splitting a simple operation across many indirections can hide the actual flow. Prefer a clear unit of behavior over an arbitrary line limit.

## Maintainability and boundaries

Maintainability means a change can be made without breaking unrelated behavior. It depends on cohesive responsibilities, limited coupling, stable contracts, useful tests, and clear ownership.

In Android, separate concerns where they change for different reasons:

- UI renders state and sends user actions;
- a state holder coordinates screen behavior;
- domain logic expresses product rules when that separation adds value;
- repositories define data access boundaries;
- data sources handle concrete network, database, or platform APIs.

These are guidelines, not a requirement to create every layer for every feature. A small feature may not need a separate domain layer. Extra indirection is justified when it isolates volatility, enables reuse, improves testing, or clarifies ownership.

Avoid hiding important behavior in global mutable state, deep inheritance, magic callbacks, or implicit lifecycle assumptions. A boundary is useful only when its contract is clearer than the code it replaces.

## Technical debt

Technical debt is an intentional trade-off or accumulated complexity that makes future work slower or riskier. It can come from time pressure, changed requirements, temporary workarounds, missing tests, outdated dependencies, or a design that no longer fits the product.

Not all debt is a mistake. A deliberate shortcut can be reasonable when its scope, risk, and expected lifetime are understood. Unmanaged debt is more dangerous: it is invisible, repeatedly surprises the team, or spreads through critical paths.

Record meaningful debt with:

- the current limitation and its impact;
- why the trade-off was accepted;
- the affected owner or area;
- a trigger for revisiting it, such as the next feature in that code;
- a concrete removal or containment plan when one is known.

Do not turn every imperfect detail into a ticket. Track debt that changes risk, delivery speed, reliability, security, or the cost of planned work.

## YAGNI and abstractions

YAGNI means "You Aren't Gonna Need It": do not add functionality, extension points, or abstractions before there is a concrete need.

An interface with one implementation is not automatically wrong. It can represent a real boundary, isolate an external API, or enable deterministic tests. It becomes suspicious when it only mirrors another type, has no independent contract, and exists for a hypothetical future implementation.

Before adding an abstraction, ask:

- What variation or dependency does it isolate today?
- Does it make the caller simpler?
- Can its contract be named precisely?
- Would introducing it later be significantly harder?

Design for known requirements while leaving code easy to refactor when evidence appears.

## Code smells

Code smells are signals of possible design or maintenance problems, not proof of a bug and not automatic rewrite instructions.

Common examples include:

- long methods or large classes with several reasons to change;
- duplicated product rules;
- deep nesting or many boolean flags;
- feature envy and unclear ownership;
- primitive values that hide domain constraints;
- changes that require edits across many unrelated files;
- hidden side effects or order-dependent callbacks;
- abstractions that add navigation without reducing complexity.

Inspect the context before acting. Duplication of two similar lines may be cheaper than a shared abstraction that couples unrelated features. Conversely, duplicated business rules can create inconsistent behavior and deserve early attention.

## Refactoring safely

Refactoring changes internal structure while preserving externally observable behavior. It should make the next change safer or the current behavior clearer.

A practical sequence is:

1. Define the behavior that must remain stable.
2. Add or identify tests at the boundary being changed.
3. Make one structural change at a time.
4. Run focused checks after each step.
5. Review the result for reduced complexity, not merely moved code.

Examples include extracting mapping from a `ViewModel`, splitting a large workflow into named steps, moving data access out of UI code, consolidating duplicated rules, or making state ownership explicit.

Do not mix a broad rewrite, behavior change, dependency upgrade, and formatting pass in one review unless they cannot be separated. Smaller diffs make regressions and design decisions easier to see.

## Automated quality gates

Automation should catch repeatable problems before a reviewer spends attention on them:

```bash
./gradlew test lint
```

A typical Android pipeline combines compilation, unit tests, Android Lint, consistent formatting, and project-specific static analysis. Instrumented or integration tests should be added where their risk coverage justifies the cost.

Android Lint detects issues related to correctness, security, performance, accessibility, internationalization, and Android API usage. Run it explicitly in CI; it is not automatically part of every Gradle build. Configure severity to match the project and suppress a finding only with a narrow scope and a documented reason.

For an existing project with many findings, a baseline can prevent new violations while old ones are reduced gradually. A baseline is migration support, not evidence that recorded issues are harmless. Avoid regenerating it merely to make CI green.

## Metrics and trade-offs

Coverage, complexity, duplication, warning counts, and build times can reveal trends, but they are proxies rather than quality itself.

- High coverage does not prove that important behavior is asserted.
- Low complexity does not guarantee a good domain model.
- Zero duplication can indicate premature abstraction.
- More layers do not automatically mean better architecture.

Use metrics to start investigation and compare change over time. Combine them with production signals such as crashes, ANRs, defect escape rate, rollback frequency, and the time required to make common changes.

## Common mistakes

- Treating formatting preferences as the main measure of quality.
- Adding architecture layers without a concrete responsibility.
- Optimizing for test coverage percentage instead of risk coverage.
- Suppressing static-analysis findings without recording why.
- Refactoring and changing behavior in one large, hard-to-review diff.
- Leaving temporary workarounds without ownership or a revisit trigger.
- Applying a code smell mechanically without considering context.
- Rewriting stable code only because a newer pattern exists.

## See also

- [Code Review](code-review.md)
- [Architecture Basics](../architecture/basics.md)
- [Testing Strategy](../testing/strategy.md)
- [Kotlin coding conventions](https://kotlinlang.org/docs/coding-conventions.html)
- [Android Lint](https://developer.android.com/studio/write/lint)
