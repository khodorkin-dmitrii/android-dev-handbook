# Compose Basics

Jetpack Compose - современный declarative UI toolkit для Android. Вместо ручного изменения View-дерева мы описываем UI как функцию от state, а Compose сам обновляет нужные части интерфейса при изменении данных.

## Основы Compose

### Что такое Jetpack Compose?

Compose используется для построения экранов на Kotlin без XML и хорошо интегрируется с `ViewModel`, `Flow` / `StateFlow`, Material Design, Navigation и testing APIs.

Главный mental model: composable должен быть быстрым, idempotent и side-effect free. Нельзя думать, что Compose каждый раз полностью перерисовывает весь экран: он старается пропускать неизменившиеся части.

**Коротко:** Jetpack Compose lets us build Android UI declaratively: UI is a function of state, and Compose recomposes affected parts when state changes.

### Declarative UI

Declarative UI - подход, где код описывает, как UI должен выглядеть для текущего state, а не какие пошаговые команды нужно выполнить, чтобы вручную изменить экран.

В imperative View System мы часто делаем `setText()`, `setVisibility()`, `notifyDataSetChanged()`. В Compose мы передаём новое состояние в composable, и UI пересобирается как результат этого состояния.

Практический плюс - проще reasoning о loading/content/error, формах, списках и state-driven экранах.

**Важно:** нельзя выполнять business logic и side effects прямо в body composable, потому что recomposition может происходить часто, быть пропущена или отменена.

**Коротко:** in declarative UI, the screen is rendered from state; when state changes, we provide new inputs and the framework updates the UI.

### Composable function

Composable function - Kotlin-функция, помеченная `@Composable`, которая описывает часть UI и может вызывать другие composable functions.

Composable не возвращает `View`. Он участвует в Composition: Compose вызывает composable functions, строит UI tree и обновляет его при изменении state.

```kotlin
@Composable
fun Greeting(name: String) {
    Text("Hello, $name")
}
```

Важные правила: composable может вызываться много раз, в другом порядке, может быть skipped, поэтому он должен быть быстрым и не должен выполнять неожиданные side effects. Для событий используют callbacks, а для controlled side effects - специальные APIs вроде `LaunchedEffect`.

**Коротко:** a composable function describes UI for given inputs; it should be fast, idempotent and free of uncontrolled side effects.

### Стадии отрисовки в Compose / Compose rendering phases

В Compose UI обновляется через несколько фаз: Composition, Layout и Drawing.

Composition - фаза, где Compose вызывает composable-функции и строит или обновляет UI tree. Здесь определяется, что должно быть на экране: какие composable нужны, какие параметры они получают и какая структура UI получается из текущего state.

Layout - фаза измерения и размещения элементов. Здесь Compose определяет размеры UI nodes и их позицию на экране. Эта фаза включает measure и placement: сначала элементы измеряются с учётом constraints, затем размещаются внутри parent.

Drawing - фаза отрисовки. Здесь Compose рисует уже измеренные и размещённые элементы: текст, фон, иконки, canvas drawing, draw modifiers и другие визуальные детали.

Важный момент: изменение state не всегда означает полный проход всех фаз. Compose старается перезапустить только те фазы, которые действительно зависят от изменившегося state.

Если state читается в body composable, изменение может вызвать recomposition, а затем при необходимости layout и drawing. Если state читается только в layout modifier, Compose может пропустить Composition и перейти сразу к Layout. Если state читается только в draw phase, Compose может ограничиться redraw без recomposition и relayout.

Например, если цвет читается внутри `Modifier.drawBehind { drawCircle(color) }`, то при изменении только `color` Compose может выполнить только Drawing phase, потому что структура UI и layout не изменились.

**Коротко:** Jetpack Compose rendering pipeline has three main phases: Composition, Layout, and Drawing. A state change may restart one or more phases depending on where that state is read.
