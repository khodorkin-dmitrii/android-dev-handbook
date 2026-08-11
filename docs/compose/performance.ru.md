# Compose Performance

Производительность Compose - это не только recomposition. Медленный кадр может быть связан с composition, layout, drawing, allocations, image loading или другой работой на main thread.

Цель не в том, чтобы убрать каждую recomposition. Нужно измерить bottleneck и уменьшить лишнюю работу именно в той фазе, которая реально тормозит.

## Сначала измеряйте

Не оптимизируйте Compose performance только по debug build. Debug-сборки и инструменты могут искажать recomposition и frame timings.

Предпочтительны:

- release или release-like builds;
- реальные устройства с реалистичными данными;
- Layout Inspector и recomposition counters для локальной диагностики;
- System Trace / Perfetto для анализа работы кадра;
- Macrobenchmark для startup, scroll и navigation scenarios.

Практичный порядок диагностики:

1. Воспроизвести медленный экран или interaction.
2. Понять, где затраты: composition, layout, drawing, allocations, image loading или main-thread work.
3. Сделать одно сфокусированное изменение.
4. Повторить измерение на том же сценарии.

## Lazy layouts

### LazyColumn performance

`LazyColumn`, `LazyRow` и lazy grids compose-ят только видимые элементы и ближайший контент, но performance всё равно зависит от identity элементов, стоимости item и организации state.

Для списков с insert, remove, reorder или sorting используйте stable unique keys:

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

Без keys identity элемента в основном привязана к позиции. После reorder remembered state может оказаться у другого logical item, а Compose может сделать больше работы, чем нужно.

Для списков с разными типами элементов задавайте `contentType`:

```kotlin
items(
    items = feedItems,
    key = { item -> item.id },
    contentType = { item -> item.type },
) { item ->
    FeedRow(item)
}
```

`contentType` помогает Compose переиспользовать compositions только между структурно похожими rows.

Item content должен быть лёгким. Не сортируйте и не фильтруйте всю коллекцию внутри item, не выполняйте I/O, не декодируйте bitmaps синхронно и не создавайте дорогие formatter-объекты на каждую recomposition. Для больших или удалённых datasets лучше использовать Paging.

### Stable keys

Правильный key должен быть стабильным для одного logical item: database id, server id, UUID или другой persistent identifier. Не используйте текущий index, если порядок списка может меняться.

Если внутри item используется `rememberSaveable`, key должен быть совместим с Android saved state, например primitive, `String`, enum или `Parcelable`.

## Performance pitfalls

### Heavy work inside a composable

Composable body может выполняться много раз. Дорогая работа внутри него быстро становится performance problem:

```kotlin
@Composable
fun UsersScreen(users: List<User>) {
    val sortedUsers = users.sortedBy(User::name) // Не повторяем это в UI без причины
    UsersList(sortedUsers)
}
```

Долгоживущие UI-данные лучше готовить во `ViewModel` или domain layer. Если небольшое UI-only вычисление действительно принадлежит UI, его можно закэшировать с правильными keys:

```kotlin
val sortedUsers = remember(users) {
    users.sortedBy(User::name)
}
```

`remember` - это composition cache, а не место для business logic, I/O или дорогой подготовки данных.

Side effects тоже не должны запускаться напрямую из composable body. Используйте `LaunchedEffect`, `produceState` или `DisposableEffect`, когда работа должна быть привязана к Composition.

### Часто меняющийся state

Если читать fast-changing state слишком высоко в дереве, можно invalidated больше UI, чем нужно. Держите чтение state ближе к месту, где значение реально используется.

Для значений, которые нужны только на layout или drawing phase, lambda-based modifiers иногда позволяют отложить чтение на более позднюю фазу:

```kotlin
Modifier.offset {
    IntOffset(x = 0, y = scrollOffset())
}
```

Используйте это только когда profiling показывает, что чтение state создаёт лишнюю composition work.

### `derivedStateOf`

`derivedStateOf` полезен, когда input state меняется часто, а UI должен обновиться только при изменении derived result:

```kotlin
val showScrollToTop by remember {
    derivedStateOf {
        listState.firstVisibleItemIndex > 0
    }
}
```

Не оборачивайте каждое вычисление в `derivedStateOf`. Для дешёвых значений, которые должны обновляться при изменении inputs, прямое вычисление проще и часто лучше.

### Stability и backwards writes

Stable immutable UI models помогают Compose пропускать лишнюю работу, но stability annotations - это contracts. Не добавляйте `@Stable` или `@Immutable` только ради исчезновения warning.

Избегайте backwards writes: обновления state после его чтения в том же composition path. Это может постоянно планировать recomposition или создать бесконечный loop.

```kotlin
@Composable
fun BadCounter() {
    var count by remember { mutableIntStateOf(0) }

    Text("Count: $count")
    count++ // Неправильно
}
```

State должен меняться из user events, effects, ViewModel или другого явного state owner.

## Частые ошибки

- Считать каждую recomposition багом.
- Измерять только debug builds.
- Читать часто меняющийся state слишком высоко в UI tree.
- Делать sorting, parsing, I/O или bitmap decoding во время composition.
- Использовать list index как key для reorderable data.
- Передавать mutable models, изменения которых Compose не наблюдает.
- Добавлять `remember`, `derivedStateOf` или stability annotations без измеренной причины.
- Оптимизировать composition, когда реальная проблема в layout, drawing, image loading или main-thread work.

## Связанные темы

- [State & Recomposition](state-recomposition.md)
- [Side Effects](side-effects.md)
- [Performance Profiling and Benchmarking](../tools/performance-profiling.md)
- [Android Performance & Memory](../android/performance-memory.md)
