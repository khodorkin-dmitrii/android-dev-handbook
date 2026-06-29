# Coroutines Basics

Coroutines помогают писать асинхронный и конкурентный код в последовательном стиле, без callback hell и ручного управления большим количеством threads.

## Coroutines basics

### Blocking code vs suspending code

Blocking code удерживает текущий thread занятым, пока операция не завершится.

Например, CPU-heavy работа не "ставит программу на паузу". Она активно использует CPU, и текущий thread не может перейти к следующей инструкции, пока работа не закончится:

```kotlin
fun blockingCpuWork() {
    (1..50_000_000).map { number ->
        number * number
    }
}

fun main() {
    println("Start")
    blockingCpuWork()
    println("End")
}
```

Здесь `End` печатается только после завершения `blockingCpuWork()`, потому что тот же thread занят вычислением.

Suspending code работает иначе. Coroutine может suspend-иться в suspension point, не удерживая underlying thread занятым. Пока одна coroutine suspended, тот же thread может выполнять другие coroutines.

Типичные suspension points:

* `delay()`;
* suspend network call;
* suspend Room query;
* `withContext()`;
* `await()`.

**Важно:** функция, помеченная как `suspend`, не становится автоматически non-blocking. Если она выполняет CPU-heavy работу без suspension points, она всё равно блокирует thread, на котором запущена.

**Коротко:** blocking code удерживает thread занятым; suspending code приостанавливает coroutine и может освободить thread для другой работы.

### Thread as a flow of execution

Thread - это независимый поток выполнения, которым управляет operating system.

Код внутри одного thread выполняется по порядку. Если thread запускает долгую blocking operation, вся последующая работа на этом же thread должна ждать.

Запуск другого thread создаёт другой независимый flow of execution:

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

В этом примере `End` может быть напечатан раньше `Blocking work finished`, потому что blocking work перенесли в другой thread.

В Android самый важный thread - main thread. Он обрабатывает UI rendering, input, lifecycle callbacks и большую часть interaction с framework. Если заблокировать main thread CPU-heavy работой или blocking I/O, можно получить jank или [ANR](../android/performance-memory.md).

Threads мощные, но относительно дорогие: у каждого thread есть свой stack, overhead планирования OS и стоимость context switching. Слишком много threads расходуют memory и могут замедлить приложение вместо ускорения.

**Коротко:** thread - это flow of execution; blocking work блокирует thread, на котором выполняется, а блокировка main thread блокирует UI.

### Concurrency vs parallelism

Concurrency и parallelism связаны, но это не одно и то же.

Parallelism означает выполнение работы в одно и то же физическое время, обычно на нескольких CPU cores. Например, две CPU-heavy задачи могут реально выполняться параллельно только если доступны несколько cores и несколько threads.

Concurrency означает организацию работы так, чтобы несколько задач могли продвигаться со временем. Для этого не всегда нужно настоящее одновременное выполнение.

Полезная mental model:

* **parallelism** - два человека действительно делают две задачи одновременно;
* **concurrency** - один человек грамотно организует задачи и использует время ожидания, а не делает всё строго по очереди.

Например, если готовить рис и курицу последовательно, это займёт больше времени:

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

Общее время - около 7 секунд.

С coroutines обе задачи можно начать concurrently:

```kotlin
suspend fun cookConcurrently() = coroutineScope {
    val rice = launch { cookRice() }
    val chicken = launch { cookChicken() }

    rice.join()
    chicken.join()

    println("Done")
}
```

Общее время - около 4 секунд, потому что обе операции в основном suspend-ятся через `delay()`, а не удерживают thread занятым.

Это хорошо работает для операций с периодами ожидания: network calls, timers, file I/O, database calls или ожидание внешних систем. Это не значит, что CPU-heavy работа автоматически станет быстрее.

**Коротко:** parallelism - это выполнение работы одновременно; concurrency - организация работы так, чтобы задачи эффективно продвигались, особенно во время ожидания.

### What is a coroutine?

Coroutine - это легковесная suspendable unit of work для асинхронного и конкурентного кода.

Coroutine не является thread. Она выполняется поверх thread или thread pool через `CoroutineDispatcher`. Пока coroutine активно выполняет код, ей нужен thread. Когда она достигает suspension point, она может приостановиться без блокировки thread и продолжиться позже.

Coroutine также может продолжиться на другом thread в зависимости от dispatcher и context.

В Android coroutines обычно используют для:

* network и database операций;
* параллельной загрузки независимых данных;
* timers и delayed actions;
* обработки user actions;
* построения [Flow-based UI state](flow-basics.md);
* переноса blocking или CPU-heavy работы с main thread.

**Коротко:** coroutine - это lightweight suspendable unit of work; thread нужен ей только во время активного выполнения.

### Coroutine vs Thread

`Thread` - это OS-level execution resource. У него есть собственный stack, он планируется operating system и стоит относительно дорого.

Coroutine намного легче. Много coroutines могут выполняться поверх небольшого thread pool. Когда coroutine suspend-ится, thread может быть переиспользован другой coroutine.

Ключевое отличие:

```text
Thread    - execution resource
Coroutine - scheduled unit of suspendable work
```

Coroutines не заменяют threads полностью. Они используют threads эффективнее.

Например, тысячи coroutines могут ждать network responses без тысяч заблокированных threads. Но если тысячи coroutines одновременно выполняют CPU-heavy работу, им всё равно нужны CPU time и подходящие dispatchers.

**Важно:** coroutines не делают код автоматически parallel. Parallel execution зависит от dispatcher, доступных threads, CPU cores и того, действительно ли работа независима.

**Коротко:** threads - это OS resources, coroutines - lightweight tasks, запланированные на threads; suspension освобождает thread, blocking - нет.

### What does `suspend` do?

`suspend` означает, что функция может приостановить выполнение coroutine и продолжить позже без блокировки thread.

Suspend function можно вызвать только из другой suspend function или из coroutine.

```kotlin
suspend fun loadUser(): User {
    return api.getUser()
}
```

`suspend` сам по себе не:

* создаёт новый thread;
* переключает dispatcher;
* запускает работу в background;
* делает CPU-heavy работу non-blocking.

Например, эта функция всё ещё опасна, если вызвать её на main thread:

```kotlin
suspend fun calculateHashes(items: List<String>): List<Int> {
    return items.map { it.hashCode() }
}
```

Она помечена как `suspend`, но в ней нет реального suspension point, и CPU work выполняется на текущем thread.

Для CPU-heavy работы переключайся на подходящий dispatcher:

```kotlin
suspend fun calculateHashes(items: List<String>): List<Int> =
    withContext(Dispatchers.Default) {
        items.map { it.hashCode() }
    }
```

Suspension cooperative: coroutine suspend-ится только в suspension points. Если код CPU-bound и никогда не достигает suspension point, он удерживает thread занятым.

**Коротко:** `suspend` помечает функцию, которая может приостанавливать и продолжать coroutine; это не то же самое, что "запустить на background thread".

### CPU-bound vs I/O-bound work

Выбор правильного dispatcher начинается с понимания типа работы.

| Work type      | Что происходит                                                | Typical dispatcher    |
| -------------- | ------------------------------------------------------------- | --------------------- |
| UI work        | обновляет UI и взаимодействует с Android framework            | `Dispatchers.Main`    |
| CPU-bound work | CPU активно вычисляет                                         | `Dispatchers.Default` |
| Blocking I/O   | thread ждёт disk, network, database или legacy blocking API   | `Dispatchers.IO`      |

CPU-bound work удерживает CPU занятым:

* сортировка большого списка;
* ручной parsing большого JSON;
* сжатие bitmap;
* вычисление hashes;
* тяжёлый mapper по большой collection.

Для CPU-bound work обычно подходит `Dispatchers.Default`. На JVM он использует shared pool, максимальный размер которого равен числу CPU cores, но не меньше двух threads. Это соответствует природе CPU work: если у device 8 CPU cores, запуск 80 CPU-heavy задач в одно и то же физическое время не сделает CPU в 10 раз быстрее. Задачи в основном будут конкурировать за те же cores.

I/O-bound work часто проводит время в ожидании:

* чтение файла;
* запись файла;
* вызов blocking network API;
* использование blocking database driver;
* вызов legacy blocking SDK code.

Для blocking I/O обычно подходит `Dispatchers.IO`. На JVM он предназначен для offloading blocking I/O в shared pool, а default parallelism limit равен 64 threads или числу CPU cores, если cores больше. Такой больший лимит логичен, потому что I/O tasks часто ждут disk, network или server response, и CPU часто не может ускорить это ожидание.

**Важно:** это не значит, что `Dispatchers.IO` заранее создаёт 64 threads для каждого app. Дополнительные threads создаются и завершаются по мере необходимости. Практическая идея в том, что `IO` может позволить большему числу blocking tasks ждать параллельно, чем `Default`, а `Default` намеренно ограничен для CPU-heavy work.

**Коротко:** используй `Default` для CPU work, `IO` для blocking waiting work и `Main` для UI work.

### Dispatchers and thread pools

`CoroutineDispatcher` определяет, где выполняется coroutine code.

Dispatcher обычно работает поверх thread или thread pool:

* `Dispatchers.Main` - Android main thread, используется для UI work;
* `Dispatchers.Default` - shared pool для CPU-bound work, на JVM ограничен числом CPU cores, но имеет минимум два threads;
* `Dispatchers.IO` - shared pool для blocking I/O work, с default parallelism limit 64 threads или числом CPU cores, если оно больше;
* `Dispatchers.Unconfined` - special case, почти не используется в обычном Android production code.

`Dispatchers.Default` оптимизирован для CPU-heavy work. Его parallelism ограничен, потому что CPU-bound work выигрывает от использования доступных CPU cores, а не от создания большого числа конкурирующих threads.

`Dispatchers.IO` оптимизирован для blocking I/O. Он может использовать больший pool, потому что многие I/O tasks большую часть времени ждут disk, network или external systems. Здесь больше threads могут быть полезны, потому что большинство из них часто ждут, а не активно используют CPU.

Упрощённое правило:

```text
CPU is busy calculating        -> Dispatchers.Default
Thread is waiting for I/O      -> Dispatchers.IO
UI needs to be updated         -> Dispatchers.Main
```

Coroutine наследует dispatcher из parent scope, если явно не указан другой:

```kotlin
viewModelScope.launch {
    // Usually runs on Main in Android ViewModel.
}
```

Переключить dispatcher для конкретного блока можно через `withContext`:

```kotlin
viewModelScope.launch {
    val user = withContext(Dispatchers.IO) {
        repository.loadUserBlocking()
    }

    // Back to the original context after withContext completes.
    _state.value = UserState.Content(user)
}
```

Не переключайся на `Dispatchers.IO` "на всякий случай". Многие современные suspend APIs, например Retrofit suspend calls или Room suspend queries, уже корректно обрабатывают threading. Явно переключай dispatcher, когда твой код выполняет blocking work или CPU-heavy work, которая иначе запустится на неправильном thread.

**Коротко:** scope контролирует lifecycle, dispatcher контролирует, где выполняется coroutine code.

### `withContext`

`withContext` меняет coroutine context для блока и suspend-ится до завершения этого блока.

Чаще всего `withContext` используют, чтобы переключить dispatcher внутри suspend function:

```kotlin
suspend fun loadImageBytes(path: String): ByteArray =
    withContext(Dispatchers.IO) {
        File(path).readBytes()
    }
```

После завершения блока выполнение продолжается в предыдущем context.

`withContext` не предназначен для запуска нескольких задач параллельно. Он ждёт результат блока. Для параллельных независимых requests обычно используют `coroutineScope` с `async` / `await`.

Хороший pattern - сделать suspend function безопасной для caller-а, перенеся нужную blocking или CPU-heavy работу внутрь функции:

```kotlin
suspend fun compressBitmap(bitmap: Bitmap): ByteArray =
    withContext(Dispatchers.Default) {
        compress(bitmap)
    }
```

Тогда callers не должны помнить, какой dispatcher корректен для этой implementation detail.

**Коротко:** `withContext` меняет context для блока и ждёт результат; он полезен для dispatcher switching, а не для fire-and-forget работы.

### `launch` vs `async`

`launch` запускает child coroutine без возвращаемого результата и возвращает `Job`.

Его используют, когда caller-у не нужно значение из coroutine:

```kotlin
viewModelScope.launch {
    repository.refresh()
}
```

`async` запускает child coroutine с результатом и возвращает `Deferred<T>`. Результат получают через `await()`, который suspend-ится до готовности значения:

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

Используй `async`, когда независимые операции могут выполняться concurrently и их результаты нужны для построения итогового результата.

Вызов `async` без `await()` обычно smell. Если результат не нужен, `launch` понятнее. Если результат нужен, явно оформи ownership этого результата и дождись его в parent operation.

Через structured concurrency child coroutines привязаны к parent scope. Если один child падает, parent может отменить остальные в зависимости от типа scope.

**Коротко:** `launch` возвращает `Job` для работы без результата; `async` возвращает `Deferred` для concurrent work с результатом через `await()`.

### Coroutine builders

Coroutine builder - это функция, которая создаёт coroutine из suspend lambda и определяет, как мы взаимодействуем с её выполнением.

Common builders и связанные scope functions:

| API               | Purpose                                                 |
| ----------------- | ------------------------------------------------------- |
| `launch`          | запускает child coroutine без результата                |
| `async`           | запускает child coroutine с результатом                 |
| `runBlocking`     | создаёт coroutine scope и блокирует текущий thread      |
| `coroutineScope`  | создаёт structured scope внутри suspend function        |
| `supervisorScope` | создаёт scope, где ошибки child coroutines изолированы  |
| `withContext`     | переключает context для блока и ждёт результат          |

`launch` и `async` запускают child coroutines внутри `CoroutineScope`.

`coroutineScope` и `supervisorScope` полезны внутри suspend functions, когда нужны structured child coroutines без создания unmanaged scope.

`withContext` часто обсуждают рядом, но это не fire-and-forget. Он выполняет блок в другом context и ждёт его завершения.

В Android предпочитай lifecycle-aware scopes:

* `viewModelScope` для работы, которой владеет `ViewModel`;
* `lifecycleScope` для работы, которой владеет lifecycle `Activity` / `Fragment`;
* APIs для [lifecycle-aware collection](lifecycle-aware-collection.md), когда UI собирает flows.

Избегай `GlobalScope` и unmanaged custom scopes для screen work. У coroutine должен быть понятный owner, и она должна отменяться, когда owner уничтожен или работа больше не нужна. Подробнее про ownership и cancellation см. в [Coroutine Scopes & Cancellation](scopes-cancellation.md).

**Коротко:** builders запускают coroutines в scope; в Android этот scope обычно должен быть lifecycle-aware.

### `runBlocking`

`runBlocking` создаёт coroutine scope и блокирует текущий thread, пока все coroutines внутри него не завершатся.

Это bridge из blocking code в suspend code:

* `main()` в console examples;
* некоторые tests;
* редкие legacy integration points, где caller нельзя сделать suspend.

```kotlin
fun main() = runBlocking {
    val user = repository.loadUser()
    println(user)
}
```

В Android UI code `runBlocking` почти всегда ошибка. Если вызвать его на main thread, он блокирует UI rendering, input handling и lifecycle processing. Это может привести к jank или [ANR](../android/performance-memory.md).

Не используй `runBlocking`, чтобы "подождать coroutine" в production UI code. Сделай call chain suspend, запускай работу из lifecycle-aware scope или отдавай state через [`Flow`](flow-basics.md) / [`StateFlow`](stateflow-sharedflow.md). Если работа должна гарантированно пережить экран, используй system-aware API вроде [WorkManager](../android/background-work-system-behavior.md), а не удерживай screen coroutine вручную.

**Коротко:** `runBlocking` - это bridge, который блокирует текущий thread; избегай его в Android UI code.
