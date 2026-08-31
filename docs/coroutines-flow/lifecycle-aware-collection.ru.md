# Lifecycle-aware Collection

Lifecycle-aware collection нужна, чтобы UI собирал данные только тогда, когда экран может ими воспользоваться. Это предотвращает лишнюю работу upstream-источников и не позволяет остановленному UI реагировать на обновления.

## Сбор данных в Android UI

### `collectAsStateWithLifecycle`

`collectAsStateWithLifecycle()` - рекомендуемый Android Compose API для преобразования `Flow` в Compose `State` с учётом `Lifecycle`. Он предоставляется библиотекой `lifecycle-runtime-compose`.

Для `StateFlow` текущее значение используется автоматически:

```kotlin
val uiState by viewModel.uiState.collectAsStateWithLifecycle()
```

Для обычного `Flow` нужно передать начальное значение:

```kotlin
val items by viewModel.items.collectAsStateWithLifecycle(
    initialValue = emptyList(),
)
```

По умолчанию collection работает, пока lifecycle находится как минимум в состоянии `STARTED`. При переходе ниже этого состояния collecting coroutine отменяется, а когда lifecycle снова становится активным, collection запускается заново. После перезапуска `StateFlow` сразу передаёт последнее значение.

Используйте `collectAsStateWithLifecycle()` для наблюдаемого состояния экрана. Обычный `collectAsState()` не учитывает lifecycle и подходит главным образом для платформонезависимого Compose-кода или потоков, чей lifetime уже контролируется другим способом.

Не используйте сбор state для одноразовых команд только ради удобства. State может быть повторно получен после пересоздания UI, поэтому для навигации и snackbar нужно явно определить семантику доставки.

### `repeatOnLifecycle`

`repeatOnLifecycle()` запускает suspending block, когда `Lifecycle` достигает заданного состояния. Ниже этого состояния block и его дочерние coroutine отменяются, а при возвращении lifecycle запускается новый block.

Типичный сбор данных во Fragment/View System:

```kotlin
viewLifecycleOwner.lifecycleScope.launch {
    viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.uiState.collect(::render)
    }
}
```

Для Fragment UI используйте `viewLifecycleOwner`, потому что lifecycle View короче lifecycle самого Fragment. Это предотвращает обновление уже уничтоженного View.

Если несколько flow нужно собирать одновременно, запускайте для каждого отдельную дочернюю coroutine. Вызов `collect` обычно не завершается, поэтому при последовательных вызовах код не дойдёт до следующих collectors:

```kotlin
viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
    launch { viewModel.uiState.collect(::render) }
    launch { viewModel.messages.collect(::showMessage) }
}
```

Предпочитайте `repeatOnLifecycle()` устаревшим `launchWhenStarted` / `launchWhenResumed`. Эти API приостанавливают consumer вместо его отмены, поэтому upstream-производитель flow может продолжать работать, пока UI остановлен.

### Effects в Compose

`LaunchedEffect` запускает coroutine, привязанную к присутствию composable в composition. Он подходит для UI-реакций вроде показа snackbar, прокрутки или навигации, но **сам по себе не учитывает Android lifecycle**.

Для effects, которые нужно обрабатывать только в состоянии `STARTED`, объедините его с `repeatOnLifecycle()`:

```kotlin
val lifecycleOwner = LocalLifecycleOwner.current

LaunchedEffect(viewModel, lifecycleOwner) {
    lifecycleOwner.lifecycle.repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.events.collect { event ->
            when (event) {
                UiEvent.NavigateBack -> navController.popBackStack()
                is UiEvent.ShowSnackbar ->
                    snackbarHostState.showSnackbar(event.message)
            }
        }
    }
}
```

`LaunchedEffect` перезапускается при изменении любого ключа. Выбирайте стабильные ключи, соответствующие владельцу подписки: случайная смена ключа отменит и заново создаст collector.

Lifecycle-aware collection не гарантирует доставку событий. `SharedFlow` с `replay = 0` теряет emission, когда активного collector нет, а replay эффекта может повторно выполнить его после пересоздания UI. Храните критически важный результат в устойчивом UI state, а для временных effects явно определяйте правила потери, буферизации и потребления.

## Связанные темы

- [StateFlow & SharedFlow](stateflow-sharedflow.ru.md)
- [Coroutine Scopes & Cancellation](scopes-cancellation.ru.md)
- [UI State Architecture](../architecture/ui-state.ru.md)
