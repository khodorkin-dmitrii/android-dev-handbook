# Java Concurrency

Java threading fundamentals for Android and legacy Java code: `Thread`, visibility, monitors, executors, futures, atomic values and concurrent collections. Java examples make the underlying APIs explicit; the same shared-state rules matter in Kotlin.

## Threads and Synchronization

### `Thread`

`start()` starts a thread that executes `run()`; directly calling `run()` is an ordinary call on the current thread. A thread can be started only once. It terminates when its work returns or an exception escapes.

Cancellation is cooperative: `interrupt()` requests a response, not forced termination. Code must check interruption or use interruptible blocking calls. `sleep()`, `wait()` and `join()` can throw `InterruptedException`, clearing the interrupt status. Propagate it, or restore the status with `Thread.currentThread().interrupt()` and exit appropriately; do not silently swallow it. Never use `Thread.stop()`.

`join()` waits for termination, not a return value. Use `Callable` / `Future` for results. Blocking waits and long-running work do not belong on Android's main thread.

### `volatile` vs `synchronized`

A write to a `volatile` field happens-before subsequent reads of that field. This also publishes preceding writes, but does not freeze the referenced object's future state or make `counter++` atomic.

```java
class SharedResource {
    private volatile boolean flag = false;

    public void setFlagTrue() {
        flag = true;
    }

    public boolean isFlag() {
        return flag;
    }
}
```

This flag needs visibility, not a multi-step update. A flag alone does not wake a blocked thread.

`synchronized` combines mutual exclusion with visibility: unlocking happens-before a subsequent lock of the **same monitor**. Instance synchronized methods lock `this`; static ones lock the declaring class's `Class` object.

```java
class SharedCounter {
    private int counter = 0;

    public synchronized void increment() {
        counter++;
    }

    public synchronized int getCounter() {
        return counter;
    }
}
```

Both reads and writes use the same monitor. Unsynchronized access is not protected merely because another method is synchronized. Keep critical sections short and use consistent lock ordering to avoid deadlocks. `Thread.sleep()` neither releases monitors nor establishes visibility.

### `wait()` / `notify()` / `notifyAll()`

These `Object` methods require ownership of the target monitor; otherwise they throw `IllegalMonitorStateException`.

- `wait()` releases that monitor, but not other locks held by the thread. It reacquires the monitor before returning.
- `notify()` selects one waiter, with no ordering guarantee; `notifyAll()` signals all waiters.
- Notification does not release the monitor or immediately transfer execution to a waiter.
- Always check the condition in a `while` loop: spurious wakeups and competing consumers can invalidate it. A notification is not stored for future waiters.

For a reusable condition, read and update its state under the same monitor. Prefer `BlockingQueue`, latches or other higher-level tools to hand-written wait/notify protocols.

## Higher-level concurrency APIs

### `Executor`

`Executor.execute(Runnable)` separates a task from its execution policy. It does **not** guarantee a background thread: an implementation may execute inline.

`ExecutorService` adds task submission, futures and lifecycle management. Reuse a pool with clear ownership. `shutdown()` rejects new tasks but lets accepted tasks finish; it does not wait for termination. `shutdownNow()` attempts interruption and returns tasks that never started; running tasks may continue if they ignore interruption.

Pool size is not the only limit: fixed pools can accumulate an unbounded task queue, while cached pools can create many threads. Choose queue bounds and rejection behavior deliberately for sustained workloads.

### `Callable` / `Future`

`Runnable` has no result; `Callable<T>` returns a value and may throw. `Future<T>.get()` waits for completion and returns the result, or throws `ExecutionException` for task failure or `CancellationException` after cancellation. The waiting thread can also be interrupted.

`get(timeout, unit)` limits waiting, not task execution; a timeout does not automatically cancel the task. `cancel(true)` may interrupt a running task, but does not guarantee that its code stops. `isDone()` includes failure and cancellation, not just success.

In Kotlin Android code, scoped coroutines and `Deferred` often provide a more natural result/cancellation model. They do not automatically make blocking Java code cancellable.

### Atomic

`AtomicInteger`, `AtomicBoolean` and `AtomicReference` support atomic operations on individual values without requiring a caller-managed monitor. `incrementAndGet()` is atomic; separate `get()` and `set()` calls are not one atomic update. Avoid promising that every implementation is strictly lock-free.

`compareAndSet(expected, update)` changes a value only if it still matches the expected value; `AtomicReference` compares references by identity. Update functions used by `updateAndGet()` may be retried, so keep them free of side effects.

Several atomic fields do not form a transaction. Protect related state with one lock, or replace an immutable state object atomically. An atomic reference does not protect mutations inside its referenced object.

## ConcurrentHashMap

### Prerequisites

- [HashMap complexity](../engineering/algorithms-complexity.md#collections-arraylist-linkedlist-hashmap-and-hashset-complexity)

`HashMap` needs external synchronization when shared with concurrent writers. `Collections.synchronizedMap(...)` serializes access through its wrapper; iteration still requires locking that wrapper.

`ConcurrentHashMap` supports concurrent access and atomic per-key updates, without a whole-map transaction:

```java
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;

ConcurrentMap<String, Integer> counts = new ConcurrentHashMap<>();
counts.put("success", 1);
counts.putIfAbsent("failure", 0);
counts.merge("success", 1, Integer::sum);
```

Separate `containsKey()` and `put()` calls can race. Use `putIfAbsent()`, `computeIfAbsent()`, `compute()` or `merge()` for a single logical update. Keep computation callbacks short and avoid recursive map updates.

Null keys and values are forbidden. Iterators are weakly consistent, not snapshots; aggregate observations such as `size()` can change during concurrent updates. Thread safety of the map does not make its mutable values thread-safe.

## `java.util.concurrent`

Useful tools beyond executors and maps:

- `BlockingQueue`: producer/consumer handoff, optionally bounded.
- `CountDownLatch`: one-shot wait for a count to reach zero.
- `Semaphore`: limit concurrent access using permits.
- `Lock` / `ReadWriteLock`: explicit locking policies; release acquired locks in `finally`.

On Android, keep blocking operations off the main thread and tie task ownership to the appropriate lifecycle. Check the Android API level or desugaring support before using newer Java APIs.

## Related topics

- [Java Core](core.md)
- [Coroutines Basics](../coroutines-flow/basics.md)
- [Coroutine Scopes & Cancellation](../coroutines-flow/scopes-cancellation.md)

## References

- [Java memory model and monitors](https://docs.oracle.com/javase/specs/jls/se25/html/jls-17.html)
- [Thread](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Thread.html) and [Object wait/notify](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Object.html)
- [Android Executor](https://developer.android.com/reference/java/util/concurrent/Executor) and [ExecutorService](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/ExecutorService.html)
- [Future](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/Future.html)
- [Atomic classes](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/atomic/package-summary.html)
- [ConcurrentHashMap](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/ConcurrentHashMap.html)
