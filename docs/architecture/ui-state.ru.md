# UI State Architecture

UI state architecture описывает, кто владеет состоянием экрана, как UI получает данные, как состояние восстанавливается и как одноразовые effects отделяются от durable state.

## UI state

### ViewModel + UI state

В modern Android `ViewModel` обычно выступает как screen-level state holder: получает события от UI, запускает use cases или repository calls и публикует UI state для экрана.

UI state должен описывать то, что экран должен показать прямо сейчас: loading, data, error, selected values, input text, enabled/disabled states и другие user-visible данные.

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

**Коротко:** `ViewModel` владеет screen UI state, отдаёт его как observable immutable state и обрабатывает действия пользователя, обновляя state через domain или data layer.

### Loading / content / error

Loading/content/error - базовая модель состояния экрана, которая явно описывает основные режимы UI: данные загружаются, данные успешно показаны или произошла ошибка.

Для простого экрана хорошо подходит sealed interface:

```kotlin
sealed interface UiState {
    data object Loading : UiState
    data class Content(val items: List<ItemUiModel>) : UiState
    data class Error(val message: String) : UiState
}
```

Такой подход удобен, когда состояния взаимоисключающие: экран находится либо в loading, либо в content, либо в error. Это уменьшает риск противоречивых boolean flags вроде `isLoading = true` и `error != null` одновременно.

Для более сложных экранов часто лучше подходит data class state: content может оставаться на экране во время refresh, а loading/error будут дополнительными полями. Например, список уже показан, но поверх него отображается pull-to-refresh indicator или snackbar error.

**Коротко:** sealed state хорошо работает для взаимоисключающих состояний экрана, а data class state лучше подходит, когда content, loading и errors могут сосуществовать.

### State vs events/effects

State - это durable описание UI, которое можно отрисовать повторно после recomposition, rotation или новой подписки. Примеры: список элементов, выбранная вкладка, текст в поле ввода, loading flag.

Events/effects - это одноразовые действия, которые не являются постоянным состоянием экрана: navigation, snackbar, toast, scroll command, permission request, opening an external screen.

Главный риск - положить one-off event в обычный UI state и случайно повторить его после rotation или нового collect. Например, если state содержит `navigateBack = true`, новый UI collector может выполнить навигацию ещё раз.

Обычно state публикуют через `StateFlow<UiState>`, а one-off effects - через `SharedFlow<UiEvent>`, `Channel` или explicit callback, в зависимости от архитектуры проекта.

**Коротко:** state описывает, как UI должен выглядеть, а effects описывают одноразовые действия, которые UI должен выполнить.

### One-off events

One-off event - это событие, которое должно быть обработано один раз: показать snackbar, открыть экран, закрыть экран, запросить permission, проскроллить список.

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

**Важно:** `SharedFlow` с `replay = 0` может потерять событие, если collector ещё не активен. Для некритичных UI effects это часто приемлемо, но важные результаты лучше моделировать как часть `UiState`.

Альтернатива - event wrapper или consumable state, но такой подход легко усложняет код. Важно выбирать решение осознанно и не смешивать durable state с transient commands.

**Коротко:** one-off events нужно отделять от persistent UI state, но delivery событий должен быть lifecycle-aware, чтобы избежать дублей или потерянных events.

### State ownership and restoration

`ViewModel` - хороший screen-level state holder, но это не persistent storage. Он переживает обычные configuration changes, например rotation, но не переживает process death автоматически.

Это значит, что `MutableStateFlow` внутри `ViewModel` достаточно для многих обычных обновлений экрана, но недостаточно для state, который будет неприятно или опасно потерять: длинные формы, onboarding progress, checkout steps, unsaved drafts или важный пользовательский ввод.

При проектировании UI state нужно решить, что должно переживать каждую lifecycle boundary:

- recomposition;
- временное исчезновение из composition;
- configuration change;
- уход со screen и возврат назад;
- process death;
- app restart.

Разному state нужны разные owners.

Небольшой локальный UI state может жить в `remember` или `rememberSaveable`. Screen-level state обычно принадлежит `ViewModel`. Небольшой restorable screen state можно хранить через `SavedStateHandle`. Важный durable progress обычно должен храниться в repository, database, DataStore или backend draft, а не только в памяти.

Полезное правило:

```text
remember              -> survives recomposition
rememberSaveable      -> survives recomposition and simple recreation
ViewModel             -> survives configuration change
SavedStateHandle      -> restores small state after process death
Repository / storage  -> persists important state beyond the screen lifecycle
```

Например, profile screen может заново загрузить данные из repository по `profileId`, поэтому весь загруженный профиль не обязательно сохранять в `SavedStateHandle`. Но search query, selected tab, draft comment или current onboarding step могут быть хорошими кандидатами для сохранения.

```kotlin
@HiltViewModel
class SearchViewModel @Inject constructor(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    private var query: String
        get() = savedStateHandle["query"] ?: ""
        set(value) {
            savedStateHandle["query"] = value
        }

    private val _uiState = MutableStateFlow(
        SearchUiState(query = query)
    )
    val uiState: StateFlow<SearchUiState> = _uiState.asStateFlow()

    fun onQueryChanged(newQuery: String) {
        query = newQuery
        _uiState.update { it.copy(query = newQuery) }
    }
}
```

Не стоит складывать всё в `SavedStateHandle`. Он лучше подходит для небольшого serializable restoration state, а не для больших списков, bitmaps, complex object graphs или данных, которые должны быть ответственностью data layer.

Temporary UI scopes - отдельный случай. Некоторый UI state вообще не должен выживать. Например, bottom sheet search session, temporary dialog state или local picker state могут намеренно очищаться, когда этот UI исчезает.

В Compose это означает, что владелец состояния должен соответствовать времени жизни UI. Если state принадлежит всему screen, держите его в screen `ViewModel`. Если он принадлежит только временному UI element, держите его локально в этом элементе или используйте более короткоживущий state holder.

В новых Compose APIs это также можно выразить через scoping `ViewModelStoreOwner` к временному composable subtree, но архитектурное решение остаётся тем же: state owner должен соответствовать ожидаемому lifetime этого UI state.

**Коротко:** `ViewModel` хранит screen state во время жизненного цикла экрана, но restoration - это отдельное проектное решение. Выбирайте owner состояния по тому, как долго state должен жить и насколько плохо будет, если он потеряется.

## Feature design

### Как проектировать feature flow с нуля?

При проектировании feature flow с нуля сначала нужно понять user scenario: какие данные нужны экрану, какие states возможны, какие user actions существуют и какие side effects должны произойти.

Практичный порядок: определить UI contract, описать `UiState`, `UiEvent` и `UserAction`, понять data sources, выбрать owner состояния, затем связать UI -> `ViewModel` -> use cases/repositories -> data sources.

Дальше нужно решить, какие операции являются one-shot suspend functions, а какие - streams `Flow`. Например, загрузить профиль один раз можно suspend-функцией, а наблюдать robot status или database лучше через `Flow`.

State и effects лучше разделять с самого начала: content/loading/error должны быть частью `UiState`, а navigation/snackbar/permission request - отдельными events/effects, если они действительно одноразовые.

Также нужно учитывать lifecycle, process death, retry, offline/cache, error mapping, analytics, testing и module boundaries. Маленькому экрану не нужна идеальная Clean Architecture, но ответственность слоёв должна быть понятной.

Решение о восстановлении состояния должно быть частью feature design, а не мыслью постфактум. Для каждого важного фрагмента state нужно решить, выводится ли он из data sources, хранится ли только в memory, сохраняется ли в `SavedStateHandle`, хранится ли локально или синхронизируется с backend.

Например:

- данные экрана, загружаемые по id, обычно можно заново загрузить из repository;
- search query, selected tab или current step часто можно восстановить из `SavedStateHandle`;
- long draft input или checkout/onboarding progress может требовать local storage или backend draft;
- snackbar/navigation effects обычно не нужно восстанавливать как state;
- temporary sheet/dialog state может намеренно исчезать, когда UI element закрывается.

**Коротко:** начинайте с UI contract и user actions, моделируйте durable `UiState` и one-off effects, решайте, как state должен восстанавливаться, а затем выбирайте, какая логика относится к `ViewModel`, domain/use cases, repositories и data sources.
