# Flow Basics

`Flow<T>` - основанный на coroutines поток, который может выдавать значения во времени, а затем завершиться успешно или с ошибкой.

## Основы Flow

### Что такое Flow?

`Flow` полезен, когда значение может изменяться или приходить несколько раз: обновления базы данных, поисковый ввод, состояние UI, прогресс, polling или realtime-события. Если suspension и coroutine scopes пока незнакомы, начни со статьи [Coroutines Basics](basics.md).

У Flow есть три основные части:

1. **Producer** выдаёт значения.
2. Промежуточные операторы преобразуют их.
3. Терминальный оператор запускает collection и обрабатывает результат.

```kotlin
fun observeVisibleUsers(): Flow<List<User>> =
    userDao.observeUsers()              // Flow<List<User>>
        .map { users -> users.filter(User::isVisible) }

suspend fun printVisibleUsers() {
    observeVisibleUsers().collect { users ->
        println(users)
    }
}
```

Операторы `map`, `filter`, `combine` и `distinctUntilChanged` возвращают новый `Flow`, но не запускают его. `collect`, `first`, `single` и `toList` - терминальные операторы. Большинство терминальных операторов являются suspending-функциями.

Обычно значения проходят через Flow последовательно: следующий оператор не начинает обработку нового значения, пока не готов к нему. Операторы `buffer`, `conflate` и `flatMapMerge` могут изменить это поведение, когда конкурентная обработка или пропуск промежуточных значений нужны явно.

### Flow и suspend-функция

Suspend-функция обычно возвращает один результат или выбрасывает одно исключение. Она подходит для one-shot операций: `login()`, `fetchUser()` или `saveSettings()`.

`Flow` нужен, когда во времени может прийти несколько значений: cached data, затем fresh data, обновления базы, прогресс загрузки или меняющийся статус устройства.

Если нужен только один ответ, suspend-функция обычно проще. Оборачивание каждого одиночного запроса во `Flow` добавляет семантику collection и cancellation без реальной пользы.

### Cold Flow и Hot Flow

Большинство Flow, созданных через `flow { ... }`, `flowOf(...)` или преобразования в repository, являются **cold**. Producer запускается для каждой терминальной операции, поэтому два collector-а могут повторить upstream-работу - включая два сетевых запроса.

```kotlin
val userFlow = flow {
    emit(api.loadUser())
}

userFlow.collect(::renderUser) // Выполняет api.loadUser()
userFlow.collect(::cacheUser)  // Выполняет его снова
```

**Hot** Flow существует независимо от конкретного collector-а. `StateFlow` хранит последнее состояние, а `SharedFlow` рассылает значения согласно настройкам replay и buffering.

В Android cold flow из repository часто преобразуют в `StateFlow` во `ViewModel` через `stateIn(...)`. Scope и политика `SharingStarted` определяют, как долго будет активна общая collection upstream-а.

`Channel` тоже является hot-примитивом, но это отдельный механизм коммуникации, а не subtype `Flow`. По умолчанию каждый элемент Channel обрабатывает один receiver; подробнее см. в статье [Channels](channels.md).

### Collection, context и cancellation

`collect` - suspending-терминальный оператор, который выполняется в collecting coroutine. Cold flow использует coroutine context collector-а, если upstream context не изменён через `flowOn`. `flowOn` влияет только на операторы выше него и не переносит collector на другой dispatcher.

Collection подчиняется structured concurrency. Отмена collecting coroutine отменяет collection и cold upstream. В Android UI используй lifecycle-aware API, например `repeatOnLifecycle` или `collectAsStateWithLifecycle`, чтобы работа прекращалась, когда UI больше не нуждается в данных.

Не поглощай `CancellationException` в общей обработке ошибок: cancellation - это управляющий сигнал, а не обычная ошибка.

### Обработка ошибок

Необработанное upstream-исключение завершает Flow и выбрасывается терминальным оператором. `catch` обрабатывает только исключения из расположенных перед ним операторов и не перехватывает cancellation или ошибки downstream-блока `collect`.

```kotlin
repository.observeUsers()
    .map(::toUiModel)
    .catch { error -> emit(UserUiModel.Error(error)) }
    .collect(::render)
```

Используй `catch` для ожидаемых восстанавливаемых ошибок или выдачи явного error state. Неожиданные ошибки обычно следует пробрасывать дальше, а не незаметно превращать в пустые данные.

### `collect` и `collectLatest`

`collect` обрабатывает каждое значение до конца. Если обработка медленная, последующие значения ждут, если только buffering или конкурентные операторы не изменили pipeline.

`collectLatest` при появлении нового значения отменяет предыдущий collector block и запускает его с последним значением. Это полезно для search-as-you-type, быстрых изменений фильтра или rendering, когда старый результат уже не актуален.

Не используй `collectLatest`, если каждое значение обязательно должно быть обработано, например для audit logging, платежей или критичных операций записи: cancellation может прервать предыдущий block на середине.
