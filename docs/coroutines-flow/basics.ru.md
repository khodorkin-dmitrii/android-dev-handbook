# Coroutines Basics

Coroutines помогают писать асинхронный и конкурентный код в последовательном стиле, без callback hell и ручного управления большим количеством threads.

## Основы coroutines

### Что такое coroutine?

Coroutine - это легковесная suspendable computation для асинхронного и конкурентного кода.

Coroutine не равна `Thread`: она выполняется поверх thread/thread pool через `CoroutineDispatcher` и может suspend-иться, освобождая поток для другой работы.

В Android coroutines обычно используют для network/database операций, параллельной загрузки независимых данных, таймеров, обработки user actions и построения Flow-based state.

**Коротко:** coroutine is a lightweight suspendable unit of work; it can suspend without blocking the underlying thread.

### Coroutine vs Thread

`Thread` - системный поток выполнения, которым управляет OS. У него есть собственный stack, context switching дорогой, и большое количество threads быстро расходует память.

Coroutine намного легче: многие coroutines могут работать поверх небольшого thread pool. Когда coroutine достигает suspension point, она может приостановиться без блокировки thread, а thread продолжит выполнять другую работу.

**Важно:** coroutines не делают код автоматически parallel. Parallel execution зависит от dispatcher, доступных threads и того, есть ли реально независимая работа.

**Коротко:** threads are OS resources, coroutines are lightweight tasks scheduled on threads; suspension frees the thread, blocking does not.

### Что делает `suspend`?

`suspend` означает, что функция может приостановить выполнение coroutine и продолжить позже, не блокируя thread.

`suspend` сам по себе не создаёт новый thread, не переключает dispatcher и не делает функцию background. Если вызвать suspend-функцию на Main dispatcher и внутри будет CPU-heavy работа без suspension, она всё равно может заблокировать UI.

Suspend-функцию можно вызвать только из другой suspend-функции или из coroutine. Типичные suspension points: `delay()`, network call, Room query, `withContext()`, `await()`.

**Коротко:** `suspend` marks a function that can suspend and resume a coroutine; it is not the same as "run on background thread".

### `launch` vs `async`

`launch` запускает coroutine без возвращаемого результата и возвращает `Job`. Его используют для fire-and-forget задач внутри scope: обновить state, отправить analytics, запустить collection или выполнить действие, результат которого не нужен вызывающему коду.

`async` запускает coroutine с результатом и возвращает `Deferred<T>`. Результат получают через `await()`, который suspend-ится до готовности значения.

`async` стоит использовать, когда действительно нужен result или параллельное выполнение независимых задач. Если вызвать `async` и никогда не вызвать `await()`, это smell: ошибки и результат могут быть обработаны неявно или потеряны.

**Коротко:** `launch` returns `Job` for work without result; `async` returns `Deferred` for concurrent computation with result via `await()`.

### Coroutine builders

Coroutine builder - функция, которая создаёт coroutine из suspend lambda и определяет, как мы взаимодействуем с её выполнением.

Основные builders: `launch`, `async`, `runBlocking`. Также часто рядом обсуждают `coroutineScope`, `supervisorScope` и `withContext`, хотя `withContext` скорее переключает context внутри текущей suspend-функции, чем создаёт независимую child coroutine для fire-and-forget.

Builders должны запускаться внутри `CoroutineScope` или создавать scope сами. Это важно для structured concurrency: coroutine не должна жить хаотично вне управляемого lifecycle.

**Коротко:** builders start coroutines in a scope and return a handle like `Job` or `Deferred` depending on whether result is needed.

### Dispatchers

`CoroutineDispatcher` определяет, на каком thread или thread pool будет выполняться coroutine.

`Dispatchers.Main` используют для UI work на main thread. `Dispatchers.IO` - для blocking I/O: network, files, database, legacy blocking APIs. `Dispatchers.Default` - для CPU-bound работы: parsing, sorting, calculations. `Unconfined` почти не используют в обычном Android production-коде.

Coroutine наследует dispatcher из parent scope, если явно не указан другой. В Android важно не делать тяжёлую работу на Main dispatcher и не переключаться на IO "на всякий случай", если библиотека уже предоставляет suspend non-blocking API.

**Коротко:** scope controls lifecycle, dispatcher controls where coroutine runs.

### `withContext`

`withContext` переключает coroutine context для выполнения блока и suspend-ится до завершения этого блока.

Чаще всего `withContext` используют для смены dispatcher внутри suspend-функции: например, выполнить blocking I/O на `Dispatchers.IO`, затем вернуться в исходный context после блока.

`withContext` не предназначен для параллельного запуска нескольких задач. Для параллельных независимых запросов обычно используют `coroutineScope` + `async` / `await`.

**Коротко:** `withContext` changes context for a block and waits for the result; it is useful for dispatcher switching, not for fire-and-forget work.

### `runBlocking`

`runBlocking` создаёт coroutine scope и блокирует текущий thread, пока все coroutines внутри него не завершатся.

Он нужен как bridge из blocking мира в suspend world: `main()` в консольных примерах, некоторые tests, legacy API, где нельзя сделать функцию suspend.

В Android UI-коде `runBlocking` почти всегда ошибка: если вызвать его на main thread, можно заблокировать UI и получить jank или ANR.

**Коротко:** `runBlocking` is a bridge that blocks the current thread; avoid it in Android UI code.
