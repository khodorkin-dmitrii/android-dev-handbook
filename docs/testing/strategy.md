# Testing Strategy

Testing strategy helps choose what to test first, which test levels to use and how to keep the test suite fast and stable.

## Testing Priorities

### What should be tested first?

Test high-business-value and high-risk code first: business logic, use cases, mappers, validators, reducers, error mapping and `ViewModel` state transitions.

Not everything needs the same level of coverage. A good strategy starts with questions: what breaks often, what is expensive to break in production, where there are complex conditions, edge cases, money, authorization, offline/cache or critical user flow.

UI and framework glue are usually tested selectively instead of trying to cover every `Activity` or composable with unit tests. Observable behavior matters more than private implementation details.

**In short:** prioritize tests by risk and value: business logic, mapping, state transitions and critical flows first, then UI/integration tests for important user scenarios.

### Unit tests vs UI tests

Unit tests check small pieces of logic quickly and in isolation: use cases, mappers, validators, reducers, `ViewModel` logic, error handling. They are cheap, fast and well suited for most business logic.

UI tests check app behavior closer to the user: screen rendering, clicks, navigation, forms, happy path and critical regression scenarios. But they are slower, more expensive to maintain and more often flaky.

A practical approach: cover most logic with unit tests, and keep UI tests for key user scenarios where UI + state + navigation integration matters.

**In short:** unit tests are fast and good for logic, UI tests are slower but useful for critical user flows and integration behavior.

### Mocks vs fakes

Mock is a test object that usually verifies interactions: whether a method was called, with which parameters and how many times.

Fake is a simplified working implementation of a dependency, for example an in-memory repository or test data source.

In Android, fakes are usually preferable when they are simple: the test becomes closer to real behavior and depends less on internal calls. Mocks are useful in focused cases where a specific interaction matters, for example analytics event, navigation callback or retry call.

**Important:** if everything is mocked, the test becomes fragile and starts checking implementation details instead of behavior. A good test usually provides input/action and checks observable output/state.

**In short:** prefer fakes for readable behavior-based tests and use mocks only when interaction verification is actually important.

### Test pyramid / testing priorities

Test pyramid is the idea that most tests should be fast unit tests, fewer should be integration tests, and even fewer should be expensive end-to-end/UI tests.

For Android this usually means many unit tests for domain/data/`ViewModel` logic, a moderate number of integration tests for repository/database/network boundaries, and a small number of UI tests for critical flows.

Priorities: business-critical logic, state transitions, error cases, edge cases, mapping between layers, persistence/migrations, authentication/payment-like flows and bugs that have already broken before.

**In short:** test pyramid keeps the suite fast and stable: many unit tests, fewer integration tests, and a small number of UI/E2E tests for critical paths.
