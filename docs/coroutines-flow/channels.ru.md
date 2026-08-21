# Channels

`Channel` - coroutine primitive для передачи последовательности значений между producers и receivers.

## Основы Channel

### Что такое Channel?

`Channel` похож на очередь с suspending operations: одна coroutine отправляет значения, а другая получает и удаляет их.

Это hot primitive. Канал существует независимо от collectors или receivers, а producer может начать работу до появления receiver, если выбранная capacity допускает buffering.

Delivery имеет point-to-point семантику: один отправленный элемент получает один receiver. Если один канал ожидают несколько receivers, они конкурируют за элементы. Этим `Channel` отличается от `SharedFlow`, который передаёт каждую emission всем активным subscribers.

**Коротко:** `Channel` используют для координации coroutines и передачи отдельных элементов, а не как ещё одну разновидность `Flow`.

### `send` и `receive`

`send()` приостанавливается, когда канал не может принять следующий элемент. `receive()` приостанавливается, пока доступных элементов нет. Такая координация позволяет consumer-у замедлять producer без блокировки threads и ручного polling.

```kotlin
suspend fun syncPendingItems(repository: ItemRepository) = coroutineScope {
    val itemIds = Channel<String>(capacity = Channel.BUFFERED)

    val producer = launch {
        try {
            repository.pendingIds().forEach { itemIds.send(it) }
        } finally {
            itemIds.close()
        }
    }

    val consumer = launch {
        for (id in itemIds) {
            repository.sync(id)
        }
    }

    joinAll(producer, consumer)
}
```

Здесь buffer сглаживает ограниченную разницу в скорости. Когда он заполнен, `send()` приостанавливается и создаёт backpressure. Когда buffer пуст, consumer ожидает, не блокируя thread.

### Capacity и buffering

Capacity определяет, насколько producer может опередить receiver:

- `Channel.RENDEZVOUS` - buffer отсутствует. Sender и receiver должны встретиться, поэтому `send()` ждёт соответствующий receive.
- `Channel.BUFFERED` - используется default buffer capacity библиотеки. Она сглаживает короткие всплески, но при default overflow strategy заполненный buffer всё равно приостанавливает producer.
- `Channel.CONFLATED` - хранит только последний элемент, заменяя предыдущее buffered значение. Подходит для заменяемых updates, но не для работы, где важен каждый элемент.
- `Channel.UNLIMITED` - принимает элементы, не приостанавливая sender из-за capacity. Если producer постоянно быстрее consumer-а, использование памяти может расти без ограничений.

Маленький buffer или rendezvous дают более строгий backpressure, но могут уменьшить throughput. Большой buffer временно разделяет скорости producer и consumer ценой памяти и большего числа in-flight элементов. Capacity следует выбирать по требованиям к delivery, а не использовать `UNLIMITED`, чтобы скрыть медленный consumer.

## Lifetime и stream APIs

### Закрытие и cancellation

`close()` означает, что новые элементы больше нельзя отправлять. Уже находящиеся в buffer элементы остаются доступными, и receivers могут обработать их до завершения iteration.

Cancellation канала означает аварийное прекращение работы: канал закрывается, а buffered элементы удаляются. Приостановленные senders и receivers возобновляются с cancellation. Используйте cancellation, когда оставшаяся работа больше не нужна, а не как синоним нормального завершения.

У канала должен быть понятный владелец `CoroutineScope`. При cancellation владельца его producer и consumer coroutines должны отменяться вместе с ним. Закрытие канала не заменяет cancellation использующих его jobs и не является общим способом отменить producer.

Подробнее об owner-based scopes и structured concurrency см. в [Coroutine Scopes & Cancellation](scopes-cancellation.md).

### Channel vs Flow vs SharedFlow

| Primitive | Основная семантика | Типичное применение |
| --- | --- | --- |
| Обычный `Flow` | Обычно cold; upstream запускается для каждого collector-а | Декларативный stream значений и transformations |
| `Channel` | Hot point-to-point передача; каждый элемент получает один receiver | Координация и распределение работы между coroutines |
| `SharedFlow` | Hot broadcast активным subscribers с настраиваемыми replay и buffering | Shared emissions для нескольких subscribers |
| `StateFlow` | Hot state holder с текущим значением | Observable state |

`receiveAsFlow()` адаптирует `ReceiveChannel` к Flow API, но не добавляет broadcast delivery. При нескольких collectors каждый элемент канала emit-ится только одному collector-у.

Используйте adapter, когда нужны Flow operators или API в форме `Flow`, сохраняя fan-out семантику канала. Если одну emission должны получить все активные subscribers, используйте `SharedFlow`.

### `channelFlow` и `callbackFlow`

`channelFlow` и `callbackFlow` - Flow builders, которые используют канал внутри. Результат всё равно остаётся cold `Flow`: block builder-а запускается отдельно для каждого collection.

`channelFlow` полезен, когда несколько child coroutines должны безопасно emit-ить concurrently. Обычный builder `flow {}` рассчитан на последовательные emissions из своего context.

`callbackFlow` адаптирует multi-shot callback API. Регистрация и cleanup должны соответствовать lifetime collection:

```kotlin
fun LocationClient.locations(): Flow<Location> = callbackFlow {
    val listener = object : LocationListener {
        override fun onLocation(location: Location) {
            trySend(location)
        }

        override fun onError(error: Throwable) {
            close(error)
        }
    }

    register(listener)
    awaitClose { unregister(listener) }
}
```

`awaitClose` сохраняет callback активным до завершения или cancellation flow и в обоих случаях выполняет cleanup. Если callback может опережать collection, buffering настраивают у полученного flow через `buffer(...)`.

## Channels в Android UI

### UI events и effects

`Channel` - не универсальный event bus и не гарантированный механизм delivery для navigation, snackbar messages и других UI effects. Успешный `send()` или получение элемента collector-ом не доказывает, что UI действительно выполнил effect.

Это важно, когда `ViewModel` живёт дольше UI consumer-а. Во время lifecycle gap effect может остаться в buffer, быть обработан позже в уже неактуальном context или потеряться при cancellation. Ни один in-memory stream не обеспечивает exactly-once processing через lifecycle changes или process death без explicit protocol, acknowledgement и persistence.

Критичные результаты и данные, которые нельзя потерять, обычно следует сводить к восстанавливаемому `UiState`. Для некритичных transient effects можно использовать отдельный stream на основе `Channel` или `SharedFlow`, если его owner, buffering, lifecycle и delivery semantics определены явно.

**Главная мысль:** выбирайте `Channel` для point-to-point координации. Для Android UI effects сначала определите, не является ли информация durable state и что должно произойти, пока активного UI consumer-а нет.

## См. также

- [Flow Basics](flow-basics.md)
- [StateFlow & SharedFlow](stateflow-sharedflow.md)
- [Lifecycle-aware Collection](lifecycle-aware-collection.md)
- [UI State Architecture](../architecture/ui-state.md)
