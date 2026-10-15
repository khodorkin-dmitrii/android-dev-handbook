# Compose Layouts & Containers

Compose layouts measure children under constraints received from their parent and then place them. Choose the smallest standard layout that expresses the UI clearly; move to a custom algorithm only when standard composition is no longer enough.

The core APIs covered here are not marked experimental in the current official Android reference. Nearby overloads and helper APIs can have a different status, so check the compiler opt-in requirement and the reference for the Compose version used by the project.

## Quick choice

| Need | Prefer | Important detail |
| --- | --- | --- |
| One horizontal or vertical sequence | `Row`, `Column` | Eagerly composes all children and does not scroll by itself |
| Overlap, overlay or alignment inside one area | `Box` | Child-specific `align` and `matchParentSize` are available only in `BoxScope` |
| Choose content from parent constraints | `BoxWithConstraints` | Reads the space offered by the parent, not the physical screen size |
| Wrap a small set onto multiple lines | `FlowRow`, `FlowColumn` | Wraps eagerly and is not lazy |
| Large or dynamic one-dimensional collection | `LazyColumn`, `LazyRow` | Composes and lays out visible items plus nearby content |
| Uniform row or column grid | `LazyVerticalGrid`, `LazyHorizontalGrid` | Supports fixed or adaptive cells and item spans |
| Masonry-style content with uneven item sizes | `LazyVerticalStaggeredGrid`, `LazyHorizontalStaggeredGrid` | Fills lanes independently, so rows or columns do not share regular boundaries |
| Swipe between pages with snapping | `HorizontalPager`, `VerticalPager` | Pages are composed lazily and controlled through `PagerState` |
| Material screen structure | `Scaffold` | Provides slots and passes `innerPadding` to the body |
| Material visual container | `Surface`, `Card` | Provides shape, color, elevation and interaction semantics, not a general layout algorithm |
| Relationships between siblings | Standard layouts first, then `ConstraintLayout` | Compose does not require a flat hierarchy for good performance |
| A genuinely new measure-and-place rule | `Layout` | Use when standard layouts and modifiers cannot express the algorithm clearly |

## Basic layouts: Row, Column and Box

### Row and Column

`Row` places children along the horizontal main axis. `Column` uses the vertical main axis. They are a good fit for compact, known sets such as a toolbar, form section or group of actions.

`arrangement` distributes children along the main axis, while `alignment` positions them on the cross axis:

- `Row` uses `horizontalArrangement` and `verticalAlignment`.
- `Column` uses `verticalArrangement` and `horizontalAlignment`.
- `Arrangement.spacedBy(...)` adds spacing without putting padding into every child.

Some modifiers are scope-specific. `Modifier.weight()` is available in `RowScope` and `ColumnScope` and distributes the remaining main-axis space among weighted siblings. `Modifier.align()` overrides the parent's cross-axis alignment for one child. These APIs are not universal modifiers: for example, a direct item of `LazyColumn` does not gain `RowScope.weight()` unless that item contains a `Row`.

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

`Box` places children in the same area and can overlap them. Typical uses are a badge over an icon, loading state over content, or an element anchored to a corner. `contentAlignment` defines the default for children; `Modifier.align()` overrides it for one child inside `BoxScope`.

`Modifier.matchParentSize()` is also a `BoxScope` modifier. It makes a child match the final size chosen for the `Box` without that child influencing the `Box` measurement. This differs from `fillMaxSize()`, which participates in measurement and can make the parent occupy all available space.

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

### Scrolling: regular versus lazy layouts

`Row`, `Column` and `Box` do not scroll on their own. A `Column` with `verticalScroll()` or a `Row` with `horizontalScroll()` composes all children, then makes the result scrollable. This is appropriate for a small, bounded amount of content such as a settings form. Use a lazy layout for a large, dynamic or potentially unbounded collection so off-screen items are not all composed initially.

Avoid putting an unbounded scrollable child inside a scrollable parent on the same axis. For example, a `LazyColumn` without a fixed height inside `Column.verticalScroll()` receives an infinite maximum height and throws an exception. Prefer one parent `LazyColumn` with `item` and `items` blocks. Nesting on different axes is valid, and same-axis nesting can be valid when the child has an explicit bounded size.

## Constraints-aware layout: BoxWithConstraints

`BoxWithConstraints` exposes `minWidth`, `maxWidth`, `minHeight` and `maxHeight` from the constraints supplied by its parent. Use it when the content structure itself must change at a local width or height threshold.

These values describe the available space at this point in the hierarchy, not the device screen. A pane, dialog or nested component may receive much less space than the window, while an unbounded parent may provide an infinite maximum on one axis. For app-wide adaptive decisions, window size classes are usually a better source; use `BoxWithConstraints` for local layout decisions.

```kotlin
BoxWithConstraints {
    if (maxWidth < 600.dp) {
        CompactContent()
    } else {
        TwoPaneContent()
    }
}
```

## Wrapping items: FlowRow and FlowColumn

`FlowRow` places children horizontally and wraps them onto new rows. `FlowColumn` places them vertically and continues in new columns. They fit chips, tags, filters and other small groups whose elements have varying sizes.

Both support arrangements, cross-axis alignment, spacing and limits such as `maxItemsInEachRow` or `maxItemsInEachColumn`. Weight is resolved within a row or column of the flow rather than across the entire container.

Flow layouts are not lazy: all children are composed and measured. They are suitable for small and medium bounded sets, not an arbitrarily large feed. For a large scrollable collection, choose a lazy list or grid.

## Lazy lists: LazyColumn and LazyRow

`LazyColumn` is the standard vertically scrolling list; `LazyRow` is its horizontal counterpart. They compose and lay out only the visible items and nearby content, making them appropriate for feeds, message histories, carousels and large datasets.

Their DSL supports individual `item` blocks and collection-oriented `items` blocks, while `contentPadding`, `Arrangement` and `LazyListState` control insets, spacing and scroll state. Details such as stable `key`, `contentType`, placeholder sizing and performance measurement belong in [Compose Performance](performance.md).

Choose a scrollable `Column` or `Row` when the child count is small and all content should participate in composition together. Choose a lazy list when the collection is large, changes over time, uses paging or should avoid composing off-screen content.

## Lazy grids: LazyVerticalGrid and LazyHorizontalGrid

`LazyVerticalGrid` scrolls vertically and divides its width into columns. `LazyHorizontalGrid` scrolls horizontally and divides its height into rows. Use them for collections whose cells should follow shared grid lines, such as galleries, dashboards or catalogs.

- `GridCells.Fixed(count)` keeps a fixed number of columns or rows and divides the available cross-axis space among them.
- `GridCells.Adaptive(minSize)` creates as many cells as fit while keeping each at least the requested size; remaining space is distributed among the cells.
- An item `span` can occupy multiple cells. `GridItemSpan(maxLineSpan)` is useful for a full-width header in an adaptive grid where the exact column count is not known in advance.

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

`LazyVerticalStaggeredGrid` and `LazyHorizontalStaggeredGrid` are lazy masonry-style layouts for items with uneven dimensions, such as photos with different aspect ratios. They use `StaggeredGridCells.Fixed` or `StaggeredGridCells.Adaptive` to define lanes.

A regular lazy grid aligns items to shared row or column boundaries, so the tallest item usually determines the size of that line. A staggered grid fills lanes independently and places later items into available lane space, producing a denser but less regular visual order. Use a regular grid when alignment matters; use a staggered grid when variable item size and space utilization matter more.

## Pagers: HorizontalPager and VerticalPager

`HorizontalPager` and `VerticalPager` present content as discrete pages with snap behavior. Typical scenarios include onboarding, media galleries and full-page sections. Pages are composed lazily, and `PagerState` exposes the current, settled and target pages and supports programmatic scrolling.

A pager is not a replacement for a free-scrolling list: use it when page boundaries are part of the interaction. `pageSize`, `contentPadding`, `pageSpacing` and fling behavior can adapt the experience, while the default page size fills the viewport along the scroll axis.

## Material components: Scaffold, Surface and Card

### Scaffold

`Scaffold` coordinates common Material screen slots such as `topBar`, `bottomBar`, `floatingActionButton`, `snackbarHost` and the main body. It does not automatically inset the body content. The content lambda receives `innerPadding`, which should be applied to the body container so bars do not cover it.

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

Apply the padding at the correct body boundary and avoid applying the same system or bar insets twice. The exact inset ownership should be explicit when nested scaffolds or edge-to-edge content are involved.

### Surface and Card

`Surface` provides a Material visual surface: shape clipping, background and content colors, border, tonal elevation, shadow and optional interaction semantics. `Card` represents a more specific Material container for a related unit of content, with filled, elevated and outlined variants.

Their primary responsibility is Material presentation, not arranging arbitrary children. Put a `Row`, `Column`, `Box` or another suitable layout inside when the content needs a placement algorithm. Do not choose `Card` as a substitute for a grid or list.

## Complex and custom placement

### ConstraintLayout

Compose `ConstraintLayout` positions composables through relationships to the parent, siblings, guidelines and barriers. It can be useful when many cross-axis relationships are easier to express as constraints or when a design already maps naturally to a constraint set.

Unlike the View system, Compose does not need a flat hierarchy to avoid expensive nested `ViewGroup` measurement. `ConstraintLayout` is therefore not mandatory for a complex screen and is not automatically faster than nested standard layouts. Prefer `Row`, `Column`, `Box` and modifiers when they express the design clearly; use `ConstraintLayout` when its relationship model makes the result easier to understand and maintain.

### Custom Layout

The `Layout` composable gives direct control over measuring children, choosing the container size and placing each child. It is appropriate for a genuinely custom geometry, coordinated placement that standard layouts cannot express, or a reusable layout algorithm with clear invariants.

Start with standard layouts and custom modifiers. They are easier to read, test and keep compatible with intrinsic measurement and accessibility expectations. Move to `Layout` when standard composition causes awkward workarounds or cannot implement the required measure-and-place behavior. A child should normally be measured only once in a layout pass, and the result must respect the constraints from the parent.

`SubcomposeLayout` is a specialized lower-level tool that can compose content during measurement. It is useful when later content depends on measured constraints or the measured size of earlier content, and it underpins patterns such as constraints-aware and lazy composition. It adds complexity and cost, so it should not be the default solution for ordinary custom placement.

## Related topics

- [Compose Basics](basics.md)
- [Compose Performance](performance.md)
- [State & Recomposition](state-recomposition.md)
- [Official Compose layout basics](https://developer.android.com/develop/ui/compose/layouts/basics)
- [Official lazy lists and grids guide](https://developer.android.com/develop/ui/compose/lists)
- [Official custom layouts guide](https://developer.android.com/develop/ui/compose/layouts/custom)
