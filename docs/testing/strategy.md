# Testing Strategy

A testing strategy decides what to test, at which level, and how to keep feedback fast and reliable. The goal is confidence in important behavior, not a particular coverage percentage or the largest possible test suite.

## Testing priorities

### What should be tested first?

Prioritize by impact and probability of failure. Start with behavior that is expensive to break or difficult to verify manually:

- business rules, calculations and state transitions;
- error handling, retries and boundary conditions;
- mapping between network, database, domain and UI models;
- persistence, migrations, caching and offline behavior;
- authentication, payments and other critical user flows;
- regressions for bugs that have already reached users.

Test observable behavior through public APIs. Tests coupled to private methods or an exact internal call sequence often fail during harmless refactoring without finding a real regression.

Coverage is a diagnostic signal, not the target. A highly covered low-risk mapper may matter less than one missing test for a destructive migration or payment state transition.

### Test size and execution environment

Test size and where a test runs are separate decisions:

| Scope | Purpose | Typical Android examples |
|---|---|---|
| Small / unit | One unit in isolation | Mapper, validator, reducer, use case, ViewModel |
| Medium / integration | Several real collaborators | Repository with a database, serialization, navigation contract |
| Large / end-to-end | User-visible flow across layers | Sign-in, checkout, offline recovery |

Local tests run on the host JVM and are usually fast. Instrumented tests run on a device or emulator and can use the real Android framework. A local test can still cover several units with Robolectric, while an instrumented test can narrowly verify one framework integration such as Room migration behavior.

Use the cheapest environment that faithfully exercises the behavior. Keep pure Kotlin logic in local tests; use Robolectric when host-side Android behavior is sufficient; use instrumented tests when correctness depends on the actual framework, device, database implementation or rendering.

The test pyramid is a cost model, not a quota: use many fast tests for deterministic logic, fewer integration tests for boundaries such as Room, serialization and repository cache policy, and a small number of UI/end-to-end tests for critical flows. Do not repeat every business-rule combination through the UI when lower-level tests provide the same confidence.

## Test doubles

A test double replaces a dependency:

- a **fake** is a lightweight working implementation, such as an in-memory repository;
- a **stub** returns predefined answers;
- a **mock** records interactions and verifies calls.

Prefer fakes or stubs when result or state matters. Use mocks when the interaction itself is the requirement, for example sending one analytics event. Mocking every collaborator makes tests mirror implementation details and may hide integration problems.

## Keeping the suite reliable

A useful test is deterministic, isolated, readable and fast enough for its feedback loop. Control time, dispatchers, randomness and external I/O. Do not use arbitrary delays; wait for observable conditions or use virtual time where possible. Reset databases, dependency containers and global state between tests.

Run fast tests on every change and broader suites in CI. Treat flaky tests as defects: fix or quarantine them with an owner and deadline instead of normalizing retries.

## Related topics

- [ViewModel Testing](viewmodel-testing.md)
- [Coroutines & Flow Testing](coroutines-flow-testing.md)
- [Android UI Testing](android-ui-testing.md)
- [Compose Testing](../compose/testing.md)
- [Architecture Basics](../architecture/basics.md)
