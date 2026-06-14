# RxJava

RxJava is a legacy reactive library for asynchronous streams, events and operator composition. In modern Android, many scenarios have moved to Coroutines and Flow, but RxJava is still common in production code.

## Operators

### `.map()` vs `.flatMap()`

`.map()` transforms each stream item into another item.

```kotlin
usersObservable
    .map { user -> user.name }
```

`.flatMap()` transforms each stream item into a new `Observable` / `Single` / another reactive source and then merges emissions into the outer stream.

```kotlin
userIdsObservable
    .flatMap { id -> api.getUser(id).toObservable() }
```

The main difference: `map` performs a synchronous value -> value transformation, while `flatMap` expands value -> stream and fits async-dependent operations.

Link: [RxJava Operator Map vs FlatMap](https://medium.com/mindorks/rxjava-operator-map-vs-flatmap-427c09678784)

**In short:** `map` transforms an item, `flatMap` starts a new reactive source for the item and merges the results.

### `.flatMap()`, `concatMap()`, `switchMap()`

`flatMap()` does not guarantee emission order from inner streams. After inner `Observable` instances are created, they run independently, and results can arrive in any order.

`concatMap()` preserves processing order according to the order of source items. But inner streams run sequentially, so the whole pipeline can become slower.

`concatMapEager()` starts inner streams in parallel, but emits results in the original order. This can require more memory because results need to be buffered.

`switchMap()` unsubscribes from the previous inner stream when a new one appears. A typical example is a search field: when the user enters a new query, the old query result is no longer needed.

Links:

- [RxJava FlatMap, SwitchMap and ConcatMap](https://medium.com/appunite-edu-collection/rxjava-flatmap-switchmap-and-concatmap-differences-examples-6d1f3ff88ee0)
- [flatMap vs concatMap vs concatMapEager](https://www.nurkiewicz.com/2017/08/flatmap-vs-concatmap-vs-concatmapeager.html)

**In short:** `flatMap` gives concurrency without order guarantees, `concatMap` preserves order sequentially, and `switchMap` keeps only the latest relevant inner stream.

### Difference between `observeOn()` and `subscribeOn()`

`subscribeOn()` defines the scheduler where subscription and upstream work closer to the source will run. Usually it does not matter where `subscribeOn()` is placed in the chain: if there are several, the one closer to source creation usually takes effect.

`observeOn()` switches the scheduler for downstream operators below it in the chain, until the next `observeOn()`.

```kotlin
api.loadUser()
    .subscribeOn(Schedulers.io())
    .map { it.toUiModel() }
    .observeOn(AndroidSchedulers.mainThread())
    .subscribe { uiModel -> render(uiModel) }
```

In Android, a typical pattern is: network/database work runs on `Schedulers.io()`, and UI update runs on `AndroidSchedulers.mainThread()`.

Link: [RxJava subscribeOn vs observeOn](https://medium.com/upday-devs/rxjava-subscribeon-vs-observeon-9af518ded53a)

**In short:** `subscribeOn()` affects upstream subscription/source work, while `observeOn()` switches the scheduler for further processing below it in the chain.

### ops: `from`, `just` - purpose and differences

`just()` creates a source that emits the passed argument as is. If several arguments are passed, they are emitted one by one, but the number of arguments is limited by overloads.

```kotlin
Observable.just("A", "B", "C")
```

`from...()` creates a source from another data type: `Iterable`, array, `Callable`, `Future`, `Publisher` and so on. For example, `fromIterable()` emits collection items one by one.

```kotlin
Observable.fromIterable(listOf("A", "B", "C"))
```

If a list is passed to `just(list)`, downstream receives one item: the list itself. If `fromIterable(list)` is used, downstream receives each list item separately.

Links:

- [Just](http://reactivex.io/documentation/operators/just.html)
- [From](http://reactivex.io/documentation/operators/from.html)

**In short:** `just()` emits arguments as values, while `fromIterable()` / `from...()` expands a container/source into emissions.

### ops: `doOn...Next`, `...Error`

`doOn...` operators allow running a side effect on different lifecycle events of a reactive chain without changing the emissions themselves.

Common options:

- `doOnNext()` - run an action before passing `onNext` downstream;
- `doAfterNext()` - run an action after passing `onNext`;
- `doOnComplete()` - run an action on successful completion;
- `doOnError()` - run an action on error;
- `doOnTerminate()` - run an action before termination, regardless of success/error;
- `doAfterTerminate()` - run an action after termination.

```kotlin
repository.observeItems()
    .doOnNext { items -> logger.log("items=${items.size}") }
    .doOnError { error -> logger.log(error) }
    .subscribe()
```

**Important:** `doOn...` is well suited for logging, metrics, debugging and lightweight side effects. Business logic should not be hidden in side-effect operators.

Link: [Do operator documentation](http://reactivex.io/documentation/operators/do.html)

**In short:** `doOn...` operators add side effects to stream lifecycle events without transforming data.

## Types and Backpressure

### `Observable` vs `Flowable`

`Observable` has no built-in backpressure strategy. If the producer emits items faster than the consumer can process them, memory problems or `MissingBackpressureException` are possible in places where backpressure is expected.

`Flowable` is designed for streams where backpressure matters: fast event sources, large data volumes, sensors, streams from a producer that can be faster than the consumer.

Backpressure is a situation where items are produced faster than downstream can process them.

Link: [RxJava 2 Flowable](https://www.baeldung.com/rxjava-2-flowable)

**In short:** `Observable` fits regular streams without backpressure, while `Flowable` is needed where a producer can overwhelm a consumer.

### `Flowable` - backpressure strategies

`Flowable` supports different backpressure strategies.

`Buffer` - events that cannot be processed in time go into a buffer. This fits cases where every event must be processed, but it is dangerous for infinite or too-fast streams.

`Drop` - events that cannot be processed in time are discarded. Example: sensor data where too high frequency is unnecessary.

`Latest` - only the latest relevant event is kept among those downstream cannot process in time.

`Error` - when backpressure appears, `MissingBackpressureException` is thrown. This fits cases where backpressure is unexpected and should be treated as an error.

`Missing` - no strategy is set at source level, and backpressure should be handled later in the chain.

Link: [RxJava 2 Flowable](https://www.baeldung.com/rxjava-2-flowable)

**In short:** backpressure strategy is chosen by stream semantics: process everything, drop extra items, keep the latest or fail explicitly.

### `Single`, `Completable`, `Maybe`

`Single<T>` emits exactly one item or an error. A good example is loading an object by id.

`Maybe<T>` emits one item, an error, or completes without a value. It fits search where the result may be absent.

`Completable` does not emit a value: it either completes successfully or with an error. It fits operations such as update/delete/save, where only completion matters.

```kotlin
fun loadUser(id: String): Single<User>
fun findCachedUser(id: String): Maybe<User>
fun updateUser(user: User): Completable
```

Link: [RxJava Single, Maybe and Completable](https://android.jlelse.eu/rxjava-single-maybe-and-completable-8686db42bac8)

**In short:** `Single` - one value, `Maybe` - value or empty, `Completable` - only success/error without value.

## More Operators

### ops: `defer`, `debounce`

`defer()` creates the source only at subscription time. Each subscriber gets a new "fresh" source.

```kotlin
val source = Observable.defer {
    Observable.just(System.currentTimeMillis())
}
```

`debounce()` waits for a specified interval after an emission. If a new value arrives during that time, the previous one is discarded and the timer starts again. When the pause is long enough, the latest value passes downstream.

A typical scenario is a search field:

```kotlin
queryChanges
    .debounce(300, TimeUnit.MILLISECONDS)
    .switchMap { query -> api.search(query).toObservable() }
```

**In short:** `defer` delays source creation until subscription, while `debounce` passes only the value after a pause in emissions.

### ops: `groupBy`, `combineLatest`, `withLatestFrom`, `switchOnNext`

`groupBy()` turns a stream of items into a stream of grouped streams. Each inner stream contains a subset of source items by key.

`combineLatest()` emits a result when any source stream emits a new value, using the latest values from the other sources. It starts working after each source has emitted at least one value.

`withLatestFrom()` is similar to `combineLatest`, but only the main source initiates emission. The second source value is taken as the latest context.

`switchOnNext()` works with a stream of streams: it subscribes to the latest inner `Observable` and unsubscribes from the previous one. As a result, downstream receives emissions only from the current inner stream.

```kotlin
Observable.combineLatest(user, settings) { userValue, settingsValue ->
    UiModel(userValue, settingsValue)
}
```

**In short:** `groupBy` groups a stream, `combineLatest` reacts to any source, `withLatestFrom` adds latest context, and `switchOnNext` switches to the latest inner stream.

### ops: `merge`, `concat`, `zip`

`merge()` combines emissions from several streams into one downstream stream without preserving order between sources.

`concat()` also combines streams, but runs them sequentially: first all emissions from the first source until completion, then the second, and so on.

`zip()` combines emissions pairwise: the first item of the first stream with the first item of the second, the second with the second, and so on.

```kotlin
Observable.zip(userSingle.toObservable(), settingsSingle.toObservable()) { user, settings ->
    UiModel(user, settings)
}
```

Links:

- [defer](http://reactivex.io/documentation/operators/defer.html)
- [groupBy](http://reactivex.io/documentation/operators/groupby.html)
- [debounce](http://reactivex.io/documentation/operators/debounce.html)
- [combineLatest](http://reactivex.io/documentation/operators/combinelatest.html)
- [merge](http://reactivex.io/documentation/operators/merge.html)
- [concat](http://reactivex.io/documentation/operators/concat.html)
- [zip](http://reactivex.io/documentation/operators/zip.html)

**In short:** `merge` mixes emissions, `concat` preserves sequential source execution, and `zip` combines emissions pairwise.
