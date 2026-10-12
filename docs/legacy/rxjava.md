# RxJava

RxJava is a reactive library for composing asynchronous and event-based streams. It is now a legacy choice for most new Android code, where Coroutines and Flow are usually preferred, but it remains common in production applications and migration work.

An Rx chain has three concerns:

- a source such as `Observable`, `Single`, or `Flowable`;
- operators that transform, combine, schedule, or observe emissions;
- a subscription represented by a `Disposable`.

Unless an operator states otherwise, an error terminates the stream. Disposing a subscription stops downstream delivery, but cancellation of the underlying work depends on whether the source supports it.

## Core reactive types

### `Observable` and `Flowable`

`Observable<T>` emits zero or more items and does not implement the Reactive Streams backpressure protocol. It fits UI events and ordinary streams where the producer cannot overwhelm the consumer or where sampling and dropping are explicitly acceptable.

`Flowable<T>` is designed for streams whose producer may be faster than downstream. Backpressure means downstream can request a bounded number of items rather than accepting an unlimited push rate. It is useful for large or high-frequency streams, not automatically for every database or network call.

When adapting a non-backpressured source with `toFlowable(strategy)`, choose a strategy from the data contract:

- `BUFFER` keeps pending items, but an unbounded buffer can exhaust memory;
- `DROP` discards items that cannot be delivered in time;
- `LATEST` keeps only the newest pending item;
- `ERROR` reports `MissingBackpressureException` when demand is insufficient;
- `MISSING` adds no strategy at the boundary, so a downstream backpressure operator must handle it.

Do not treat a strategy as a performance switch. Dropping a payment event is incorrect, while dropping intermediate sensor readings may be acceptable.

### `Single`, `Maybe`, and `Completable`

- `Single<T>` emits exactly one value or an error.
- `Maybe<T>` emits one value, completes empty, or reports an error.
- `Completable` emits no value and only completes or reports an error.

```kotlin
fun loadUser(id: String): Single<User>
fun findCachedUser(id: String): Maybe<User>
fun updateUser(user: User): Completable
```

Choose the narrowest type that expresses the contract. A possibly missing database row is usually a `Maybe`, while a save whose result is only success or failure is a `Completable`.

## Transforming inner sources

### `map` and `flatMap`

`map` performs a one-to-one synchronous transformation. It does not introduce another reactive source.

```kotlin
usersObservable.map { user -> user.name }
```

`flatMap` maps each item to an inner source and merges its emissions into the outer stream. It is suitable for dependent asynchronous work.

```kotlin
userIdsObservable
    .flatMap { id -> api.getUser(id).toObservable() }
```

### `flatMap`, `concatMap`, and `switchMap`

These operators differ in concurrency, ordering, and cancellation:

- `flatMap` may subscribe to several inner sources concurrently and does not preserve their emission order;
- `concatMap` waits for each inner source to complete before subscribing to the next, preserving source order;
- `concatMapEager` subscribes eagerly but buffers results to emit them in source order;
- `switchMap` disposes the previous inner subscription when a new source item arrives and keeps only the latest inner source active.

`switchMap` is useful for search queries, but disposal is not a transaction rollback. A disposed network request may still reach the server, so writes must not rely on `switchMap` for correctness.

```kotlin
queryChanges
    .debounce(300, TimeUnit.MILLISECONDS)
    .distinctUntilChanged()
    .switchMap { query -> api.search(query).toObservable() }
```

## Scheduling

### `subscribeOn` and `observeOn`

`subscribeOn(scheduler)` schedules subscription to the upstream source. Its position in a simple chain does not change which upstream source it affects. With multiple `subscribeOn` calls, the one closest to the source normally controls where the source subscription begins; extra switches make behavior harder to reason about.

`observeOn(scheduler)` moves downstream notifications to that scheduler from that point until another `observeOn` changes it. It also introduces an asynchronous boundary and buffering, so unnecessary switches have a cost.

```kotlin
api.loadUser()
    .subscribeOn(Schedulers.io())
    .map { it.toUiModel() }
    .observeOn(AndroidSchedulers.mainThread())
    .subscribe(
        { uiModel -> render(uiModel) },
        { error -> showError(error) },
    )
```

`Schedulers.io()` is intended for blocking I/O and may grow its thread pool. CPU-intensive work belongs on `Schedulers.computation()`. UI access belongs on `AndroidSchedulers.mainThread()`.

## Creating sources

### `just`, `fromIterable`, and `defer`

`just(value)` captures and emits the supplied value. `Observable.just(list)` emits one item - the list itself. `fromIterable(list)` emits every list element separately.

```kotlin
Observable.just(listOf("A", "B"))          // Observable<List<String>>
Observable.fromIterable(listOf("A", "B")) // Observable<String>
```

`defer` creates a new source for each subscriber at subscription time. Use it when a value or decision must be evaluated lazily rather than captured while the chain is assembled.

```kotlin
val currentTime = Observable.defer {
    Observable.just(System.currentTimeMillis())
}
```

## Combining streams

- `merge` forwards emissions from all sources as they arrive; cross-source order is not guaranteed.
- `concat` subscribes to sources sequentially and waits for each one to complete.
- `zip` combines the first item from each source, then the second item from each, and so on.
- `combineLatest` emits after every source has emitted once, then reacts whenever any source changes.
- `withLatestFrom` emits only when the primary source emits and adds the latest values from the other sources.
- `switchOnNext` consumes a stream of streams and forwards only the latest inner stream.

```kotlin
Observable.combineLatest(user, settings) { userValue, settingsValue ->
    UiModel(userValue, settingsValue)
}
```

Be careful with sources that never complete: a `concat` chain may never reach its next source, and `zip` may wait forever for the next matching item.

## Side effects, errors, and disposal

`doOnNext`, `doOnError`, `doOnComplete`, `doOnSubscribe`, `doOnDispose`, and `doFinally` observe lifecycle events without changing the normal emissions. They are useful for logging, metrics, tracing, and cleanup. Keep business state transitions in explicit operators or subscribers instead of hiding them in `doOn...` callbacks.

```kotlin
repository.observeItems()
    .doOnNext { items -> logger.log("items=${items.size}") }
    .doOnError(logger::log)
    .doFinally { progress.hide() }
```

Always define an error path. A one-argument `subscribe` has no application error handler, and unhandled errors may reach `RxJavaPlugins.onError`. Use `onErrorReturn`, `onErrorResumeNext`, or `retry` only when their semantics match the operation. Unbounded retry loops can amplify outages or repeat non-idempotent writes.

On Android, bind subscriptions to an explicit owner. A `CompositeDisposable` is commonly cleared when the corresponding screen, presenter, or component is destroyed. A retained subscription that captures an `Activity`, `Fragment`, or View can leak it or deliver a late UI update.

## Migrating to Coroutines and Flow

Migrate at boundaries rather than rewriting every chain at once. First preserve behavior with tests, including ordering, cancellation, retry, and empty-result semantics. Then replace one API or feature and keep adapters at the boundary while both models coexist.

Typical conceptual mappings include:

- `Single<T>` -> `suspend () -> T`;
- `Maybe<T>` -> `suspend () -> T?` when absence is the only empty outcome;
- `Completable` -> `suspend () -> Unit`;
- `Observable<T>` / `Flowable<T>` -> `Flow<T>` with an explicitly chosen buffering policy;
- `switchMap` -> `flatMapLatest`, `concatMap` -> `flatMapConcat`.

The types are not mechanically equivalent. Rx disposal and coroutine cancellation propagate differently, Flow is cold by default, and backpressure strategies do not map one-to-one to Flow buffering. Review ownership and cancellation at every bridge.

Related topics: [Flow Basics](../coroutines-flow/flow-basics.md), [Flow Operators](../coroutines-flow/flow-operators.md), and [Coroutine Scopes & Cancellation](../coroutines-flow/scopes-cancellation.md).

References: [RxJava project and documentation](https://github.com/ReactiveX/RxJava), [ReactiveX operator reference](https://reactivex.io/documentation/operators.html).
