# Compose Performance

Compose performance is not only about recomposition. A slow frame can be caused by composition, layout, drawing, allocations, image loading, or other main-thread work.

The goal is not to avoid every recomposition. The goal is to measure the bottleneck and reduce unnecessary work in the phase that is actually slow.

## Measure first

Do not optimize Compose performance only from a debug build. Debug builds and tooling can distort recomposition and frame timings.

Prefer:

- release or release-like builds;
- real devices with realistic data;
- Layout Inspector and recomposition counters for local investigation;
- System Trace / Perfetto for frame work;
- Macrobenchmark for startup, scroll and navigation scenarios.

A useful investigation order:

1. Reproduce the slow screen or interaction.
2. Check whether the cost is composition, layout, drawing, allocation, image loading or main-thread work.
3. Make one focused change.
4. Measure the same scenario again.

## Lazy layouts

### LazyColumn performance

`LazyColumn`, `LazyRow` and lazy grids compose only visible items and nearby content, but performance still depends on item identity, item cost and state organization.

For lists with insert, remove, reorder or sorting, use stable unique keys:

```kotlin
LazyColumn {
    items(
        items = messages,
        key = { message -> message.id },
    ) { message ->
        MessageRow(message)
    }
}
```

Without keys, item identity is tied mostly to position. After a reorder, remembered state may move to the wrong logical item and Compose may do more work than needed.

For lists with different item types, provide `contentType`:

```kotlin
items(
    items = feedItems,
    key = { item -> item.id },
    contentType = { item -> item.type },
) { item ->
    FeedRow(item)
}
```

`contentType` helps Compose reuse compositions only between structurally similar rows.

Keep item content lightweight. Do not sort or filter the whole collection inside an item, perform I/O, decode bitmaps synchronously, or create expensive formatters on every recomposition. For large or remote datasets, prefer Paging.

### Stable keys

A correct key should be stable for the same logical item: database id, server id, UUID or another persistent identifier. Avoid using the current index when list order can change.

If `rememberSaveable` is used inside an item, the key must be compatible with Android saved state, for example a primitive, `String`, enum or `Parcelable`.

## Performance pitfalls

### Heavy work inside a composable

A composable body can run many times. Expensive work inside it quickly becomes a performance problem:

```kotlin
@Composable
fun UsersScreen(users: List<User>) {
    val sortedUsers = users.sortedBy(User::name) // Avoid repeated work here
    UsersList(sortedUsers)
}
```

Prefer preparing durable UI data in `ViewModel` or the domain layer. If a small UI-only calculation really belongs in UI, cache it with correct keys:

```kotlin
val sortedUsers = remember(users) {
    users.sortedBy(User::name)
}
```

`remember` is a composition cache, not a place to hide business logic, I/O or expensive data preparation.

Side effects should also not start directly from the composable body. Use `LaunchedEffect`, `produceState` or `DisposableEffect` when work must be tied to Composition.

### Frequently changing state

Reading fast-changing state too high in the tree can invalidate more UI than necessary. Keep state reads close to the place where the value is used.

For values used only by layout or drawing, lambda-based modifiers can sometimes defer the read to a later phase:

```kotlin
Modifier.offset {
    IntOffset(x = 0, y = scrollOffset())
}
```

Use this only when profiling shows that the state read causes unnecessary composition work.

### `derivedStateOf`

`derivedStateOf` is useful when input state changes often, but the UI should update only when the derived result changes:

```kotlin
val showScrollToTop by remember {
    derivedStateOf {
        listState.firstVisibleItemIndex > 0
    }
}
```

Do not wrap every calculation in `derivedStateOf`. For cheap values that should update whenever inputs change, direct calculation is simpler and often better.

### Stability and backwards writes

Stable immutable UI models help Compose skip unnecessary work, but stability annotations are contracts. Do not add `@Stable` or `@Immutable` just to silence tooling.

Avoid backwards writes: updating state after reading it in the same composition path. This can schedule repeated recompositions or create an endless loop.

```kotlin
@Composable
fun BadCounter() {
    var count by remember { mutableIntStateOf(0) }

    Text("Count: $count")
    count++ // Wrong
}
```

State should change from user events, effects, ViewModel, or another explicit state owner.

## Common mistakes

- Treating every recomposition as a bug.
- Measuring only debug builds.
- Reading frequently changing state too high in the UI tree.
- Doing sorting, parsing, I/O or bitmap decoding during composition.
- Using list indexes as keys for reorderable data.
- Passing mutable models whose changes Compose cannot observe.
- Adding `remember`, `derivedStateOf` or stability annotations without a measured reason.
- Optimizing composition while the real problem is layout, drawing, image loading or main-thread work.

## Related topics

- [State & Recomposition](state-recomposition.md)
- [Side Effects](side-effects.md)
- [Performance Profiling and Benchmarking](../tools/performance-profiling.md)
- [Android Performance & Memory](../android/performance-memory.md)
