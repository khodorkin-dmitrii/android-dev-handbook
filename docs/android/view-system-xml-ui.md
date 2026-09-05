# View System / XML UI

The View System is Android's classic UI toolkit, built around XML layouts, `View`, `ViewGroup`, resources, themes, styles, and an imperative rendering pipeline. It remains important for existing applications, interoperability with Compose, custom widgets, and interviews.

## View lifecycle and custom UI

### View lifecycle: measure / layout / draw

Rendering a View hierarchy has three main phases: measure, layout, and draw.

During **measure**, a parent calls `measure()` on each child with width and height `MeasureSpec` values:

- `EXACTLY` - the parent requires a specific size;
- `AT_MOST` - the child may use up to the given size;
- `UNSPECIFIED` - the parent imposes no bound on that dimension.

A custom `View` overrides `onMeasure()` only when the default measurement is insufficient, then reports its result with `setMeasuredDimension()`. Measurement may run more than once, so it must stay fast and deterministic.

During **layout**, the parent assigns each child its final bounds. A custom `ViewGroup` implements `onLayout()` and usually coordinates it with child measurement in `onMeasure()`.

During **draw**, the hierarchy renders into a `Canvas`. Custom content normally belongs in `onDraw()`. Create reusable `Paint`, `Path`, and similar objects outside this method, and move size-dependent calculations to `onSizeChanged()` when possible.

### `invalidate()` vs `requestLayout()`

`invalidate()` marks a `View` as needing redraw. Use it when visual state changes but the measured size and position remain valid, for example after changing a custom color, progress value, or drawing data.

`requestLayout()` marks the hierarchy as needing another measure/layout pass. Use it when content, layout parameters, or state can change a View's size or the placement of children. This work can propagate through ancestors and is generally more expensive than redraw alone.

When both geometry and appearance change, layout and drawing may both be needed. Avoid calling either method repeatedly from code that runs during the same pass.

### Custom View and Custom ViewGroup

Create a custom `View` when standard widgets cannot provide the required drawing, input handling, or behavior. Typical overrides include `onMeasure()`, `onDraw()`, `onSizeChanged()`, and `onTouchEvent()`.

Create a custom `ViewGroup` when children need custom measurement and placement rules. It normally overrides both `onMeasure()` and `onLayout()`.

Common requirements and pitfalls:

- respect padding, minimum size, and `MeasureSpec` constraints;
- avoid allocations and expensive calculations during drawing;
- read configurable values from styled attributes instead of hardcoding them;
- expose meaningful content descriptions and accessibility actions;
- when handling taps manually, call `performClick()` so accessibility services receive the action;
- save custom transient state when it must survive recreation.

### Dialog vs DialogFragment

`Dialog` is a window for modal UI. When it is created and shown directly, the caller owns dismissal, lifecycle coordination, and state restoration.

`DialogFragment` manages a `Dialog` through `FragmentManager`. It integrates the dialog with Fragment lifecycle events and back-stack behavior, making it the safer default for dialogs owned by a Fragment-based screen.

`DialogFragment` does not make arbitrary state persistent automatically. Keep durable state in a `ViewModel` or saved state, and recreate the dialog from that state. Avoid retaining a plain `Dialog` or an old `Activity` context across configuration changes.

## Lists and recycling

### How RecyclerView works

`RecyclerView` displays large or changing data sets using only the item Views needed for the viewport and a limited working set. Its main collaborators have distinct responsibilities:

- `RecyclerView` is the `ViewGroup` that coordinates scrolling, layout, animations, and recycling.
- `LayoutManager` decides which item positions are needed, measures and places their Views, and defines scrolling behavior.
- `RecyclerView.Recycler` supplies a View for a requested position, reusing a compatible `ViewHolder` when possible.
- `Adapter` reports the item count, creates holders, and binds data to them.
- `ViewHolder` owns an item View and caches references needed during binding.

A useful conceptual request chain is:

```text
RecyclerView -> LayoutManager -> Recycler -> Adapter -> ViewHolder
```

This describes collaboration, not ownership. During layout or scrolling, the `LayoutManager` obtains required Views through the `Recycler`. A compatible holder may come from attached scrap, cache, or a recycled-view pool. The `Adapter` creates a holder when none can be reused and binds it when its content must represent a position.

Standard implementations cover common layouts:

- `LinearLayoutManager` - vertical or horizontal list;
- `GridLayoutManager` - grid with a configured span count;
- `StaggeredGridLayoutManager` - grid whose items may have different sizes.

The `LayoutManager` does not own the data or define item content. For changing lists, prefer `ListAdapter` or `AsyncListDiffer` with a correct `DiffUtil.ItemCallback`. Use stable IDs only when items really have stable, unique identities.

## Binding, performance and styling

### ViewBinding vs DataBinding

`ViewBinding` generates a binding class for each enabled XML layout and provides type-safe references to Views with IDs. It replaces most `findViewById()` calls but does not evaluate XML expressions or observe data.

`DataBinding` also generates binding classes and supports XML expressions, binding adapters, observable data, and two-way binding. These features can reduce glue code, but they add build-time complexity and make data flow and debugging less explicit.

Use `ViewBinding` when the screen only needs safe View references. Use `DataBinding` when its declarative binding model is an intentional project-wide choice rather than for a single convenience.

A Fragment's View lifecycle is shorter than the Fragment lifecycle. If binding is stored in a Fragment property, clear that reference in `onDestroyView()` and never access it outside the View lifecycle.

### XML UI performance

Typical bottlenecks include repeated measurement, unnecessarily nested layouts, overdraw, expensive main-thread work, allocations during drawing, and heavy `RecyclerView` binding.

Useful practices:

- flatten hierarchies where measurement shows a benefit; `ConstraintLayout` is useful for complex relationships but is not automatically faster for every screen;
- use `<merge>`, `<include>`, and `ViewStub` where they simplify or defer hierarchy creation;
- use `ListAdapter` / `DiffUtil` for targeted list updates instead of `notifyDataSetChanged()`;
- keep `onBindViewHolder()` cheap and move decoding, formatting, and data preparation out of the hot path;
- inspect actual frames with Layout Inspector, Android Profiler, and system tracing rather than optimizing only by hierarchy depth.

### Themes and Styles

A theme defines high-level defaults for an application, activity, or subtree: colors, typography, shapes, system bars, and widget attributes.

A style is a reusable set of attributes applied to a particular View or family of Views. It can be assigned directly with `style="..."` or referenced by a theme as a default component style.

Prefer theme attributes such as `?attr/colorPrimary` and `?attr/textAppearanceBodyMedium` over fixed values when a component must adapt to branding, dark theme, or another theme overlay.

### Spannable

`Spannable` represents text with style or behavior attached to ranges inside one string. Common spans include `ForegroundColorSpan`, `StyleSpan`, `UnderlineSpan`, `ClickableSpan`, `AbsoluteSizeSpan`, and `ImageSpan`.

Use `SpannableString` when the characters are fixed and only spans change. Use `SpannableStringBuilder` when both text and spans are assembled incrementally.

Span ranges are index-based, so do not hardcode offsets that assume a particular translation. Derive ranges from localized content or use annotated resources. A `ClickableSpan` also requires an appropriate `movementMethod`, such as `LinkMovementMethod`, and meaningful accessibility behavior.

## Related topics

- [Activity, Fragment & Lifecycle](activity-fragment-lifecycle.md)
- [Android Components](components.md)
- [Performance & Memory](performance-memory.md)
- [Android Canvas](canvas.md)
- [Compose Basics](../compose/basics.md)
