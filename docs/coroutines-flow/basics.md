# Coroutines Basics

Coroutines help write asynchronous and concurrent code in a sequential style, without callback hell and manual management of many threads.

**Note:** This article was partly inspired by Phillipp Lackner’s video on threads, coroutines, dispatchers, concurrency and parallelism. The video is a good companion explanation if you prefer a visual walkthrough: [Kotlin Coroutines, Threads, Dispatchers, Concurrency and Parallelism](https://www.youtube.com/watch?v=0Hv5LTxAutw).

## Coroutines basics

### Blocking code vs suspending code

Blocking code keeps the current thread busy until the operation completes.

For example, CPU-heavy work does not "pause" the program. It actively uses the CPU, and the current thread cannot continue with the next instruction until the work is finished:

```kotlin
fun blockingCpuWork(): Long {
    var result = 0L

    repeat(50_000_000) { number ->
        result += number.toLong() * number
    }

    return result
}

fun main() {
    println("Start")
    val result = blockingCpuWork()
    println("End: $result")
}
```

Here `End` is printed only after `blockingCpuWork()` finishes, because the same thread is busy executing the calculation.

Suspending code is different. A coroutine can suspend at a suspension point without keeping the underlying thread busy. While one coroutine is suspended, the same thread can run other coroutines.

Typical suspension points include:

* `delay()`;
* a suspend network call;
* a suspend Room query;
* `withContext()`;
* `await()`.

**Important:** a function marked as `suspend` is not automatically non-blocking. If it performs CPU-heavy work without suspension points, it still blocks the thread where it runs.

**In short:** blocking code keeps a thread busy; suspending code pauses a coroutine and can free the thread for other work.

### Thread as a flow of execution

A thread is an independent flow of execution managed by the operating system.

Code inside one thread is executed in order. If a thread starts a long blocking operation, all later work on that same thread has to wait.

Starting another thread creates another independent flow of execution:

```kotlin
fun main() {
    println("Start")

    Thread {
        blockingCpuWork()
        println("Blocking work finished")
    }.start()

    println("End")
}
```

In this example, `End` can be printed before `Blocking work finished`, because the blocking work was moved to another thread.

In Android, the most important thread is the main thread. It handles UI rendering, input, lifecycle callbacks and most framework interaction. Blocking the main thread with CPU-heavy or blocking I/O work can cause jank or [ANR](../android/performance-memory.md).

Threads are powerful, but they are relatively expensive: each thread has its own stack, OS scheduling overhead and context switching cost. Creating too many threads wastes memory and can make the app slower instead of faster.

**In short:** a thread is an execution flow; blocking work blocks the thread where it runs, and blocking the main thread blocks the UI.

### Concurrency vs parallelism

Concurrency and parallelism are related, but they are not the same.

Parallelism means executing work at the same physical time, usually on multiple CPU cores. For example, two CPU-heavy calculations can run truly in parallel only if there are multiple cores and multiple threads available.

Concurrency means structuring work so multiple tasks can make progress over time. It does not always require true simultaneous execution.

A useful mental model:

* **parallelism** - two people actually doing two tasks at the same time;
* **concurrency** - one person organizing tasks intelligently, using waiting time instead of doing everything strictly one after another.

For example, cooking rice and chicken sequentially takes longer:

```kotlin
suspend fun cookRice() {
    delay(3_000)
}

suspend fun cookChicken() {
    delay(4_000)
}

suspend fun cookSequentially() {
    cookRice()
    cookChicken()
    println("Done")
}
```

The total time is about 7 seconds.

With coroutines, both tasks can be started concurrently:

```kotlin
suspend fun cookConcurrently() = coroutineScope {
    val rice = launch { cookRice() }
    val chicken = launch { cookChicken() }

    rice.join()
    chicken.join()

    println("Done")
}
```

The total time is about 4 seconds, because both operations mostly suspend with `delay()` instead of keeping the thread busy.

This works well for operations with waiting periods: network calls, timers, file I/O, database calls or waiting for external systems. It does not mean that CPU-heavy work becomes faster automatically.

**In short:** parallelism is doing work at the same time; concurrency is organizing work so tasks can make progress efficiently, especially during waiting periods.

### What is a coroutine?

A coroutine is a lightweight suspendable unit of work for asynchronous and concurrent code.

A coroutine is not a thread. It runs on top of a thread or thread pool through a `CoroutineDispatcher`. While it is actively executing code, it needs a thread. When it reaches a suspension point, it can pause without blocking that thread and resume later.

A coroutine can also resume on a different thread depending on dispatcher and context.

In Android, coroutines are usually used for:

* network and database operations;
* parallel loading of independent data;
* timers and delayed actions;
* handling user actions;
* building [Flow-based UI state](flow-basics.md);
* moving blocking or CPU-heavy work away from the main thread.

**In short:** a coroutine is a lightweight suspendable unit of work; it needs a thread only while it is actively running.

### Coroutine vs Thread

A `Thread` is an OS-level execution resource. It has its own stack, is scheduled by the operating system and is relatively expensive.

A coroutine is much lighter. Many coroutines can run on top of a small thread pool. When a coroutine suspends, the thread can be reused by another coroutine.

This is the key difference:

```text
Thread    - execution resource
Coroutine - scheduled unit of suspendable work
```

Coroutines do not replace threads completely. They use threads more efficiently.

For example, thousands of coroutines can wait for network responses without requiring thousands of blocked threads. But if thousands of coroutines all perform CPU-heavy work at the same time, they still need CPU time and appropriate dispatchers.

**Important:** coroutines do not make code automatically parallel. Parallel execution depends on dispatcher, available threads, CPU cores and whether the work is actually independent.

**In short:** threads are OS resources, coroutines are lightweight tasks scheduled on threads; suspension frees the thread, blocking does not.

### What does `suspend` do?

`suspend` means that a function can pause coroutine execution and resume later without blocking the thread.

A suspend function can be called only from another suspend function or from a coroutine.

```kotlin
suspend fun loadUser(): User {
    return api.getUser()
}
```

`suspend` by itself does not:

* create a new thread;
* switch dispatcher;
* make work run in background;
* make CPU-heavy work non-blocking.

For example, this function is still dangerous if called on the main thread:

```kotlin
suspend fun calculateHashes(items: List<String>): List<Int> {
    return items.map { it.hashCode() }
}
```

It is marked as `suspend`, but there is no real suspension point and the CPU work runs on the current thread.

For CPU-heavy work, switch to an appropriate dispatcher:

```kotlin
suspend fun calculateHashes(items: List<String>): List<Int> =
    withContext(Dispatchers.Default) {
        items.map { it.hashCode() }
    }
```

Suspension is cooperative: a coroutine suspends only at suspension points. If code is CPU-bound and never reaches a suspension point, it keeps the thread busy.

**In short:** `suspend` marks a function that can suspend and resume a coroutine; it is not the same as "run on a background thread".

### CPU-bound vs I/O-bound work

Choosing the right dispatcher starts with understanding the type of work.

| Work type      | What happens                                                    | Typical dispatcher    |
| -------------- | --------------------------------------------------------------- | --------------------- |
| UI work        | updates UI and interacts with Android framework                 | `Dispatchers.Main`    |
| CPU-bound work | CPU is actively calculating                                     | `Dispatchers.Default` |
| Blocking I/O   | thread waits for disk, network, database or legacy blocking API | `Dispatchers.IO`      |

CPU-bound work keeps the CPU busy:

* sorting a large list;
* parsing a large JSON manually;
* compressing a bitmap;
* calculating hashes;
* running a heavy mapper over a large collection.

For CPU-bound work, `Dispatchers.Default` is usually the right choice. On JVM it is backed by a shared pool whose parallelism is tied to the number of CPU cores, with exact sizing left to implementation details. This matches the nature of CPU work: if the device has 8 CPU cores, running 80 CPU-heavy tasks at the same physical time will not make the CPU 10 times faster. The tasks mostly compete for the same cores.

I/O-bound work often spends time waiting:

* reading a file;
* writing a file;
* calling a blocking network API;
* using a blocking database driver;
* calling legacy blocking SDK code.

For blocking I/O, `Dispatchers.IO` is usually the right choice. On JVM it is designed for offloading blocking I/O to shared scheduler resources and can allow more concurrent blocking tasks than `Default`, within implementation-defined limits. This larger effective parallelism makes sense because I/O tasks often wait for disk, network or server response, and the CPU often cannot speed up that waiting period.

**Important:** this does not mean `Dispatchers.IO` pre-creates a fixed set of threads for every app or is completely separate from the coroutine scheduler. The practical idea is that `IO` can allow more blocking tasks to wait in parallel than `Default`, while `Default` is intentionally limited for CPU-heavy work.

**In short:** use `Default` for CPU work, `IO` for blocking waiting work and `Main` for UI work.

### Dispatchers and thread pools

`CoroutineDispatcher` controls where coroutine code runs.

A dispatcher usually works over a thread or thread pool:

* `Dispatchers.Main` - Android main thread, used for UI work;
* `Dispatchers.Default` - shared pool for CPU-bound work, with parallelism roughly tied to CPU cores on JVM;
* `Dispatchers.IO` - shared resources for blocking I/O work, able to allow more waiting tasks than `Default` within implementation-defined limits;
* `Dispatchers.Unconfined` - special case, almost never used in regular Android production code.

`Dispatchers.Default` is optimized for CPU-heavy work. Its parallelism is tied to CPU capacity because CPU-bound work benefits from using available CPU cores, not from creating many more competing threads.

`Dispatchers.IO` is optimized for blocking I/O. It can allow more concurrent waiting work and shares implementation resources with the coroutine scheduler rather than being a simple fixed separate pool. More threads can be useful here because many I/O tasks are often waiting, not actively using CPU.

A simplified rule:

```text
CPU is busy calculating        -> Dispatchers.Default
Thread is waiting for I/O      -> Dispatchers.IO
UI needs to be updated         -> Dispatchers.Main
```

A coroutine inherits dispatcher from the parent scope unless another one is specified explicitly:

```kotlin
viewModelScope.launch {
    // Usually runs on Main in Android ViewModel.
}
```

You can switch dispatcher for a specific block with `withContext`:

```kotlin
viewModelScope.launch {
    val user = withContext(Dispatchers.IO) {
        repository.loadUserBlocking()
    }

    // Back to the original context after withContext completes.
    _state.value = UserState.Content(user)
}
```

Avoid switching to `Dispatchers.IO` "just in case". Many modern suspend APIs, such as Retrofit suspend calls or Room suspend queries, already handle threading appropriately. Use explicit dispatcher switching when your code performs blocking work or CPU-heavy work that would otherwise run on the wrong thread.

**In short:** scope controls lifecycle, dispatcher controls where coroutine code runs.

### `withContext`

`withContext` changes coroutine context for a block and suspends until that block completes.

Most often, `withContext` is used to switch dispatcher inside a suspend function:

```kotlin
suspend fun loadImageBytes(path: String): ByteArray =
    withContext(Dispatchers.IO) {
        File(path).readBytes()
    }
```

After the block finishes, execution resumes in the previous context.

`withContext` is not intended for launching several tasks in parallel. It waits for the block result. For parallel independent requests, usually use `coroutineScope` with `async` / `await`.

A good pattern is to make a suspend function safe for its caller by moving the required blocking or CPU-heavy work inside the function:

```kotlin
suspend fun compressBitmap(bitmap: Bitmap): ByteArray =
    withContext(Dispatchers.Default) {
        compress(bitmap)
    }
```

Then callers do not need to remember which dispatcher is correct for that implementation detail.

**In short:** `withContext` changes context for a block and waits for the result; it is useful for dispatcher switching, not for fire-and-forget work.

### `launch` vs `async`

`launch` starts a child coroutine without a returned result and returns `Job`.

It is used when the caller does not need a value from the coroutine:

```kotlin
viewModelScope.launch {
    repository.refresh()
}
```

`async` starts a child coroutine with a result and returns `Deferred<T>`. The result is obtained through `await()`, which suspends until the value is ready:

```kotlin
suspend fun loadScreenData(): ScreenData = coroutineScope {
    val userDeferred = async { repository.loadUser() }
    val itemsDeferred = async { repository.loadItems() }

    ScreenData(
        user = userDeferred.await(),
        items = itemsDeferred.await()
    )
}
```

Use `async` when independent operations can run concurrently and their results are needed to build a final result.

Calling `async` without `await()` is usually a smell. If no result is needed, `launch` is clearer. If a result is needed, make ownership of that result explicit and await it in the parent operation.

Through structured concurrency, child coroutines are tied to their parent scope. If one child fails, the parent can cancel the rest depending on the scope type.

**In short:** `launch` returns `Job` for work without result; `async` returns `Deferred` for concurrent work with result via `await()`.

### Coroutine builders

Coroutine builder is a function that creates a coroutine from a suspend lambda and defines how we interact with its execution.

Common builders and related scope functions:

| API               | Purpose                                                 |
| ----------------- | ------------------------------------------------------- |
| `launch`          | starts a child coroutine without a result               |
| `async`           | starts a child coroutine with a result                  |
| `runBlocking`     | creates a coroutine scope and blocks the current thread |
| `coroutineScope`  | creates a structured scope inside a suspend function    |
| `supervisorScope` | creates a scope where child failures are isolated       |
| `withContext`     | switches context for a block and waits for the result   |

`launch` and `async` start child coroutines inside a `CoroutineScope`.

`coroutineScope` and `supervisorScope` are useful inside suspend functions when you need structured child coroutines without creating an unmanaged scope.

`withContext` is often discussed nearby, but it is not fire-and-forget. It runs a block in another context and waits for it to complete.

In Android, prefer lifecycle-aware scopes:

* `viewModelScope` for work owned by a `ViewModel`;
* `lifecycleScope` for work owned by `Activity` / `Fragment` lifecycle;
* [lifecycle-aware collection](lifecycle-aware-collection.md) APIs for collecting UI flows.

Avoid `GlobalScope` and unmanaged custom scopes for screen work. A coroutine should have a clear owner and should be cancelled when that owner is destroyed or no longer needs the work. For the broader ownership and cancellation model, see [Coroutine Scopes & Cancellation](scopes-cancellation.md).

**In short:** builders start coroutines in a scope; in Android, that scope should usually be lifecycle-aware.

### `runBlocking`

`runBlocking` creates a coroutine scope and blocks the current thread until all coroutines inside it complete.

It is a bridge from blocking code to suspend code:

* `main()` in console examples;
* some tests;
* rare legacy integration points where a caller cannot be made suspend.

```kotlin
fun main() = runBlocking {
    val user = repository.loadUser()
    println(user)
}
```

In Android UI code, `runBlocking` is almost always a mistake. If called on the main thread, it blocks UI rendering, input handling and lifecycle processing. This can cause jank or [ANR](../android/performance-memory.md).

Do not use `runBlocking` to "wait for a coroutine" in production UI code. Make the call chain suspend, launch work from a lifecycle-aware scope or expose state through [`Flow`](flow-basics.md) / [`StateFlow`](stateflow-sharedflow.md). If the work must reliably outlive a screen, use a system-aware API such as [WorkManager](../android/background-work-system-behavior.md) instead of keeping a screen coroutine alive manually.

**In short:** `runBlocking` is a bridge that blocks the current thread; avoid it in Android UI code.
