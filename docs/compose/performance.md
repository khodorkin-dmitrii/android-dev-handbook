# Compose Performance

Compose performance should be analyzed by phases: Composition, Layout and Drawing. The problem may be not only recomposition, but also expensive layout, draw, allocations or main-thread work.

## Lazy layouts

### LazyColumn performance

`LazyColumn`, `LazyRow` and lazy grids efficiently compose only visible items and reuse compositions, but performance still depends on item identity, item UI cost and state organization.

For lists with insert/remove/reorder, set stable unique keys: `key = { item.id }`. Without keys, Compose ties item state to position, so moving items can lose `remember` state and cause unnecessary recompositions.

For lists with different item types, `contentType` is useful. It helps Compose reuse compositions only between items with similar structure, instead of trying to reuse an item of one type as an item of another type.

Item composable should be lightweight: do not sort or filter large collections inside an item, do not do I/O, do not create heavy objects and do not perform expensive image/formatting work on every recomposition. For large or remote data, prefer Paging.

**In short:** `LazyColumn` is lazy by rendering only visible items, but real performance depends on stable keys, lightweight item content, correct state ownership and avoiding heavy work during composition.

### Stable keys

Stable keys in lazy layouts are stable unique identifiers that help Compose preserve item identity when the dataset changes.

By default, item identity is effectively tied to its position. This is bad for lists where items are added, removed, sorted or moved: item state can "move" to the wrong item, and Compose can do more work than needed.

A correct key should be stable for the same logical item: database id, server id, UUID or another persistent identifier. Using index is dangerous if list order can change.

If `rememberSaveable` is used inside an item, the key must be compatible with `Bundle`, for example primitive, enum or `Parcelable`, so state can be restored after recreation or after the item leaves the viewport.

**In short:** stable keys keep item identity across list changes, preserving item state and helping Compose avoid unnecessary recomposition.

## Performance pitfalls

### Heavy work inside a composable

Composable body can run many times, be skipped or restart when state changes. Therefore heavy work inside a composable quickly becomes a performance problem.

Typical mistakes: sorting/filtering a large list directly in a composable, parsing data, creating a formatter on every recomposition, doing I/O, synchronously decoding bitmap, performing complex calculations or launching side effects directly from the body.

It is better to prepare data ahead of time in `ViewModel` / domain layer and pass a ready UI model to UI. If a local calculation truly belongs to UI and depends on specific inputs, it can be cached with `remember(inputs)`, but `remember` should not hide business logic.

Suspend work and callback/subscription APIs need controlled side effects: `LaunchedEffect`, `produceState` or `DisposableEffect`, not direct work launch from the composable body.

**In short:** composables should describe UI, not perform heavy work; move expensive work out of composition or cache it with the right keys.

### Compose UI performance pitfalls

Common pitfalls: reading frequently changing state too high in the tree, passing mutable/unstable models, forgetting stable keys in lazy lists, doing heavy work in a composable, creating unnecessary allocations, launching side effects in the body, using nested scroll/lazy layouts without size constraints, doing backwards writes and updating state after it has already been read in composition.

`derivedStateOf` is useful when input state changes often, but UI should update only when the derived result changes. But it is not needed for ordinary cheap calculations that should update as often as inputs.

Optimize after measurement: debug build can distort the picture. Prefer release/R8 build, Layout Inspector, recomposition highlights/counters, Android Profiler, tracing/Perfetto, Macrobenchmark and real user scenarios.

**In short:** Compose performance is not about avoiding recomposition blindly; it is about measuring the bottleneck and reducing unnecessary work in composition, layout, drawing and the main thread.
