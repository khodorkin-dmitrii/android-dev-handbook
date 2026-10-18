# Coroutines & Flow

Этот раздел посвящён Kotlin Coroutines и Flow в Android: асинхронной работе, structured concurrency, cancellation, потокам данных, hot state, доставке событий и lifecycle-aware collection.

Практичный порядок изучения: начните с основ корутин и владения scope. Затем изучите основы Flow и operators, после чего сравните channels со `StateFlow` и `SharedFlow`. Перед подключением потоков к Android UI разберите lifecycle-aware collection.

## Основы корутин

- [Coroutines Basics](basics.md) - suspending work, concurrency, dispatchers, builders и переключение execution context.
- [Coroutine Scopes & Cancellation](scopes-cancellation.md) - владение scope, structured concurrency, job hierarchy, supervision, cleanup и cooperative cancellation.

## Потоки данных и коммуникация

- [Flow Basics](flow-basics.md) - cold streams, collection, context, cancellation и границы обработки ошибок.
- [Flow Operators](flow-operators.md) - transformation, flattening, combining, buffering, retry и terminal operations.
- [Channels](channels.md) - семантика send/receive, buffering, closing, cancellation и point-to-point communication.
- [StateFlow & SharedFlow](stateflow-sharedflow.md) - hot streams, observable state, broadcasts, replay, `stateIn` и `shareIn`.

## Интеграция с Android lifecycle

- [Lifecycle-aware Collection](lifecycle-aware-collection.md) - `repeatOnLifecycle`, `collectAsStateWithLifecycle`, параллельные collectors и границы Compose effects.
