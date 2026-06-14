# Coroutines Basics

Coroutines help write asynchronous and concurrent code in a sequential style, without callback hell and manual management of many threads.

## Coroutines basics

### What is a coroutine?

Coroutine - a lightweight suspendable computation for asynchronous and concurrent code.

A coroutine is not the same as `Thread`: it runs on top of a thread/thread pool through `CoroutineDispatcher` and can suspend, freeing the thread for other work.

In Android, coroutines are usually used for network/database operations, parallel loading of independent data, timers, handling user actions and building Flow-based state.

**In short:** coroutine is a lightweight suspendable unit of work; it can suspend without blocking the underlying thread.

### Coroutine vs Thread

`Thread` - a system execution thread managed by the OS. It has its own stack, context switching is expensive, and a large number of threads quickly consumes memory.

Coroutine is much lighter: many coroutines can run on top of a small thread pool. When a coroutine reaches a suspension point, it can pause without blocking the thread, and the thread can continue doing other work.

**Important:** coroutines do not make code automatically parallel. Parallel execution depends on dispatcher, available threads and whether there is actually independent work.

**In short:** threads are OS resources, coroutines are lightweight tasks scheduled on threads; suspension frees the thread, blocking does not.

### What does `suspend` do?

`suspend` means that a function can pause coroutine execution and resume later without blocking the thread.

`suspend` by itself does not create a new thread, does not switch dispatcher and does not make a function background. If a suspend function is called on Main dispatcher and contains CPU-heavy work without suspension, it can still block UI.

A suspend function can be called only from another suspend function or from a coroutine. Typical suspension points: `delay()`, network call, Room query, `withContext()`, `await()`.

**In short:** `suspend` marks a function that can suspend and resume a coroutine; it is not the same as "run on background thread".

### `launch` vs `async`

`launch` starts a coroutine without a returned result and returns `Job`. It is used for fire-and-forget tasks inside a scope: update state, send analytics, start collection or perform an action whose result is not needed by the caller.

`async` starts a coroutine with a result and returns `Deferred<T>`. The result is obtained through `await()`, which suspends until the value is ready.

Use `async` when a result or parallel execution of independent tasks is actually needed. Calling `async` and never calling `await()` is a smell: errors and result may be handled implicitly or lost.

**In short:** `launch` returns `Job` for work without result; `async` returns `Deferred` for concurrent computation with result via `await()`.

### Coroutine builders

Coroutine builder - a function that creates a coroutine from a suspend lambda and defines how we interact with its execution.

Main builders: `launch`, `async`, `runBlocking`. `coroutineScope`, `supervisorScope` and `withContext` are often discussed nearby, although `withContext` rather switches context inside the current suspend function than creates an independent child coroutine for fire-and-forget work.

Builders should be launched inside `CoroutineScope` or create a scope themselves. This matters for structured concurrency: a coroutine should not live chaotically outside a managed lifecycle.

**In short:** builders start coroutines in a scope and return a handle like `Job` or `Deferred` depending on whether result is needed.

### Dispatchers

`CoroutineDispatcher` defines on which thread or thread pool a coroutine will run.

`Dispatchers.Main` is used for UI work on the main thread. `Dispatchers.IO` - for blocking I/O: network, files, database, legacy blocking APIs. `Dispatchers.Default` - for CPU-bound work: parsing, sorting, calculations. `Unconfined` is almost never used in regular Android production code.

A coroutine inherits dispatcher from the parent scope unless another one is specified explicitly. In Android, avoid heavy work on Main dispatcher and avoid switching to IO "just in case" if a library already provides a suspend non-blocking API.

**In short:** scope controls lifecycle, dispatcher controls where coroutine runs.

### `withContext`

`withContext` switches coroutine context for a block and suspends until that block completes.

Most often, `withContext` is used to switch dispatcher inside a suspend function: for example, run blocking I/O on `Dispatchers.IO`, then return to the original context after the block.

`withContext` is not intended for launching several tasks in parallel. For parallel independent requests, usually use `coroutineScope` + `async` / `await`.

**In short:** `withContext` changes context for a block and waits for the result; it is useful for dispatcher switching, not for fire-and-forget work.

### `runBlocking`

`runBlocking` creates a coroutine scope and blocks the current thread until all coroutines inside it complete.

It is needed as a bridge from the blocking world to the suspend world: `main()` in console examples, some tests, legacy APIs where a function cannot be made suspend.

In Android UI code, `runBlocking` is almost always a mistake: if called on the main thread, it can block UI and cause jank or ANR.

**In short:** `runBlocking` is a bridge that blocks the current thread; avoid it in Android UI code.
