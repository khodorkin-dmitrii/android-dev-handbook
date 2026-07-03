# Compose Basics

Jetpack Compose - современный declarative UI toolkit для Android. Вместо ручного изменения View-дерева мы описываем UI как функцию от state, а Compose обновляет нужные части интерфейса при изменении данных.

## Основы Compose

### Что такое Jetpack Compose?

Compose используется для построения экранов на Kotlin без XML и хорошо интегрируется с `ViewModel`, `Flow` / `StateFlow`, Material Design, Navigation и testing APIs.

Главная mental model: composable должен быть быстрым, idempotent и side-effect free. Не стоит думать, что Compose каждый раз полностью перерисовывает весь экран: он старается пропускать неизменившиеся части.

Compose - это не только замена XML layouts. Он меняет подход к моделированию UI: вместо ручного проталкивания изменений во View мы передаём state и позволяем Compose обновить затронутую часть интерфейса.

**Коротко:** Jetpack Compose позволяет строить Android UI declaratively: UI является функцией от state, а Compose recomposes affected parts when state changes.

### Declarative UI

Declarative UI - это подход, при котором код описывает, как UI должен выглядеть для текущего state, а не какие пошаговые команды нужно выполнить, чтобы вручную изменить экран.

В imperative View System мы часто вызываем `setText()`, `setVisibility()` или `notifyDataSetChanged()`. В Compose мы передаём новое состояние в composable, Compose заново выполняет затронутые composable functions и обновляет UI tree там, где это нужно.

Практический плюс - проще reasoning о loading/content/error, формах, списках и state-driven экранах.

```kotlin
data class UserUiState(
    val isLoading: Boolean = false,
    val userName: String? = null,
    val error: String? = null
)

@Composable
fun UserScreen(
    state: UserUiState,
    onRetryClick: () -> Unit
) {
    when {
        state.isLoading -> CircularProgressIndicator()
        state.error != null -> ErrorMessage(
            message = state.error,
            onRetryClick = onRetryClick
        )
        state.userName != null -> Text("Hello, ${state.userName}")
    }
}
```

Здесь composable не решает, как загружать данные. Он только отображает текущее состояние и отдаёт наружу callbacks для пользовательских действий.

**Важно:** не выполняйте business logic и side effects прямо в body composable, потому что recomposition может происходить часто, быть пропущена или отменена.

**Коротко:** в declarative UI экран рендерится из state; когда state меняется, мы передаём новые inputs, а framework обновляет UI.

### Compose vs View System

Классический Android View System является imperative: XML описывает начальный layout, а код позже изменяет views через вызовы вроде `setText()`, `setVisibility()` или adapter update APIs.

Compose является declarative: UI описывается прямо на Kotlin через composable functions. Когда state меняется, Compose сам решает, что нужно recomposed, laid out или redrawn.

Это не значит, что View System везде устарел. Многие production-приложения используют оба подхода во время миграции:

- Compose можно встроить в существующие XML / Fragment screens через `ComposeView`.
- Android Views можно встроить в Compose через `AndroidView`.
- Новые экраны можно писать на Compose, пока legacy screens остаются на Views.

**Коротко:** View System imperatively обновляет существующие views; Compose declaratively рендерит UI из state и поддерживает постепенную миграцию.

### Composable function

Composable function - это Kotlin-функция, помеченная `@Composable`, которая описывает часть UI и может вызывать другие composable functions.

Composable не возвращает `View`. Он участвует в Composition: Compose вызывает composable functions, строит UI tree и обновляет его при изменении state.

```kotlin
@Composable
fun Greeting(name: String) {
    Text("Hello, $name")
}
```

Важные правила: composable может вызываться много раз, в другом порядке или быть skipped, поэтому он должен быть быстрым и не должен выполнять неожиданные side effects. Для событий используют callbacks, а для controlled side effects - специальные APIs вроде `LaunchedEffect`.

Не стоит делать прямо в body composable:

- network или database calls;
- запуск coroutines без effect API;
- мутацию external state во время composition;
- тяжёлые вычисления на каждой recomposition;
- logging или analytics, которые должны произойти ровно один раз.

Вместо этого держите screen logic во `ViewModel`, отдавайте state в UI, отправляйте user actions обратно через callbacks и используйте Compose side-effect APIs только тогда, когда effect действительно привязан к composition.

**Коротко:** composable function описывает UI для заданных inputs; она должна быть быстрой, idempotent и свободной от uncontrolled side effects.

### Стадии отрисовки в Compose / Compose rendering phases

В Compose UI обновляется через несколько фаз: Composition, Layout и Drawing.

Composition - фаза, в которой Compose вызывает composable functions и строит или обновляет UI tree. Здесь Compose определяет, что должно быть на экране: какие composables нужны, какие параметры они получают и какая структура UI получается из текущего state.

Layout - фаза измерения и размещения элементов. Здесь Compose определяет размеры UI nodes и их позицию на экране. Эта фаза включает measure и placement: сначала элементы измеряются с учётом constraints, затем размещаются внутри parent.

Drawing - фаза отрисовки. Здесь Compose рисует уже измеренные и размещённые элементы: текст, фон, иконки, canvas drawing, draw modifiers и другие визуальные детали.

Важный момент: изменение state не всегда означает полный проход всех фаз. Compose старается перезапустить только те фазы, которые действительно зависят от изменившегося state.

Если state читается в body composable, изменение может вызвать recomposition, а затем при необходимости layout и drawing. Если state читается только в layout modifier, Compose может пропустить Composition и перейти сразу к Layout. Если state читается только в draw phase, Compose может ограничиться redraw без recomposition и relayout.

Например, если цвет читается внутри `Modifier.drawBehind { drawCircle(color) }`, то при изменении только `color` Compose может выполнить только Drawing phase, потому что структура UI и layout не изменились.

**Коротко:** rendering pipeline в Jetpack Compose состоит из трёх основных фаз: Composition, Layout и Drawing. Изменение state может перезапустить одну или несколько фаз в зависимости от того, где этот state читается.

## Related topics

- [State & Recomposition](state-recomposition.md)
- [Side Effects](side-effects.md)
- [Compose Performance](performance.md)
- [UI State Architecture](../architecture/ui-state.md)
