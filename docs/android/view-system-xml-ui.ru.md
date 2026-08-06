# View System / XML UI

View System - классический Android UI stack на XML layout, `View`, `ViewGroup`, themes, styles и rendering pipeline.

## View lifecycle и custom UI

### View lifecycle: measure / layout / draw

View lifecycle состоит из трёх основных фаз: measure, layout и draw.

Measure определяет, какого размера должна быть `View`. Родитель вызывает `measure()` у child `View` и передаёт `MeasureSpec`: `EXACTLY`, `AT_MOST` или `UNSPECIFIED`. В custom `View` обычно переопределяют `onMeasure()` и вызывают `setMeasuredDimension()`.

Layout определяет позицию `View` внутри родителя. Для обычной `View` это делает parent, а custom `ViewGroup` в `onLayout()` размещает своих children.

Draw отвечает за отрисовку `View` на `Canvas`. Для custom `View` обычно переопределяют `onDraw()`, но не делают там тяжёлые вычисления и allocations.

**Коротко:** measure calculates size, layout places the view, draw renders it on the screen.

### `invalidate()` vs `requestLayout()`

`invalidate()` просит систему перерисовать `View`. Это нужно, когда изменился только внешний вид: цвет, текстура, progress, custom drawing, но размер и позиция не изменились.

`requestLayout()` просит заново пройти measure/layout для `View` hierarchy. Это нужно, когда изменился размер, layout params, содержимое, влияющее на размер, или положение children.

`requestLayout()` обычно дороже, потому что может затронуть измерение и размещение дерева `View`. Если нужно только перерисовать `Canvas`, достаточно `invalidate()`.

В custom `View` важно выбирать правильный вызов: при изменении drawing state - `invalidate()`, при изменении measured size или layout-affecting state - `requestLayout()`.

### Custom View и Custom ViewGroup

Custom `View` создают, когда стандартных widgets недостаточно и нужно своё рисование, touch handling или особое поведение. Обычно наследуются от `View` и переопределяют `onMeasure()`, `onDraw()` и при необходимости `onTouchEvent()`.

Custom `ViewGroup` создают, когда нужно своё правило измерения и размещения children. Обычно переопределяют `onMeasure()` и `onLayout()`.

Ключевые pitfalls: не делать allocations в `onDraw()`, учитывать padding, корректно обрабатывать `MeasureSpec`, вызывать `setMeasuredDimension()` в `onMeasure()`, поддерживать accessibility и не забывать про `invalidate()` / `requestLayout()`.

**Коротко:** custom `View` отвечает в основном за собственное измерение и рисование, а custom `ViewGroup` дополнительно измеряет и размещает дочерние `View`.

### Dialog vs DialogFragment

`Dialog` - базовый UI-компонент для показа модального окна. Его можно создать напрямую через `Dialog` или `AlertDialog`, но тогда разработчик сам отвечает за lifecycle, сохранение состояния и корректную работу при configuration changes.

`DialogFragment` - `Fragment`-обёртка вокруг `Dialog`. Он интегрирован с `FragmentManager`, имеет lifecycle, корректнее переживает rotation и лучше подходит для показа диалогов в Android-приложении.

На практике `DialogFragment` удобнее, когда диалог связан с navigation/lifecycle или должен переживать пересоздание экрана. Обычный `Dialog` может быть достаточен для простых внутренних случаев, но его легче привязать к устаревшему `Activity Context` и получить leak.

**Коротко:** `Dialog` is just a window, `DialogFragment` manages that dialog through Fragment lifecycle and `FragmentManager`.

## Списки и переиспользование View

### Как работает RecyclerView

`RecyclerView` эффективно отображает большие наборы данных, создавая и сохраняя только те `View` элементов, которые нужны для видимой области и небольшого рабочего запаса вокруг неё. Его основные компоненты разделяют ответственность:

- `RecyclerView` - контейнер `ViewGroup`, который координирует layout, прокрутку и переиспользование элементов.
- `LayoutManager` - определяет, какие позиции сейчас нужны, измеряет и размещает их `View`, а также задаёт пространственное поведение прокрутки.
- `RecyclerView.Recycler` - получает подходящую `View` для запрошенной позиции. По возможности он переиспользует существующий `ViewHolder`, а когда holder нужно создать или привязать, задействует `Adapter`.
- `Adapter` - сообщает количество элементов, создаёт `ViewHolder` и привязывает к нему данные.
- `ViewHolder` - хранит `View` отдельного элемента и ссылки, используемые во время binding.

Полезная концептуальная цепочка запроса выглядит так:

```text
RecyclerView -> LayoutManager -> Recycler -> Adapter -> ViewHolder
```

Это схема взаимодействия, а не иерархия владения. Во время layout `LayoutManager` запрашивает через `Recycler` те `View`, которые нужны для текущего viewport. При прокрутке он перемещает прикреплённые дочерние элементы, передаёт больше не нужные элементы на переиспользование и запрашивает `View` для новых видимых позиций. `Recycler` может использовать совместимый holder повторно; иначе `Adapter` создаёт его и при необходимости выполняет binding.

Стандартные реализации покрывают большинство вариантов раскладки:

- `LinearLayoutManager` - вертикальный или горизонтальный список.
- `GridLayoutManager` - сетка с фиксированным количеством spans.
- `StaggeredGridLayoutManager` - staggered grid, в котором элементы могут иметь разные размеры.

`LayoutManager` не владеет данными и не определяет содержимое элементов. `Adapter` описывает, как представить данные, а `LayoutManager` решает, где и когда должны появиться `View` элементов.

**Коротко:** `RecyclerView` координирует список, `LayoutManager` управляет размещением и прокруткой, `Recycler` переиспользует `View` элементов, `Adapter` создаёт и привязывает holders, а `ViewHolder` хранит `View` отдельного элемента.

## Binding, performance и оформление

### ViewBinding vs DataBinding

`ViewBinding` генерирует binding-класс для XML layout и даёт type-safe доступ к `View` без `findViewById()`. Он не содержит binding expressions и почти не добавляет runtime overhead.

`DataBinding` тоже генерирует binding-класс, но дополнительно поддерживает expressions в XML, binding adapters, two-way binding и привязку observable data. Это мощнее, но сложнее для поддержки, дебага и компиляции.

`ViewBinding` обычно выбирают, когда нужно просто безопасно получить ссылки на `View`. `DataBinding` используют, когда проект сознательно строит UI через XML bindings, но в modern Android часто предпочитают `ViewBinding` + `ViewModel` / `Flow` / `LiveData` или переход на Compose.

Важно очищать binding во `Fragment` в `onDestroyView()`, потому что View lifecycle короче Fragment lifecycle.

### XML UI performance

Основные проблемы XML UI performance: слишком глубокая View hierarchy, лишние nested layouts, overdraw, тяжёлая работа на main thread, частые `requestLayout()`, allocations в custom drawing и неэффективные `RecyclerView` adapters.

Для оптимизации hierarchy используют `ConstraintLayout`, `merge` / `include` / `ViewStub`, flattening layouts и разумное переиспользование компонентов.

Для списков важно использовать `RecyclerView` с `DiffUtil` / `ListAdapter`, stable ids там, где это оправдано, и не делать тяжёлый bind на main thread.

Для отрисовки полезно проверять overdraw, Layout Inspector, Android Profiler и frame rendering tools.

**Коротко:** XML performance usually depends on hierarchy depth, layout passes, drawing cost and main-thread work.

### Themes and Styles

Theme задаёт внешний вид приложения или `Activity` на высоком уровне: цвета, typography, shape, status bar/navigation bar, default attributes для widgets и Material components.

Style - набор атрибутов для конкретного `View` или семейства `View`. Style можно применить напрямую к элементу через `style="..."` или использовать как часть theme.

Главная идея: theme отвечает за глобальный look and feel, а style - за переиспользуемое оформление конкретных компонентов.

В XML UI часто используют theme attributes через `?attr/colorPrimary` или `?attr/textAppearanceBodyMedium`, чтобы компонент автоматически подстраивался под текущую тему, dark mode и branding.

**Коротко:** theme is app/screen-level styling, style is view-level reusable styling; attributes connect components with the current theme.

### Spannable

`Spannable` - Android API для текста с разными стилями внутри одной строки или одного `TextView`: цвет, размер, жирность, underline, clickable spans, иконки и custom spans.

`SpannableString` используется, когда текст неизменяемый по содержимому, но к нему нужно применить spans. `SpannableStringBuilder` удобен, когда текст собирается постепенно.

Типичные spans: `ForegroundColorSpan`, `StyleSpan`, `UnderlineSpan`, `ClickableSpan`, `AbsoluteSizeSpan`, `ImageSpan`.

Важно: spans работают по диапазонам индексов, поэтому нужно аккуратно обрабатывать локализацию. Нельзя жёстко рассчитывать, что substring всегда будет на той же позиции в разных языках.

`ClickableSpan` требует настроить `movementMethod` у `TextView`, например `LinkMovementMethod`, иначе клик может не работать.

**Коротко:** `Spannable` lets one `TextView` render rich text with multiple styles and clickable ranges without splitting text into many views.
