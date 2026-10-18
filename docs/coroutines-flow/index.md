# Coroutines & Flow

This section covers Kotlin Coroutines and Flow in Android: asynchronous work, structured concurrency, cancellation, streams, hot state, event delivery, and lifecycle-aware collection.

For a practical learning path, start with coroutine basics and scope ownership. Continue with Flow fundamentals and operators, then compare channels with `StateFlow` and `SharedFlow`. Finish with lifecycle-aware collection before connecting streams to Android UI.

## Coroutine foundations

- [Coroutines Basics](basics.md) - suspending work, concurrency, dispatchers, builders, and switching execution context.
- [Coroutine Scopes & Cancellation](scopes-cancellation.md) - scope ownership, structured concurrency, job hierarchies, supervision, cleanup, and cooperative cancellation.

## Streams and communication

- [Flow Basics](flow-basics.md) - cold streams, collection, context, cancellation, and error boundaries.
- [Flow Operators](flow-operators.md) - transformation, flattening, combining, buffering, retry, and terminal operations.
- [Channels](channels.md) - send and receive semantics, buffering, closing, cancellation, and point-to-point communication.
- [StateFlow & SharedFlow](stateflow-sharedflow.md) - hot streams, observable state, broadcasts, replay, `stateIn`, and `shareIn`.

## Android lifecycle integration

- [Lifecycle-aware Collection](lifecycle-aware-collection.md) - `repeatOnLifecycle`, `collectAsStateWithLifecycle`, parallel collectors, and Compose effect boundaries.
