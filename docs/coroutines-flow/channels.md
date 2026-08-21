# Channels

`Channel` is a coroutine primitive for transferring a sequence of values between producers and receivers.

## Channel basics

### What is a Channel?

A `Channel` is similar to a queue with suspending operations: one coroutine sends values, while another receives and removes them.

It is a hot primitive. A channel exists independently of collectors or receivers, and a producer can start before a receiver appears if the selected capacity allows buffering.

Delivery is point-to-point: one sent element is received by one receiver. If several receivers wait on the same channel, they compete for elements. This differs from `SharedFlow`, which broadcasts each emission to all active subscribers.

**In short:** use `Channel` to coordinate coroutines and transfer ownership of individual elements, not as another kind of `Flow`.

### `send` and `receive`

`send()` suspends when the channel cannot accept another element. `receive()` suspends while no element is available. This coordination lets a consumer slow a producer instead of requiring blocking threads or manual polling.

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

Here the buffer absorbs a limited difference in speed. When it fills, `send()` suspends and applies backpressure. When it is empty, the consumer waits without blocking a thread.

### Capacity and buffering

The capacity determines how far producers can run ahead of receivers:

- `Channel.RENDEZVOUS` - no buffer. Sender and receiver must meet; `send()` waits for a matching receive.
- `Channel.BUFFERED` - uses the library's default buffer capacity. It smooths short bursts, but a full buffer still suspends the producer with the default overflow strategy.
- `Channel.CONFLATED` - keeps only the latest element by replacing an older buffered value. It fits replaceable updates, not work where every item matters.
- `Channel.UNLIMITED` - accepts elements without suspending the sender because of capacity. If production stays faster than consumption, memory usage can grow without a bound.

A small or rendezvous buffer gives stronger backpressure but can reduce throughput. A larger buffer decouples producer and consumer temporarily, at the cost of memory and more in-flight work. Choose capacity from the delivery requirements rather than using `UNLIMITED` to hide a slow consumer.

## Lifetime and stream APIs

### Closing and cancellation

`close()` means that no new elements can be sent. Elements already in the buffer remain available, and receivers can drain them before iteration completes.

Channel cancellation is an abort: it closes the channel and removes buffered elements. Suspended senders and receivers resume with cancellation. Use it when remaining work is no longer needed, not as a synonym for normal completion.

A channel should belong to a clear `CoroutineScope`. When the owner is cancelled, its producer and consumer coroutines should be cancelled with it. Closing a channel does not replace cancellation of the jobs that use it, and closing a channel is not a general way to cancel its producer.

See [Coroutine Scopes & Cancellation](scopes-cancellation.md) for owner-based scopes and structured concurrency.

### Channel vs Flow vs SharedFlow

| Primitive | Main semantics | Typical use |
| --- | --- | --- |
| Regular `Flow` | Usually cold; upstream runs for each collector | Declarative stream of values and transformations |
| `Channel` | Hot point-to-point transfer; each element goes to one receiver | Coordination and work distribution between coroutines |
| `SharedFlow` | Hot broadcast to active subscribers, with configurable replay and buffering | Shared emissions observed by multiple subscribers |
| `StateFlow` | Hot state holder with a current value | Observable state |

`receiveAsFlow()` adapts a `ReceiveChannel` to the Flow API, but it does not add broadcast delivery. With multiple collectors, each channel element is emitted to only one collector.

Use the adapter when Flow operators or a Flow-shaped boundary are useful, while preserving the channel's fan-out semantics. If every active subscriber must see the same emission, use `SharedFlow` instead.

### `channelFlow` and `callbackFlow`

`channelFlow` and `callbackFlow` are Flow builders that use a channel internally. Their result is still a cold `Flow`: the builder block runs separately for each collection.

`channelFlow` is useful when several child coroutines must emit safely and concurrently. A regular `flow {}` builder expects sequential emission from its own context.

`callbackFlow` adapts a multi-shot callback API. Registration and cleanup must follow the collection lifetime:

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

`awaitClose` keeps the callback active until the flow completes or is cancelled and performs cleanup in either case. Buffering can be configured on the resulting flow with `buffer(...)` when the callback can outpace collection.

## Channels in Android UI

### UI events and effects

A `Channel` is not a universal event bus or a guaranteed delivery mechanism for navigation, snackbar messages or other UI effects. A successful `send()` or receipt by a collector does not prove that the UI actually performed the effect.

This matters when a `ViewModel` outlives its UI consumer. During a lifecycle gap, an effect may remain buffered, be handled later in an obsolete context, or be lost through cancellation. No in-memory stream provides exactly-once processing across lifecycle changes or process death without an explicit protocol, acknowledgement and persistence.

Critical results and information that must not be lost should usually be reduced to recoverable `UiState`. Non-critical transient effects may use a separate `Channel`- or `SharedFlow`-based stream when the owner, buffering, lifecycle and delivery semantics are defined explicitly.

**Key idea:** choose `Channel` for point-to-point coordination. For Android UI effects, first decide whether the information is actually durable state and what should happen while no UI consumer is active.

## See also

- [Flow Basics](flow-basics.md)
- [StateFlow & SharedFlow](stateflow-sharedflow.md)
- [Lifecycle-aware Collection](lifecycle-aware-collection.md)
- [UI State Architecture](../architecture/ui-state.md)
