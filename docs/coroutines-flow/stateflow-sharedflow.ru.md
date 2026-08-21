# StateFlow & SharedFlow

`StateFlow` и `SharedFlow` - hot Flow primitives для состояния, событий и shared emissions.

## State и events

### Что такое StateFlow?

`StateFlow` - hot `Flow`, который всегда хранит текущее значение state и сразу отдаёт его новому collector-у.

У `StateFlow` всегда есть initial value. Он хорошо подходит для UI state во `ViewModel`: loading/content/error, form state, selected item, screen data и derived state.

`StateFlow` conflated: если значение быстро меняется, collector обычно получает актуальное последнее значение, а не обязан обработать каждое промежуточное. Также `StateFlow` не emit-ит новое значение, если оно `equals()` старому.

Обычно во `ViewModel` наружу отдают read-only `StateFlow`, а внутри держат `MutableStateFlow`:

```kotlin
private val _uiState = MutableStateFlow(UiState.Loading)
val uiState: StateFlow<UiState> = _uiState.asStateFlow()
```

**Коротко:** `StateFlow` is a hot observable state holder with a current value; it is a good fit for `ViewModel` UI state.

### Что такое SharedFlow?

`SharedFlow` - hot `Flow` для broadcast-style emissions нескольким collectors.

В отличие от `StateFlow`, `SharedFlow` не обязан иметь текущее `value`. Его поведение настраивается через `replay`, `extraBufferCapacity` и `onBufferOverflow`.

`SharedFlow` подходит для событий или streams, где не всегда есть "текущее состояние": navigation events, snackbar messages, refresh triggers, analytics-like events, websocket updates.

В отличие от `Channel`, `SharedFlow` использует broadcast semantics: каждую emission получают все активные subscribers. Канал передаёт каждый элемент одному из конкурирующих receivers. Полное сравнение приведено в статье [Channels](channels.md).

Для one-off UI events часто используют `MutableSharedFlow` с `replay = 0`, чтобы новый collector не получил старое событие автоматически:

```kotlin
private val _events = MutableSharedFlow<UiEvent>()
val events = _events.asSharedFlow()
```

**Важно:** events требуют аккуратного lifecycle-aware collection, иначе событие можно потерять, если collector ещё не активен. Для критичных событий иногда лучше моделировать их как часть state.

**Коротко:** `SharedFlow` is a configurable hot broadcast stream; it is useful for events or shared emissions, not necessarily for state.

### StateFlow vs SharedFlow

`StateFlow` хранит одно текущее значение и всегда имеет initial value. Новый collector сразу получает latest value.

`SharedFlow` более общий: он может иметь replay cache, buffer и не обязан иметь current value. С `replay = 0` новый collector не получает старые emissions.

Для UI state обычно выбирают `StateFlow`, потому что экрану всегда нужно знать текущее состояние. Для one-off events или shared event streams чаще выбирают `SharedFlow`.

`StateFlow` можно представить как специализированный `SharedFlow` для state: `replay = 1`, latest value, equality-based conflation и обязательное initial value.

**Важно:** не стоит хранить navigation/snackbar как простое поле в `StateFlow`, если событие должно быть consumed один раз. Но и `SharedFlow` с `replay = 0` может потерять событие, если collector отсутствует.

**Коротко:** `StateFlow` is for state with a current value, `SharedFlow` is for configurable shared emissions and events.

### StateFlow vs LiveData

`LiveData` - lifecycle-aware observable data holder из AndroidX Lifecycle. Он автоматически учитывает `LifecycleOwner` и активен только в `STARTED` / `RESUMED` состояниях.

`StateFlow` - Kotlin Coroutines primitive. Он не знает Android lifecycle сам по себе, поэтому в UI его нужно collect-ить lifecycle-aware: `collectAsStateWithLifecycle()` в Compose или `repeatOnLifecycle()` во View System.

`StateFlow` лучше интегрируется с coroutines/Flow operators, `combine`, `stateIn`, testing через coroutines test APIs и Kotlin multiplatform-style архитектурой.

`LiveData` всё ещё встречается в legacy Android проектах и простых lifecycle-aware сценариях, но для modern Android Kotlin обычно предпочтительнее `Flow` / `StateFlow`.

**Важно:** если collect-ить `StateFlow` напрямую из `Activity` / `Fragment` без `repeatOnLifecycle`, collection может продолжаться в неподходящем lifecycle state и делать лишнюю работу или обновлять неактивный UI.

**Коротко:** `LiveData` is Android lifecycle-aware by design; `StateFlow` is coroutine-based and needs lifecycle-aware collection on Android.

### State vs events/effects

State описывает текущее состояние экрана и должно быть reproducible: если пересоздать экран и снова отрисовать state, UI должен выглядеть корректно.

Events/effects - одноразовые действия: navigation, snackbar, toast, open dialog, scroll command, permission request. Их не всегда удобно хранить как обычное состояние, потому что они могут повториться после recreation или нового collector-а.

Для state чаще используют `StateFlow<UiState>`. Для некритичных transient effects можно использовать `SharedFlow` или point-to-point stream на основе `Channel`, если lifecycle и delivery semantics определены явно. Канал не гарантирует, что событие от более долгоживущего `ViewModel` действительно будет обработано UI; критичные результаты лучше сводить к восстанавливаемому state. Подробнее см. в [Channels](channels.md).

Главное правило: критичные данные лучше хранить в state. Отдельный effect/event stream подходит для transient commands, только если его lifecycle и поведение при отсутствии активного UI consumer-а определены заранее.

```kotlin
sealed interface UiEvent {
    data class ShowSnackbar(val message: String) : UiEvent
    data object NavigateBack : UiEvent
}
```

**Коротко:** state is durable and describes what the UI should show; events/effects are one-time actions and need careful lifecycle handling.
