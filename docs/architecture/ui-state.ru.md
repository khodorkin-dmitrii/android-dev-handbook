# UI State Architecture

UI state architecture описывает, кто владеет состоянием экрана, как UI получает данные и как одноразовые effects отделяются от durable state.

## UI state

### ViewModel + UI state

`ViewModel` в modern Android обычно играет роль screen-level state holder: получает события от UI, запускает use cases/repository calls и публикует UI state для экрана.

UI state должен быть описанием того, что экран должен показать прямо сейчас: loading, data, error, selected values, input text, enabled/disabled states и другие user-visible данные.

Практичный подход - хранить UI state как immutable data class или sealed hierarchy и отдавать наружу read-only `StateFlow`. UI только рендерит state и отправляет actions/events обратно во `ViewModel`.

```kotlin
data class ProfileUiState(
    val isLoading: Boolean = false,
    val userName: String = "",
    val errorMessage: String? = null
)

private val _uiState = MutableStateFlow(ProfileUiState())
val uiState: StateFlow<ProfileUiState> = _uiState.asStateFlow()
```

**Коротко:** `ViewModel` owns screen UI state, exposes it as an observable immutable state, and handles user actions by updating that state through domain or data layer.

### Loading / content / error

Loading/content/error - базовая модель состояния экрана, которая помогает явно описать основные режимы UI: данные загружаются, данные успешно показаны, произошла ошибка.

Для простого экрана можно использовать sealed interface:

```kotlin
sealed interface UiState {
    data object Loading : UiState
    data class Content(val items: List<ItemUiModel>) : UiState
    data class Error(val message: String) : UiState
}
```

Такой подход удобен, когда состояния взаимоисключающие: экран либо loading, либо content, либо error. Он уменьшает количество противоречивых boolean flags вроде `isLoading = true` и `error != null` одновременно.

Для более сложных экранов часто используют data class state: content может оставаться на экране во время refresh, а loading/error могут быть дополнительными полями. Например, список уже показан, но сверху идёт pull-to-refresh или snackbar error.

**Коротко:** sealed state works well for mutually exclusive screen states, while data class state is better when content, loading and errors can coexist.

### State vs events/effects

State - durable описание UI, которое можно отрисовать повторно после recomposition, rotation или новой подписки. Например: список элементов, выбранная вкладка, текст в поле ввода, loading flag.

Events/effects - одноразовые действия, которые не являются постоянным состоянием экрана: navigation, snackbar, toast, scroll command, permission request, open external screen.

Главный риск - положить one-off event в обычный UI state и случайно повторить его после rotation или повторного collect. Например, если state содержит `navigateBack = true`, новый UI collector может выполнить навигацию ещё раз.

Обычно state публикуют через `StateFlow<UiState>`, а one-off effects - через `SharedFlow<UiEvent>`, `Channel` или explicit callback, в зависимости от архитектуры проекта.

**Коротко:** state describes what the UI should look like, effects describe one-time actions the UI should perform.

### One-off events

One-off event - событие, которое должно быть обработано один раз: показать snackbar, открыть экран, закрыть экран, запросить permission, проскроллить список.

Типичный вариант во `ViewModel`:

```kotlin
sealed interface UiEvent {
    data class ShowSnackbar(val message: String) : UiEvent
    data object NavigateBack : UiEvent
}

private val _events = MutableSharedFlow<UiEvent>()
val events = _events.asSharedFlow()
```

UI collect-ит events lifecycle-aware и выполняет side effect. В Compose это часто делают через `LaunchedEffect`, во View System - через `repeatOnLifecycle`.

**Важно:** `SharedFlow` с `replay = 0` может потерять событие, если collector ещё не активен. Для некритичных UI effects это часто приемлемо, но для важного состояния лучше моделировать результат как часть `UiState`.

Альтернатива - event wrapper/consumable state, но он легко усложняет код. Важно выбирать подход осознанно и не смешивать durable state с transient commands.

**Коротко:** one-off events should be separated from persistent UI state, but event delivery must be lifecycle-aware to avoid duplicates or lost events.

## Feature design

### Как проектировать feature flow с нуля?

При проектировании feature flow сначала нужно понять user scenario: какие данные нужны экрану, какие states возможны, какие user actions есть и какие side effects должны произойти.

Практичный порядок: определить UI contract, описать `UiState`, `UiEvent` и `UserAction`, понять источники данных, выбрать owner состояния, затем связать UI -> `ViewModel` -> use cases/repositories -> data sources.

Дальше стоит решить, какие операции one-shot suspend functions, а какие являются streams `Flow`. Например, загрузить профиль один раз можно suspend-функцией, а наблюдать статус робота или базу данных лучше через `Flow`.

Важно сразу отделить state от effects: content/loading/error должны быть частью `UiState`, а navigation/snackbar/permission request - отдельными events/effects, если они действительно одноразовые.

Также нужно подумать о lifecycle, process death, retry, offline/cache, error mapping, analytics, testing и границах модулей. Не обязательно строить идеальную Clean Architecture для маленького экрана, но ответственность слоёв должна быть понятной.

**Коротко:** start from the UI contract and user actions, model durable `UiState` and one-off effects, then decide which logic belongs to `ViewModel`, domain/use cases, repositories and data sources.
