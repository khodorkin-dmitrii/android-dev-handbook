# Performance & Memory

Performance и memory topics помогают понимать отзывчивость UI, rendering, leaks, profiling и ограничения Android runtime.

## Responsiveness и rendering

### ANR

ANR (Application Not Responding) - состояние, когда Android считает приложение зависшим, потому что main thread слишком долго не отвечает на события.

Типичные причины: тяжёлая работа на main thread, синхронный I/O, долгие database/network операции, deadlock, блокировка main thread через `wait()` / `join()` / `sleep()` или слишком тяжёлый `BroadcastReceiver`.

Для `Activity` ANR обычно возникает, если приложение не отвечает на input events около 5 секунд. Для `BroadcastReceiver` лимиты зависят от типа receiver и версии Android, поэтому лучше держать работу receiver короткой и делегировать длительные задачи в `WorkManager` / foreground service.

Профилактика: не блокировать main thread, переносить I/O и CPU-heavy work на подходящие dispatchers/thread pools, следить за locks, использовать `StrictMode`, traces и Android Studio Profiler.

**Коротко:** ANR happens when the main thread is blocked long enough that the system cannot process input or lifecycle messages.

### Jank

Jank - заметные рывки UI, когда кадры не успевают отрисоваться вовремя.

При 60 Hz у приложения примерно 16.6 ms на кадр, при 120 Hz - около 8.3 ms. Если main thread или render thread заняты слишком долго, кадр пропускается и пользователь видит лаг.

Причины jank: тяжёлый layout/draw, глубокая hierarchy, синхронная работа на main thread, частые allocations и GC, сложный `RecyclerView` bind, большие images, неправильная работа с animations.

Инструменты: Layout Inspector, Android Profiler, System Trace/Perfetto, Profile GPU Rendering, Macrobenchmark/JankStats.

**Коротко:** jank is missed frame deadlines; fix it by reducing main-thread work, layout/draw cost, allocations and expensive binds.

### Overdraw

Overdraw - ситуация, когда один и тот же pixel рисуется несколько раз за один frame.

Например, если `Activity` background, root layout background и Card background перекрывают друг друга, GPU делает лишнюю работу.

Overdraw не всегда критичен, но сильный overdraw может ухудшать rendering performance, особенно на слабых устройствах или сложных экранах.

Оптимизация: убрать лишние backgrounds, flatten hierarchy, не рисовать невидимые слои, аккуратно использовать alpha/shadows, проверять UI через debugging tools и profiler.

**Коротко:** overdraw is drawing the same pixels multiple times; reduce redundant backgrounds and unnecessary overlapping layers.

## Memory и tooling

### Memory leaks in Android

Memory leak в Android возникает, когда объект уже не нужен, но всё ещё удерживается через strong reference и не может быть собран GC.

Классические причины: хранение `Activity` / `Fragment` / `View Context` в singleton, static references на `View`, callback/listener без отписки, долгоживущая coroutine с reference на UI, `Handler` / `Runnable`, `ViewBinding` после `onDestroyView()`.

Особенно важно помнить Fragment view lifecycle: `Fragment` может жить дольше своей `View`, поэтому binding нужно очищать в `onDestroyView()`, а UI observers привязывать к `viewLifecycleOwner`.

Профилактика: использовать `applicationContext` для долгоживущих объектов, lifecycle-aware collection, weak references только когда это действительно подходит, clear callbacks/listeners, не хранить `View` в `ViewModel`.

**Коротко:** leaks happen when obsolete Android components remain reachable from GC roots, often through singletons, callbacks, static references or wrong lifecycle scope.

### Android Profiler

Android Profiler - инструмент Android Studio для анализа CPU, memory, network, energy и поведения приложения во время выполнения.

CPU profiler помогает искать долгие методы, hot paths, main-thread блокировки и expensive frames. Memory profiler показывает allocations, heap usage, GC activity и помогает найти удерживаемые объекты.

Network profiler полезен для оценки запросов, payload size и timing, хотя для OkHttp/Retrofit часто также используют logging/interceptors и backend tracing.

Profiler лучше использовать вместе с реальными сценариями: slow startup, scrolling, opening heavy screen, loading data, animation.

**Коротко:** Android Profiler helps verify performance hypotheses instead of guessing; it shows CPU, memory, network and energy behavior under real app usage.

Практический workflow, разделяющий investigation и repeatable measurement, описан в [Performance Profiling and Benchmarking](../tools/performance-profiling.md). Работа с утечками разобрана в [Memory Leak Detection](../tools/memory-leaks.md).

### LeakCanary

LeakCanary - библиотека для автоматического обнаружения memory leaks в Android debug builds.

Она отслеживает уничтоженные `Activity`, `Fragment`, `View` и другие объекты, которые должны быть garbage collected, но остаются reachable.

Если объект не собирается, LeakCanary анализирует heap dump и показывает reference chain от GC root до leaked object.

Типичные находки: Fragment view binding leak, listener/callback leak, retained `Activity` context, adapter/view reference, coroutine или lambda, удерживающая UI.

LeakCanary не чинит leak автоматически, но быстро показывает цепочку ссылок и помогает найти владельца лишней reference.

**Коротко:** LeakCanary detects retained objects and shows the reference path that keeps them alive.

### dex / multidex

DEX (Dalvik Executable) - формат bytecode, который выполняет Android Runtime. Java/Kotlin code компилируется в JVM bytecode, а затем Android build tools преобразуют его в DEX.

У DEX есть историческое ограничение около 65K method references на один dex-файл. Если приложение превышает этот лимит, нужен multidex: приложение разбивается на несколько dex-файлов.

На Android 5.0+ ART поддерживает loading multiple dex files нативно. На более старых версиях требовалась support library multidex и специальная инициализация.

Причины роста method count: большие libraries, Google Play Services целиком, DI/generated code, legacy dependencies. Решения: удалить лишние зависимости, использовать более узкие artifacts, R8 shrinking, minification, proguard rules и modularization.

**Коротко:** multidex is a solution for the 64K DEX method reference limit, but first you should reduce method count with dependency cleanup and shrinking.
