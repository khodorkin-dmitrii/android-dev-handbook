# Testing

This section covers an Android testing strategy and focused tests for ViewModels, asynchronous code, and user interfaces. Choose a test level according to the behavior and risk, keeping most feedback fast and deterministic.

## Suggested path

Start with the strategy: decide what to test and at which boundary. Then test state and events in ViewModels, control virtual time in coroutine tests, and use UI tests for interactions that require the Android or Compose runtime. The [Code Review](../engineering/code-review.md) chapter helps connect tests with change risk.

## Articles

- [Testing Strategy](strategy.md) - test levels, useful boundaries, fakes, and maintainability.
- [ViewModel Testing](viewmodel-testing.md) - state transitions, one-off effects, and dependency control.
- [Coroutines & Flow Testing](coroutines-flow-testing.md) - test dispatchers, virtual time, and stream assertions.
- [Android UI Testing](android-ui-testing.md) - Compose and View interactions, semantics, and device-level checks.
