# View System / XML UI

View System - the classic Android UI stack based on XML layout, `View`, `ViewGroup`, themes, styles and the rendering pipeline.

## View lifecycle and custom UI

### View lifecycle: measure / layout / draw

View lifecycle consists of three main phases: measure, layout and draw.

Measure determines what size a `View` should be. The parent calls `measure()` on a child `View` and passes a `MeasureSpec`: `EXACTLY`, `AT_MOST` or `UNSPECIFIED`. In a custom `View`, `onMeasure()` is usually overridden and `setMeasuredDimension()` is called.

Layout determines the position of a `View` inside its parent. For a regular `View`, the parent does this, while a custom `ViewGroup` places its children in `onLayout()`.

Draw renders the `View` on a `Canvas`. A custom `View` usually overrides `onDraw()`, but heavy calculations and allocations should not happen there.

**In short:** measure calculates size, layout places the view, draw renders it on the screen.

### `invalidate()` vs `requestLayout()`

`invalidate()` asks the system to redraw a `View`. This is needed when only appearance changed: color, texture, progress, custom drawing, while size and position did not change.

`requestLayout()` asks the system to run measure/layout again for the `View` hierarchy. This is needed when size, layout params, size-affecting content or child positions changed.

`requestLayout()` is usually more expensive because it can affect measurement and placement of the `View` tree. If you only need to redraw the `Canvas`, `invalidate()` is enough.

In a custom `View`, choose the right call: when drawing state changes - `invalidate()`; when measured size or layout-affecting state changes - `requestLayout()`.

### Custom View and Custom ViewGroup

Create a custom `View` when standard widgets are not enough and you need custom drawing, touch handling or special behavior. Usually it inherits from `View` and overrides `onMeasure()`, `onDraw()` and, when needed, `onTouchEvent()`.

Create a custom `ViewGroup` when you need your own rules for measuring and placing children. Usually it overrides `onMeasure()` and `onLayout()`.

Key pitfalls: avoid allocations in `onDraw()`, account for padding, handle `MeasureSpec` correctly, call `setMeasuredDimension()` in `onMeasure()`, support accessibility and remember `invalidate()` / `requestLayout()`.

**In short:** custom `View` is mainly responsible for its own measurement and drawing, while custom `ViewGroup` additionally measures and places child `View`s.

### Dialog vs DialogFragment

`Dialog` - a basic UI component for showing a modal window. It can be created directly through `Dialog` or `AlertDialog`, but then the developer is responsible for lifecycle, state saving and correct behavior during configuration changes.

`DialogFragment` - a `Fragment` wrapper around a `Dialog`. It is integrated with `FragmentManager`, has a lifecycle, handles rotation more correctly and is usually better for showing dialogs in an Android app.

In practice, `DialogFragment` is more convenient when the dialog is tied to navigation/lifecycle or should survive screen recreation. A plain `Dialog` may be enough for simple internal cases, but it is easier to bind it to a stale `Activity Context` and get a leak.

**In short:** `Dialog` is just a window, `DialogFragment` manages that dialog through Fragment lifecycle and `FragmentManager`.

## Lists and recycling

### How RecyclerView works

`RecyclerView` efficiently displays large data sets by creating and keeping only the item `View`s needed for the visible area and a small working set around it. Its main components have separate responsibilities:

- `RecyclerView` is the `ViewGroup` container that coordinates layout, scrolling and recycling.
- `LayoutManager` decides which item positions are needed, measures and places their `View`s, and implements the spatial behavior of scrolling.
- `RecyclerView.Recycler` obtains a suitable `View` for a requested position. It reuses an existing `ViewHolder` when possible and involves the `Adapter` when a holder must be created or bound.
- `Adapter` provides the item count, creates `ViewHolder`s and binds data to them.
- `ViewHolder` wraps an item `View` and keeps references used during binding.

A useful conceptual request chain is:

```text
RecyclerView -> LayoutManager -> Recycler -> Adapter -> ViewHolder
```

This is a collaboration flow, not an ownership hierarchy. During layout, the `LayoutManager` requests the `View`s required for the current viewport through the `Recycler`. During scrolling, it moves the attached children, recycles those that are no longer needed and requests `View`s for newly visible positions. The `Recycler` can reuse a compatible holder; otherwise the `Adapter` creates one, and it binds the holder when required.

The standard implementations cover most layouts:

- `LinearLayoutManager` - a vertical or horizontal list.
- `GridLayoutManager` - a grid with a fixed number of spans.
- `StaggeredGridLayoutManager` - a staggered grid where items may have different sizes.

The `LayoutManager` does not own the data or define item content. The `Adapter` describes how data is represented, while the `LayoutManager` determines where and when item `View`s appear.

**In short:** `RecyclerView` coordinates the list, `LayoutManager` controls placement and scrolling, `Recycler` reuses item views, `Adapter` creates and binds holders, and `ViewHolder` stores an individual item `View`.

## Binding, performance and styling

### ViewBinding vs DataBinding

`ViewBinding` generates a binding class for an XML layout and gives type-safe access to `View`s without `findViewById()`. It does not include binding expressions and adds almost no runtime overhead.

`DataBinding` also generates a binding class, but additionally supports expressions in XML, binding adapters, two-way binding and binding observable data. It is more powerful, but harder to maintain, debug and compile.

`ViewBinding` is usually chosen when you simply need safe references to `View`s. `DataBinding` is used when a project intentionally builds UI through XML bindings, but in modern Android teams often prefer `ViewBinding` + `ViewModel` / `Flow` / `LiveData`, or move to Compose.

It is important to clear binding in a `Fragment` in `onDestroyView()`, because the View lifecycle is shorter than the Fragment lifecycle.

### XML UI performance

Main XML UI performance problems: overly deep View hierarchy, unnecessary nested layouts, overdraw, heavy work on the main thread, frequent `requestLayout()`, allocations in custom drawing and inefficient `RecyclerView` adapters.

To optimize hierarchy, use `ConstraintLayout`, `merge` / `include` / `ViewStub`, layout flattening and reasonable component reuse.

For lists, it is important to use `RecyclerView` with `DiffUtil` / `ListAdapter`, stable ids where justified, and avoid heavy binding on the main thread.

For rendering, it is useful to inspect overdraw, Layout Inspector, Android Profiler and frame rendering tools.

**In short:** XML performance usually depends on hierarchy depth, layout passes, drawing cost and main-thread work.

### Themes and Styles

Theme defines the high-level appearance of an app or `Activity`: colors, typography, shape, status bar/navigation bar, default attributes for widgets and Material components.

Style - a set of attributes for a specific `View` or family of `View`s. A style can be applied directly to an element through `style="..."` or used as part of a theme.

The main idea: theme is responsible for global look and feel, while style is reusable styling for specific components.

XML UI often uses theme attributes through `?attr/colorPrimary` or `?attr/textAppearanceBodyMedium`, so a component automatically adapts to the current theme, dark mode and branding.

**In short:** theme is app/screen-level styling, style is view-level reusable styling; attributes connect components with the current theme.

### Spannable

`Spannable` - an Android API for text with different styles inside one string or one `TextView`: color, size, bold style, underline, clickable spans, icons and custom spans.

`SpannableString` is used when the text content is immutable, but spans need to be applied to it. `SpannableStringBuilder` is convenient when text is assembled gradually.

Typical spans: `ForegroundColorSpan`, `StyleSpan`, `UnderlineSpan`, `ClickableSpan`, `AbsoluteSizeSpan`, `ImageSpan`.

Important: spans work by index ranges, so localization must be handled carefully. Do not hardcode the assumption that a substring will always be at the same position in different languages.

`ClickableSpan` requires configuring `movementMethod` on `TextView`, for example `LinkMovementMethod`; otherwise clicks may not work.

**In short:** `Spannable` lets one `TextView` render rich text with multiple styles and clickable ranges without splitting text into many views.
