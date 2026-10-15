# Layouts и контейнеры Compose

Layouts в Compose измеряют дочерние элементы с учётом constraints, полученных от parent, а затем размещают их. Выбирайте самый простой стандартный layout, который ясно выражает структуру UI, и переходите к собственному алгоритму только тогда, когда обычной композиции недостаточно.

Основные API из этой статьи не помечены как experimental в актуальной официальной Android reference. У соседних overloads и вспомогательных API статус может отличаться, поэтому для используемой в проекте версии Compose нужно учитывать требуемый compiler opt-in и сверяться с reference.

## Быстрый выбор

| Задача | Что выбрать | Важная особенность |
| --- | --- | --- |
| Одна горизонтальная или вертикальная последовательность | `Row`, `Column` | Сразу compose-ят всех детей и сами по себе не прокручиваются |
| Наложение элементов или выравнивание внутри одной области | `Box` | `align` и `matchParentSize` для отдельного ребёнка доступны только в `BoxScope` |
| Выбор контента по constraints родителя | `BoxWithConstraints` | Учитывает доступное от parent пространство, а не физический размер экрана |
| Перенос небольшого набора на несколько строк | `FlowRow`, `FlowColumn` | Выполняют перенос eagerly и не являются lazy |
| Большая или динамическая одномерная коллекция | `LazyColumn`, `LazyRow` | Compose-ят и размещают видимые элементы и ближайший контент |
| Регулярная сетка по строкам или столбцам | `LazyVerticalGrid`, `LazyHorizontalGrid` | Поддерживает фиксированные и адаптивные ячейки, а также spans |
| Masonry-сетка с элементами разного размера | `LazyVerticalStaggeredGrid`, `LazyHorizontalStaggeredGrid` | Заполняет lanes независимо, без общих границ строк или столбцов |
| Перелистывание страниц со snap-поведением | `HorizontalPager`, `VerticalPager` | Страницы compose-ятся lazily и управляются через `PagerState` |
| Material-структура экрана | `Scaffold` | Предоставляет slots и передаёт `innerPadding` основному контенту |
| Material-контейнер для представления | `Surface`, `Card` | Задают shape, color, elevation и interaction semantics, а не универсальный алгоритм размещения |
| Связи между соседними элементами | Сначала стандартные layouts, затем `ConstraintLayout` | Для производительности Compose не требуется плоская иерархия |
| Действительно новый алгоритм измерения и размещения | `Layout` | Нужен, когда стандартные layouts и modifiers не выражают алгоритм достаточно ясно |

## Базовые layouts: Row, Column и Box

### Row и Column

`Row` размещает дочерние элементы по горизонтальной main axis. У `Column` main axis вертикальная. Они подходят для небольших заранее известных наборов: toolbar, секции формы или группы действий.

`arrangement` распределяет элементы по main axis, а `alignment` выравнивает их по cross axis:

- `Row` использует `horizontalArrangement` и `verticalAlignment`.
- `Column` использует `verticalArrangement` и `horizontalAlignment`.
- `Arrangement.spacedBy(...)` добавляет интервалы без отдельного padding у каждого ребёнка.

Некоторые modifiers зависят от scope. `Modifier.weight()` доступен в `RowScope` и `ColumnScope` и распределяет оставшееся место по main axis между элементами с weight. `Modifier.align()` переопределяет выравнивание parent по cross axis для одного ребёнка. Это не универсальные modifiers: например, прямой item в `LazyColumn` не получает `RowScope.weight()`, пока внутри этого item не создан `Row`.

```kotlin
Row(
    verticalAlignment = Alignment.CenterVertically,
    horizontalArrangement = Arrangement.spacedBy(12.dp)
) {
    Icon(Icons.Default.Info, contentDescription = null)
    Text("A message that uses the remaining width", Modifier.weight(1f))
    Button(onClick = onRetry) { Text("Retry") }
}
```

### Box

`Box` размещает дочерние элементы в одной области и позволяет накладывать их друг на друга. Типичные сценарии - badge поверх иконки, loading state поверх контента или элемент в углу контейнера. `contentAlignment` задаёт общее выравнивание, а `Modifier.align()` переопределяет его для конкретного ребёнка внутри `BoxScope`.

`Modifier.matchParentSize()` также относится к `BoxScope`. Он растягивает ребёнка до итогового размера `Box`, но этот ребёнок не влияет на измерение самого `Box`. Этим он отличается от `fillMaxSize()`, который участвует в measurement и может заставить parent занять всё доступное пространство.

```kotlin
Box {
    ContentCard()
    Box(
        Modifier
            .matchParentSize()
            .background(Color.Black.copy(alpha = 0.2f))
    )
    CircularProgressIndicator(Modifier.align(Alignment.Center))
}
```

### Прокрутка: обычные и lazy layouts

`Row`, `Column` и `Box` сами по себе не прокручиваются. `Column` с `verticalScroll()` или `Row` с `horizontalScroll()` сначала compose-ит всех детей, а затем делает результат прокручиваемым. Это подходит для небольшого ограниченного объёма контента, например формы настроек. Для большой, динамической или потенциально неограниченной коллекции используйте lazy layout, чтобы не compose-ить сразу все элементы вне экрана.

Не помещайте scrollable child без ограниченного размера внутрь scrollable parent по той же оси. Например, `LazyColumn` без заданной высоты внутри `Column.verticalScroll()` получает бесконечную максимальную высоту и выбрасывает исключение. Обычно лучше использовать один parent `LazyColumn` с блоками `item` и `items`. Вложенная прокрутка по разным осям допустима, как и прокрутка по одной оси, если размер дочернего контейнера явно ограничен.

## Layout с учётом constraints: BoxWithConstraints

`BoxWithConstraints` предоставляет `minWidth`, `maxWidth`, `minHeight` и `maxHeight` из constraints, переданных его parent. Он нужен, когда при локальном пороге ширины или высоты должна меняться сама структура контента.

Эти значения описывают доступное место в конкретной точке иерархии, а не размер экрана устройства. Pane, dialog или вложенный компонент может получить намного меньше места, чем window, а parent без ограничения по одной из осей может передать бесконечный максимум. Для адаптивных решений уровня всего приложения обычно лучше подходят window size classes, а `BoxWithConstraints` - для локальных решений layout.

```kotlin
BoxWithConstraints {
    if (maxWidth < 600.dp) {
        CompactContent()
    } else {
        TwoPaneContent()
    }
}
```

## Перенос элементов: FlowRow и FlowColumn

`FlowRow` размещает элементы горизонтально и переносит их на новые строки. `FlowColumn` размещает их вертикально и продолжает в новых столбцах. Они подходят для chips, tags, filters и других небольших групп с элементами разного размера.

Оба layout поддерживают arrangements, выравнивание по cross axis, интервалы и ограничения вроде `maxItemsInEachRow` или `maxItemsInEachColumn`. Weight рассчитывается в пределах отдельной строки или столбца flow, а не всего контейнера.

Flow layouts не являются lazy: все дочерние элементы compose-ятся и измеряются. Они подходят для небольших и средних ограниченных наборов, но не для ленты произвольного размера. Для большой прокручиваемой коллекции выбирайте lazy list или grid.

## Lazy lists: LazyColumn и LazyRow

`LazyColumn` - стандартный вертикальный прокручиваемый список, а `LazyRow` - его горизонтальный вариант. Они compose-ят и размещают только видимые items и ближайший контент, поэтому подходят для feeds, истории сообщений, каруселей и больших наборов данных.

DSL поддерживает отдельные блоки `item` и ориентированные на коллекции блоки `items`, а `contentPadding`, `Arrangement` и `LazyListState` управляют отступами, интервалами и состоянием прокрутки. Подробности про stable `key`, `contentType`, размеры placeholders и измерение производительности находятся в статье [Compose Performance](performance.md).

Выбирайте scrollable `Column` или `Row`, когда детей немного и весь контент должен участвовать в composition сразу. Используйте lazy list, когда коллекция большая, меняется со временем, загружается через paging или не должна compose-ить контент вне экрана.

## Lazy grids: LazyVerticalGrid и LazyHorizontalGrid

`LazyVerticalGrid` прокручивается вертикально и делит ширину на столбцы. `LazyHorizontalGrid` прокручивается горизонтально и делит высоту на строки. Они подходят для коллекций, ячейки которых должны следовать общей сетке, например galleries, dashboards или catalogs.

- `GridCells.Fixed(count)` сохраняет фиксированное число столбцов или строк и делит между ними доступное место по cross axis.
- `GridCells.Adaptive(minSize)` создаёт столько ячеек, сколько помещается при заданном минимальном размере, а оставшееся место распределяет между ними.
- Через `span` item может занять несколько ячеек. `GridItemSpan(maxLineSpan)` удобен для заголовка на всю ширину adaptive grid, когда точное число столбцов заранее неизвестно.

```kotlin
LazyVerticalGrid(columns = GridCells.Adaptive(minSize = 160.dp)) {
    item(span = { GridItemSpan(maxLineSpan) }) {
        SectionHeader()
    }
    items(products) { product ->
        ProductCard(product)
    }
}
```

## Staggered grids

`LazyVerticalStaggeredGrid` и `LazyHorizontalStaggeredGrid` - lazy layouts в стиле masonry для элементов с разными размерами, например фотографий с разным aspect ratio. Для определения lanes они используют `StaggeredGridCells.Fixed` или `StaggeredGridCells.Adaptive`.

В обычной lazy grid элементы выравниваются по общим границам строк или столбцов, поэтому размер линии обычно задаёт самый высокий элемент. Staggered grid заполняет lanes независимо и помещает следующие items в свободное место, создавая более плотный, но менее регулярный визуальный порядок. Используйте обычную grid, когда важно выравнивание, и staggered grid, когда важнее переменный размер элементов и плотное использование пространства.

## Pagers: HorizontalPager и VerticalPager

`HorizontalPager` и `VerticalPager` показывают контент как отдельные страницы со snap-поведением. Типичные сценарии - onboarding, media gallery и полноэкранные секции. Страницы compose-ятся lazily, а `PagerState` предоставляет current, settled и target pages и позволяет программно управлять прокруткой.

Pager не заменяет свободно прокручиваемый список: он нужен, когда границы страниц являются частью взаимодействия. `pageSize`, `contentPadding`, `pageSpacing` и fling behavior позволяют настроить поведение, а по умолчанию страница заполняет viewport вдоль оси прокрутки.

## Material-компоненты: Scaffold, Surface и Card

### Scaffold

`Scaffold` координирует стандартные slots Material-экрана: `topBar`, `bottomBar`, `floatingActionButton`, `snackbarHost` и основной body. Он не добавляет нужные отступы в body автоматически. Content lambda получает `innerPadding`, который нужно применить к корневому контейнеру body, чтобы bars не перекрывали контент.

```kotlin
Scaffold(
    topBar = { TopAppBar(title = { Text("Library") }) }
) { innerPadding ->
    LazyColumn(
        modifier = Modifier.padding(innerPadding)
    ) {
        items(books) { BookRow(it) }
    }
}
```

Применяйте padding на правильной границе body и не учитывайте одни и те же system или bar insets дважды. При вложенных scaffolds или edge-to-edge контенте владелец каждого inset должен быть определён явно.

### Surface и Card

`Surface` создаёт Material surface: clipping по shape, background и content colors, border, tonal elevation, shadow и при необходимости interaction semantics. `Card` - более специализированный Material-контейнер для связанной единицы контента с filled, elevated и outlined вариантами.

Их основная задача - Material-представление, а не произвольное размещение детей. Если контенту нужен алгоритм размещения, добавьте внутрь `Row`, `Column`, `Box` или другой подходящий layout. `Card` не заменяет grid или list.

## Сложное и собственное размещение

### ConstraintLayout

Compose `ConstraintLayout` размещает composables через связи с parent, соседними элементами, guidelines и barriers. Он может быть полезен, когда множество связей по разным осям проще выразить constraints или когда дизайн естественно описывается через constraint set.

В отличие от View system, Compose не требует плоской иерархии ради экономии на измерении вложенных `ViewGroup`. Поэтому `ConstraintLayout` не обязателен для сложного экрана и не становится автоматически быстрее вложенных стандартных layouts. Предпочитайте `Row`, `Column`, `Box` и modifiers, если они ясно описывают дизайн. Используйте `ConstraintLayout`, когда его модель связей делает код понятнее и удобнее в поддержке.

### Собственный Layout

Composable `Layout` даёт прямой контроль над измерением детей, выбором размера контейнера и размещением каждого ребёнка. Он подходит для действительно нестандартной геометрии, согласованного размещения, которое нельзя выразить обычными layouts, или переиспользуемого алгоритма с понятными инвариантами.

Начинайте со стандартных layouts и custom modifiers. Их легче читать, тестировать и согласовывать с intrinsic measurement и accessibility expectations. Переходите к `Layout`, когда обычная композиция приводит к неестественным обходным решениям или не может реализовать нужное поведение measure-and-place. В рамках одного layout pass ребёнка обычно следует измерять только один раз, а результат должен соблюдать constraints от parent.

`SubcomposeLayout` - специализированный низкоуровневый инструмент, который позволяет compose-ить контент во время measurement. Он нужен, когда последующий контент зависит от измеренных constraints или размера ранее измеренного контента, и лежит в основе constraints-aware и lazy-паттернов. Он повышает сложность и стоимость, поэтому не должен быть решением по умолчанию для обычного custom placement.

## Связанные темы

- [Compose Basics](basics.md)
- [Compose Performance](performance.md)
- [State & Recomposition](state-recomposition.md)
- [Официальная документация по основам Compose layouts](https://developer.android.com/develop/ui/compose/layouts/basics)
- [Официальная документация по lazy lists и grids](https://developer.android.com/develop/ui/compose/lists)
- [Официальная документация по custom layouts](https://developer.android.com/develop/ui/compose/layouts/custom)
