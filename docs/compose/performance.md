# Compose Performance

Compose performance нужно анализировать по фазам: Composition, Layout и Drawing. Проблема может быть не только в recomposition, но и в дорогом layout, draw, allocations или main-thread work.

## Lazy layouts

### LazyColumn performance

`LazyColumn`, `LazyRow` и lazy grids эффективно compose-ят только видимые элементы и переиспользуют compositions, но performance всё равно зависит от identity элементов, стоимости item UI и организации state.

Для списков с insert/remove/reorder нужно задавать stable unique keys: `key = { item.id }`. Без keys Compose привязывает item state к позиции, поэтому при перемещении элементов можно потерять `remember` state и получить лишние recompositions.

Для списков с разными типами элементов полезен `contentType`. Он помогает Compose переиспользовать compositions только между элементами похожей структуры, а не пытаться переиспользовать item одного типа как item другого типа.

Item composable должен быть лёгким: не сортировать и не фильтровать большие коллекции внутри item, не делать I/O, не создавать тяжёлые объекты и не выполнять дорогой image/formatting work на каждую recomposition. Для больших или удалённых данных лучше использовать Paging.

**Коротко:** `LazyColumn` is lazy by rendering only visible items, but real performance depends on stable keys, lightweight item content, correct state ownership and avoiding heavy work during composition.

### Stable keys

Stable keys в lazy layouts - это стабильные уникальные identifiers, которые помогают Compose сохранить identity элемента при изменении dataset.

По умолчанию identity элемента фактически связана с его позицией. Это плохо для списков, где элементы добавляются, удаляются, сортируются или перемещаются: item state может "переехать" не туда, а Compose может сделать больше работы, чем нужно.

Правильный key должен быть стабильным для одного и того же logical item: database id, server id, UUID или другой устойчивый identifier. Index использовать опасно, если порядок списка может меняться.

Если внутри item используется `rememberSaveable`, key должен быть совместим с `Bundle`, например primitive, enum или `Parcelable`, чтобы state мог восстановиться после recreation или после ухода item за пределы viewport.

**Коротко:** stable keys keep item identity across list changes, preserving item state and helping Compose avoid unnecessary recomposition.

## Performance pitfalls

### Heavy work inside composable

Composable body может выполняться много раз, быть skipped или перезапускаться при изменении state. Поэтому тяжёлая работа внутри composable быстро превращается в performance problem.

Типичные ошибки: сортировать/фильтровать большой список прямо в composable, парсить данные, создавать formatter на каждую recomposition, выполнять I/O, синхронно декодировать bitmap, делать сложные вычисления или запускать side effects прямо из body.

Лучше подготовить данные заранее во `ViewModel` / domain layer и передать в UI готовую UI model. Если локальное вычисление действительно относится к UI и зависит от конкретных inputs, его можно кэшировать через `remember(inputs)`, но `remember` не должен прятать business logic.

Для suspend work и callback/subscription API нужны controlled side effects: `LaunchedEffect`, `produceState` или `DisposableEffect`, а не прямой запуск работы из composable body.

**Коротко:** composables should describe UI, not perform heavy work; move expensive work out of composition or cache it with the right keys.

### Compose UI performance pitfalls

Частые pitfalls: читать часто меняющийся state слишком высоко в дереве, передавать mutable/unstable models, забывать stable keys в lazy lists, делать heavy work в composable, создавать лишние allocations, запускать side effects в body, использовать nested scroll/lazy layouts без ограничений размера, делать backwards writes и обновлять state после того, как он уже был прочитан в composition.

`derivedStateOf` полезен, когда input state меняется часто, а UI должен обновляться только при изменении derived result. Но он не нужен для обычных дешёвых вычислений, которые должны обновляться так же часто, как inputs.

Оптимизировать нужно после измерений: debug build может искажать картину. Лучше смотреть release/R8 build, Layout Inspector, recomposition highlights/counters, Android Profiler, tracing/Perfetto, Macrobenchmark и реальные user scenarios.

**Коротко:** Compose performance is not about avoiding recomposition blindly; it is about measuring the bottleneck and reducing unnecessary work in composition, layout, drawing and the main thread.
