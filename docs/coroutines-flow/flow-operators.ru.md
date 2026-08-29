# Flow Operators

Flow operators строят pipeline между producer и collector. При выборе оператора важно не то, какой из них короче, а что должно происходить с порядком, cancellation, ошибками и медленными consumers.

Cold и hot flow, collection и context подробнее разобраны в статье [Flow Basics](flow-basics.md).

## Преобразование и фильтрация

Большинство промежуточных операторов lazy: они возвращают новый `Flow` и выполняются только после запуска терминального оператора.

| Задача | Оператор |
| --- | --- |
| Преобразовать каждое значение | `map` |
| Оставить подходящие значения | `filter` / `filterNotNull` |
| Пропустить последовательные одинаковые значения | `distinctUntilChanged` |
| Выполнить side effect, не меняя значение | `onEach` |
| Оставить или пропустить часть потока | `take`, `drop`, `takeWhile` |

```kotlin
userDao.observeUsers()
    .map { users -> users.filter(User::isVisible) }
    .distinctUntilChanged()
    .onEach { users -> analytics.logVisibleCount(users.size) }
```

`distinctUntilChanged` сравнивает соседние значения через `equals`. Применять его непосредственно к `StateFlow` избыточно: `StateFlow` уже не выдаёт последовательные равные значения.

### `map` и `flatMapLatest`

Используй `map`, когда одно входное значение превращается в одно выходное, в том числе если преобразование вызывает suspend-функцию.

Оператор `flatMap*` нужен, когда каждое входное значение создаёт новый `Flow`:

| Оператор | Inner flows |
| --- | --- |
| `flatMapConcat` | собираются последовательно с сохранением порядка |
| `flatMapMerge` | собираются конкурентно; результаты могут перемешиваться |
| `flatMapLatest` | предыдущий inner flow отменяется при новом входном значении |

```kotlin
selectedUserId
    .distinctUntilChanged()
    .flatMapLatest(repository::observeUser)
    .map(User::toUiModel)
```

Так можно описать наблюдение за выбранным пользователем: смена ID отменяет устаревшую подписку. Не используй `flatMapLatest`, если каждая внутренняя операция обязана завершиться, например для критичной записи.

## Объединение нескольких Flow

`combine`, `zip` и `merge` решают разные задачи:

| Оператор | Результат |
| --- | --- |
| `combine` | после первого значения от каждого источника пересчитывает результат при изменении любого из них |
| `zip` | объединяет значения попарно и завершается, когда завершился один из источников |
| `merge` | передаёт значения совместимых Flow по мере поступления без гарантий порядка между источниками |

Для построения UI state обычно подходит `combine`:

```kotlin
combine(userFlow, balanceFlow, cardsFlow) { user, balance, cards ->
    UiState(user, balance, cards)
}
```

Используй `zip`, только если значения действительно образуют пары. `merge` подходит для равнозначных событий, например нажатия кнопки обновления и pull-to-refresh gesture.

## Время и медленные collectors

Для поискового ввода часто используют несколько операторов вместе:

```kotlin
queryFlow
    .debounce(300)
    .distinctUntilChanged()
    .flatMapLatest(repository::search)
```

`debounce` выдаёт значение, когда источник не менялся в течение заданного интервала. Это уменьшает число запросов при быстром вводе, но намеренно добавляет задержку.

По умолчанию Flow выполняется последовательно, поэтому медленный downstream может приостановить upstream. При необходимости выбери явную стратегию:

| Оператор | Поведение при медленном consumer |
| --- | --- |
| `buffer` | позволяет upstream и downstream работать параллельно; хранит значения до заполнения buffer |
| `conflate` | пропускает промежуточные значения, сохраняя последнее |
| `collectLatest` | отменяет предыдущий collector block ради нового значения |

`conflate` и `collectLatest` подходят, только если старые значения теряют актуальность. Они опасны для логов, платежей, команд и других потоков, где важно каждое значение.

## Ошибки, retry и завершение

`retry` и `retryWhen` перезапускают upstream flow после подходящей ошибки. `retryWhen` также получает номер повторной попытки с нуля и может приостановиться для backoff:

```kotlin
repository.observeData()
    .retryWhen { cause, attempt ->
        if (cause !is IOException || attempt >= 3) return@retryWhen false
        delay(500L * (1L shl attempt.toInt()))
        true
    }
    .map(Data::toUiState)
    .catch { error -> emit(UiState.Error(error)) }
```

Порядок операторов важен: `retryWhen` должен находиться перед `catch`, потому что `catch` обрабатывает ошибку вместо её повторного выбрасывания. Оба оператора прозрачны для downstream-ошибок и cancellation.

Повторяй только transient и idempotent операции. Payment или запись могут выполниться дважды без idempotency key или проверки результата.

`onStart` может выдать loading state перед запуском upstream. `onCompletion` наблюдает обычное завершение, ошибку или cancellation, но, в отличие от `catch`, сам по себе не обрабатывает исключение.

## Терминальные операторы

Терминальные операторы запускают collection:

| Задача | Оператор |
| --- | --- |
| Обработать каждое значение | `collect` |
| Получить первое значение и отменить upstream | `first` / `firstOrNull` |
| Потребовать ровно одно значение | `single` / `singleOrNull` |
| Собрать конечный Flow в коллекцию | `toList` |
| Запустить collection в переданном scope | `launchIn` |

Не вызывай `toList` или `single` для hot или другого незавершающегося Flow: они будут ждать completion, который может никогда не наступить.
