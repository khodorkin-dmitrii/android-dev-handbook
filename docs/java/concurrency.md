# Java Concurrency

Java concurrency topics that help with understanding legacy Java code, Android internals and the low-level threading model: `Thread`, `volatile`, `synchronized`, `wait()` / `notify()`, `Executor`, `Future`, atomic classes and `java.util.concurrent`.

## Threads and Synchronization

### `Thread`

`Thread` is the basic unit of execution in Java. When `start()` is called, the JVM creates a new execution thread and calls `run()` inside that new thread.

The thread finishes when `run()` reaches the end or throws an unhandled exception. Do not stop a thread with `stop()`: it is an unsafe API. Usually cooperative cancellation is used through `interrupt()`, a flag, `Future` cancellation or higher-level concurrency APIs.

To wait for a result from the outside, use `join()`, `Future` / `Callable`, `CountDownLatch`, a callback or shared state with proper synchronization. In Android, new Kotlin code usually uses coroutines, but understanding raw `Thread` is useful for legacy code.

### `volatile` vs `synchronized`

`volatile` guarantees visibility: if one thread writes a new value to a volatile field, other threads will see the current value. `volatile` also establishes a happens-before relationship for reads/writes of that variable.

But `volatile` does not make compound operations atomic. For example, `counter++` is still not thread-safe because it consists of read, modify and write.

`synchronized` provides mutual exclusion: only one thread can execute a protected block on the same monitor. It also ensures visibility of changes when entering and exiting the monitor. `volatile` can be enough for a simple flag; a critical section and compound operations need `synchronized`, a lock or atomic classes.

Example of a volatile flag:

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

Here `volatile` is suitable for a simple flag: one thread changes the value, another thread is guaranteed to see the current value. But if a compound operation is needed, `volatile` is no longer enough.

Example of a synchronized counter:

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

Here `synchronized` protects the critical section: `increment()` executes atomically relative to other synchronized methods on the same object, and changes are visible to other threads after exiting the monitor.

### `wait()` / `notify()` / `notifyAll()`

`wait()`, `notify()` and `notifyAll()` are low-level `Object` methods for coordinating threads through a monitor.

They can be called only inside a `synchronized` block or `synchronized` method on the same monitor object. `wait()` releases the monitor and suspends the thread, `notify()` wakes one waiting thread, and `notifyAll()` wakes all waiting threads.

In practice, `wait()` is almost always used in a `while` loop with a condition check because spurious wakeups are possible. Modern code usually prefers `java.util.concurrent`, locks, queues, coroutines or reactive primitives.

## Higher-level concurrency APIs

### `Executor`

`Executor` is an abstraction for running tasks without manual `Thread` management. Instead of `new Thread(...).start()`, code passes a `Runnable` to `Executor`, and the concrete implementation decides where and when to execute it.

Most often code uses `ExecutorService` and thread pools: fixed thread pool, cached thread pool, single-thread executor. This allows threads to be reused, parallelism to be limited and `shutdown()` to be managed.

**In short:** `Executor` separates task description from the execution mechanism. In Android, raw `Executor` appears in legacy/Java code, while Kotlin code often replaces it with coroutines and `Dispatchers`.

### `Callable` / `Future`

`Runnable` describes a task without a result, while `Callable<T>` describes a task that returns a value or throws an exception.

`Future<T>` represents the result of an asynchronous operation. `get()` can wait for the result, but remember: `get()` blocks the current thread, so it must not be called on the Android main thread.

`Future` also allows checking task state and attempting cancellation through `cancel()`. In modern Android code, a similar role is often played by `suspend` functions, `Deferred` or `Flow`, but `Callable` / `Future` are important for Java concurrency and legacy APIs.

### Atomic

Atomic classes from `java.util.concurrent.atomic` provide lock-free thread-safe operations on individual values: `AtomicInteger`, `AtomicBoolean`, `AtomicReference` and others.

They are useful for simple counters, flags and compare-and-set logic. For example, `AtomicInteger.incrementAndGet()` is atomic, unlike regular `counter++`.

But atomic classes do not replace full synchronization for complex state made of several fields. If several related values need to change atomically, use `synchronized`, `Lock` or another state-management model.

### `java.util.concurrent`

`java.util.concurrent` is a Java package with high-level concurrency tools: `ExecutorService`, `Future`, `BlockingQueue`, `CountDownLatch`, `Semaphore`, `ConcurrentHashMap`, locks, atomic classes and more.

Its goal is to provide safer and more convenient primitives than manual `Thread` management, `wait()` / `notify()` and shared mutable state.

**Key idea:** the basics of `Thread` / `synchronized` / `wait()` are important to understand, but production code usually uses higher-level tools from `java.util.concurrent` or, in modern Android Kotlin, coroutines.
