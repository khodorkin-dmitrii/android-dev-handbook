# Flow Basics

`Flow` - coroutine-based stream данных, который позволяет описывать несколько asynchronous значений во времени.

## Основы Flow

### Что такое Flow?

`Flow` - asynchronous stream данных из Kotlin Coroutines, который может emit-ить несколько значений во времени.

Обычный `Flow` по умолчанию cold: код внутри `flow { ... }` не запускается, пока его не начнут collect-ить.

`Flow` используют для наблюдения за изменениями: database updates, search input, UI state, realtime updates, polling, websocket-like streams и объединение нескольких источников данных.

```kotlin
fun observeUser(id: String): Flow<User> = flow {
    emit(api.getUser(id))
}
```

**Коротко:** `Flow` is a coroutine-based asynchronous stream; by default it is cold and starts when collected.

### Flow vs suspend function

Suspend function обычно возвращает один результат или одну ошибку. Она хорошо подходит для one-shot операций: `login()`, `fetchUser()`, `saveSettings()`, `sendAnalytics()`.

`Flow` подходит, когда значений может быть несколько во времени: сначала cached data, потом fresh data, затем database updates или realtime status updates.

Если нужен один ответ - чаще проще и понятнее suspend function. Если нужен stream обновлений или reactive chain - `Flow`.

Типичный pitfall: использовать `Flow` для простого одиночного запроса и усложнить API без реальной пользы.

**Коротко:** `suspend` is for a single asynchronous result, `Flow` is for multiple values over time.

### Cold Flow vs Hot Flow

Cold Flow начинает работу только при collection. Каждый новый collector обычно заново запускает upstream.

Например, если внутри `flow { api.load() }`, то два collector-а могут запустить два отдельных API call.

Hot Flow существует независимо от конкретного collector-а и может хранить или emit-ить значения даже без активных подписчиков. `StateFlow` и `SharedFlow` - hot flows.

В Android часто превращают cold flow из repository в hot `StateFlow` во `ViewModel` через `stateIn(viewModelScope, SharingStarted.WhileSubscribed(...), initialValue)`, чтобы UI получил стабильное состояние и upstream не запускался хаотично.

**Коротко:** cold flows are started by collectors, hot flows live independently of collectors.

### `collect` vs `collectLatest`

`collect` обрабатывает каждое значение до конца. Если приходит новое значение, оно ждёт, пока предыдущая обработка завершится.

`collectLatest` отменяет обработку предыдущего значения, если пришло новое. Это полезно, когда старый результат уже не актуален.

Типичные примеры `collectLatest`: search-as-you-type, быстрые изменения фильтра, обновление UI, где важен только последний input.

**Важно:** `collectLatest` отменяет body collection, поэтому его нельзя использовать там, где каждое значение обязательно должно быть обработано, например audit/logging/critical write operation.

**Коротко:** `collect` processes every emission, `collectLatest` cancels previous processing when a new value arrives.
