# View System / XML UI

View System - классический UI toolkit Android на основе XML-разметки, `View`, `ViewGroup`, ресурсов, тем, стилей и императивного rendering pipeline. Он по-прежнему важен для существующих приложений, интеграции с Compose, custom widgets и собеседований.

## Жизненный цикл View и custom UI

### Жизненный цикл View: measure / layout / draw

Отрисовка View hierarchy состоит из трёх основных фаз: measure, layout и draw.

Во время **measure** родитель вызывает `measure()` для каждого дочернего элемента и передаёт `MeasureSpec` для ширины и высоты:

- `EXACTLY` - родитель требует конкретный размер;
- `AT_MOST` - дочерний элемент может занять не больше заданного размера;
- `UNSPECIFIED` - родитель не ограничивает размер по этой оси.

Custom `View` переопределяет `onMeasure()`, только если стандартного измерения недостаточно, и сообщает результат через `setMeasuredDimension()`. Измерение может выполняться несколько раз, поэтому оно должно быть быстрым и детерминированным.

Во время **layout** родитель задаёт окончательные границы каждого дочернего элемента. Custom `ViewGroup` реализует `onLayout()` и обычно согласует размещение с измерением children в `onMeasure()`.

Во время **draw** иерархия рисуется на `Canvas`. Собственную отрисовку обычно выполняют в `onDraw()`. Переиспользуемые `Paint`, `Path` и похожие объекты следует создавать за пределами этого метода, а вычисления, зависящие от размера, по возможности переносить в `onSizeChanged()`.

### `invalidate()` vs `requestLayout()`

`invalidate()` помечает `View` как требующую перерисовки. Он нужен, когда изменилось визуальное состояние, но текущие размер и позиция остаются корректными, например при изменении цвета, progress или данных custom drawing.

`requestLayout()` помечает иерархию как требующую нового прохода measure/layout. Он нужен, когда содержимое, layout params или состояние могут изменить размер `View` либо расположение children. Такой запрос может распространиться вверх по иерархии и обычно дороже одной перерисовки.

Если изменилась и геометрия, и внешний вид, могут потребоваться оба этапа. Не стоит многократно вызывать эти методы из кода, который выполняется во время того же прохода.

### Custom View и Custom ViewGroup

Custom `View` создают, когда стандартные widgets не дают нужной отрисовки, обработки ввода или поведения. Обычно переопределяют `onMeasure()`, `onDraw()`, `onSizeChanged()` и при необходимости `onTouchEvent()`.

Custom `ViewGroup` нужен для собственных правил измерения и размещения children. Обычно он переопределяет и `onMeasure()`, и `onLayout()`.

Основные требования и типичные ошибки:

- учитывать padding, минимальный размер и ограничения `MeasureSpec`;
- избегать allocations и тяжёлых вычислений во время draw;
- получать настраиваемые значения из styled attributes, а не хардкодить их;
- предоставлять осмысленные content descriptions и accessibility actions;
- при ручной обработке нажатий вызывать `performClick()`, чтобы действие получали accessibility services;
- сохранять временное пользовательское состояние, если оно должно переживать пересоздание.

### Dialog vs DialogFragment

`Dialog` - окно для модального UI. Если создать и показать его напрямую, вызывающий код сам отвечает за закрытие, согласование с lifecycle и восстановление состояния.

`DialogFragment` управляет `Dialog` через `FragmentManager`. Он связывает диалог с lifecycle Fragment и back stack, поэтому обычно безопаснее для диалогов на экранах, построенных на Fragment.

`DialogFragment` не делает произвольное состояние автоматически постоянным. Долгоживущее состояние следует хранить во `ViewModel` или saved state и по нему пересоздавать диалог. Не нужно удерживать обычный `Dialog` или старый `Activity` context после configuration change.

## Списки и переиспользование View

### Как работает RecyclerView

`RecyclerView` отображает большие или изменяемые наборы данных, используя только item Views, необходимые для viewport и ограниченного рабочего запаса. Основные участники имеют разные обязанности:

- `RecyclerView` - контейнер `ViewGroup`, координирующий прокрутку, layout, анимации и recycling.
- `LayoutManager` - определяет нужные позиции, измеряет и размещает их Views и задаёт поведение прокрутки.
- `RecyclerView.Recycler` - предоставляет View для запрошенной позиции, по возможности переиспользуя совместимый `ViewHolder`.
- `Adapter` - сообщает количество элементов, создаёт holders и привязывает к ним данные.
- `ViewHolder` - хранит item View и ссылки, необходимые во время binding.

Полезная концептуальная цепочка запроса:

```text
RecyclerView -> LayoutManager -> Recycler -> Adapter -> ViewHolder
```

Это схема взаимодействия, а не иерархия владения. Во время layout или прокрутки `LayoutManager` получает нужные Views через `Recycler`. Совместимый holder может быть взят из attached scrap, cache или recycled-view pool. Если подходящего holder нет, `Adapter` создаёт его, а когда содержимое должно соответствовать позиции - выполняет binding.

Стандартные реализации покрывают типичные раскладки:

- `LinearLayoutManager` - вертикальный или горизонтальный список;
- `GridLayoutManager` - сетка с заданным количеством spans;
- `StaggeredGridLayoutManager` - сетка с элементами разного размера.

`LayoutManager` не владеет данными и не определяет содержимое элементов. Для изменяемых списков лучше использовать `ListAdapter` или `AsyncListDiffer` с корректным `DiffUtil.ItemCallback`. Stable IDs нужны только тогда, когда у элементов действительно есть стабильные уникальные идентификаторы.

## Binding, performance и оформление

### ViewBinding vs DataBinding

`ViewBinding` генерирует binding-класс для каждой подключённой XML-разметки и предоставляет type-safe ссылки на Views с ID. Он заменяет большинство вызовов `findViewById()`, но не вычисляет XML expressions и не наблюдает за данными.

`DataBinding` тоже генерирует binding-классы и поддерживает XML expressions, binding adapters, observable data и two-way binding. Эти возможности могут уменьшить количество связующего кода, но усложняют сборку и делают поток данных и отладку менее явными.

`ViewBinding` подходит, когда экрану нужны только безопасные ссылки на Views. `DataBinding` стоит использовать, когда его декларативная модель является осознанным решением для проекта, а не удобством для одного случая.

View lifecycle у Fragment короче lifecycle самого Fragment. Если binding хранится в property Fragment, ссылку нужно очищать в `onDestroyView()` и не использовать за пределами View lifecycle.

### Производительность XML UI

Типичные узкие места - повторные измерения, лишние вложенные layouts, overdraw, тяжёлая работа на main thread, allocations во время draw и дорогой binding в `RecyclerView`.

Практические рекомендации:

- упрощать иерархию там, где измерения показывают пользу; `ConstraintLayout` удобен для сложных связей, но не становится автоматически быстрее на любом экране;
- использовать `<merge>`, `<include>` и `ViewStub`, когда они упрощают или откладывают создание иерархии;
- применять `ListAdapter` / `DiffUtil` для точечных обновлений вместо `notifyDataSetChanged()`;
- делать `onBindViewHolder()` дешёвым, вынося decoding, formatting и подготовку данных из горячего пути;
- анализировать реальные кадры через Layout Inspector, Android Profiler и system tracing, а не оптимизировать только по глубине иерархии.

### Themes and Styles

Theme задаёт высокоуровневые значения по умолчанию для приложения, `Activity` или части иерархии: цвета, typography, shapes, системные панели и атрибуты widgets.

Style - переиспользуемый набор атрибутов для конкретной `View` или семейства Views. Его можно назначить напрямую через `style="..."` или указать в theme как стандартный стиль компонента.

Если компонент должен адаптироваться к брендингу, dark theme или theme overlay, лучше использовать theme attributes вроде `?attr/colorPrimary` и `?attr/textAppearanceBodyMedium`, а не фиксированные значения.

### Spannable

`Spannable` представляет текст, к диапазонам которого привязано оформление или поведение. Типичные spans: `ForegroundColorSpan`, `StyleSpan`, `UnderlineSpan`, `ClickableSpan`, `AbsoluteSizeSpan` и `ImageSpan`.

`SpannableString` подходит, когда символы не меняются, а изменяются только spans. `SpannableStringBuilder` удобен, когда текст и spans собираются постепенно.

Диапазоны spans задаются индексами, поэтому нельзя хардкодить offsets в расчёте на конкретный перевод. Диапазоны следует определять по локализованному содержимому или использовать аннотированные resources. Для `ClickableSpan` также нужен подходящий `movementMethod`, например `LinkMovementMethod`, и корректное accessibility-поведение.

## Связанные темы

- [Activity, Fragment & Lifecycle](activity-fragment-lifecycle.md)
- [Android Components](components.md)
- [Performance & Memory](performance-memory.md)
- [Android Canvas](canvas.md)
- [Compose Basics](../compose/basics.md)
