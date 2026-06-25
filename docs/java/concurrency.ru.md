# Java Concurrency

Темы Java concurrency, которые помогают понимать legacy Java-код, Android internals и низкоуровневую модель многопоточности: `Thread`, `volatile`, `synchronized`, `wait()` / `notify()`, `Executor`, `Future`, atomic classes и `java.util.concurrent`.

## Потоки и синхронизация

### `Thread`

`Thread` - базовая единица выполнения в Java. Когда вызывается `start()`, JVM создаёт новый поток выполнения и вызывает `run()` внутри этого нового потока.

Поток завершится, когда метод `run()` дойдёт до конца или выбросит необработанное исключение. Останавливать поток через `stop()` нельзя: это unsafe API. Обычно используют cooperative cancellation через `interrupt()`, флаг, `Future` cancellation или higher-level concurrency APIs.

Чтобы дождаться результата снаружи, можно использовать `join()`, `Future` / `Callable`, `CountDownLatch`, callback или shared state с правильной синхронизацией. В Android для нового Kotlin-кода чаще используют coroutines, но понимать raw `Thread` полезно для legacy-кода.

### `volatile` vs `synchronized`

`volatile` гарантирует visibility: если один thread записал новое значение volatile-поля, другие threads увидят актуальное значение. Также `volatile` задаёт happens-before relationship для чтения/записи этой переменной.

Но `volatile` не делает составные операции атомарными. Например, `counter++` всё равно не thread-safe, потому что это чтение, изменение и запись.

`synchronized` даёт mutual exclusion: только один thread может выполнять protected block на одном monitor. Также `synchronized` обеспечивает visibility изменений при входе и выходе из monitor. Для простого флага может хватить `volatile`, для критической секции и compound operations нужен `synchronized`, lock или atomic classes.

Пример volatile-флага:

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

Здесь `volatile` подходит для простого флага: один thread меняет значение, другой гарантированно видит актуальное значение. Но если нужно выполнить compound operation, `volatile` уже недостаточно.

Пример synchronized-счётчика:

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

Здесь `synchronized` защищает критическую секцию: `increment()` выполняется атомарно относительно других synchronized-методов на том же объекте, а изменения видны другим threads после выхода из monitor.

### `wait()` / `notify()` / `notifyAll()`

`wait()`, `notify()` и `notifyAll()` - низкоуровневые методы `Object` для координации threads через monitor.

Их можно вызывать только внутри `synchronized`-блока или `synchronized`-метода на том же объекте-мониторе. `wait()` освобождает monitor и приостанавливает thread, `notify()` будит один ожидающий thread, `notifyAll()` будит всех ожидающих.

На практике `wait()` почти всегда используют в `while`-loop с проверкой условия, потому что возможны spurious wakeups. В современном коде чаще предпочитают `java.util.concurrent`, locks, queues, coroutines или reactive primitives.

## Higher-level concurrency APIs

### `Executor`

`Executor` - abstraction для запуска задач без ручного управления `Thread`. Вместо `new Thread(...).start()` код передаёт `Runnable` в `Executor`, а конкретная реализация решает, где и когда его выполнить.

Чаще всего используют `ExecutorService` и thread pools: fixed thread pool, cached thread pool, single-thread executor. Это позволяет переиспользовать threads, ограничивать параллелизм и управлять `shutdown()`.

**Коротко:** `Executor` отделяет описание задачи от механизма её выполнения. В Android raw `Executor` встречается в legacy/Java-коде, а в Kotlin-коде часто заменяется coroutines и `Dispatchers`.

### `Callable` / `Future`

`Runnable` описывает задачу без результата, а `Callable<T>` описывает задачу, которая возвращает значение или бросает exception.

`Future<T>` представляет результат асинхронной операции. Через `get()` можно дождаться результата, но важно помнить: `get()` блокирует текущий thread, поэтому его нельзя вызывать на Android main thread.

`Future` также позволяет проверить состояние задачи и попытаться отменить её через `cancel()`. В современном Android-коде похожую роль часто играют `suspend` functions, `Deferred` или `Flow`, но `Callable` / `Future` важно знать для Java concurrency и legacy APIs.

### Atomic

Atomic classes из `java.util.concurrent.atomic` дают lock-free thread-safe операции над отдельными значениями: `AtomicInteger`, `AtomicBoolean`, `AtomicReference` и другие.

Они полезны для простых counters, flags и compare-and-set логики. Например, `AtomicInteger.incrementAndGet()` атомарен, в отличие от обычного `counter++`.

Но Atomic не заменяет полноценную синхронизацию для сложного состояния из нескольких полей. Если нужно атомарно менять несколько связанных значений, лучше использовать `synchronized`, `Lock` или другую модель state management.

## ConcurrentHashMap

### Предварительные темы

- [HashMap complexity](../engineering/algorithms-complexity.md#collections-arraylist-linkedlist-hashmap-and-hashset-complexity)

`ConcurrentHashMap` - thread-safe реализация `Map` для shared maps, которые читают и обновляют несколько threads.

Обычный `HashMap` небезопасен при concurrent writes: один thread может увидеть stale data, перезаписать update другого thread или оставить map во внутренне неконсистентном состоянии. `Collections.synchronizedMap(...)` оборачивает каждую операцию одним общим lock, что просто, но часто снижает concurrency и всё равно требует ручной синхронизации во время итерации. `ConcurrentHashMap` обычно лучше подходит для активно разделяемых maps, потому что он спроектирован для concurrent access и даёт атомарные операции над map.

Базовый пример:

```java
ConcurrentMap<String, Integer> counts = new ConcurrentHashMap<>();

counts.put("success", 1);
counts.putIfAbsent("failure", 0);
counts.merge("success", 1, Integer::sum);
```

**Важно:** отдельные операции thread-safe, но составные check-then-act sequences не становятся атомарными автоматически:

```java
if (!map.containsKey(key)) {
    map.put(key, value);
}
```

Между `containsKey()` и `put()` другой thread может обновить тот же key. Когда одно логическое обновление должно выполниться как единая операция, лучше использовать атомарные API: `putIfAbsent()`, `computeIfAbsent()`, `compute()` или `merge()`.

### Связанные темы

- `synchronized`
- `volatile`
- `ReadWriteLock`

## `java.util.concurrent`

`java.util.concurrent` - пакет Java с high-level инструментами для многопоточности: `ExecutorService`, `Future`, `BlockingQueue`, `CountDownLatch`, `Semaphore`, `ConcurrentHashMap`, locks, atomic classes и др.

Его цель - дать более безопасные и удобные примитивы, чем ручное управление `Thread`, `wait()` / `notify()` и shared mutable state.

**Главная мысль:** базу `Thread` / `synchronized` / `wait()` важно понимать, но в production чаще используют более высокоуровневые инструменты из `java.util.concurrent` или, в modern Android Kotlin, coroutines.
