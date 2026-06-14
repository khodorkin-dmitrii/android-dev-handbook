# Performance & Memory

Performance and memory topics help understand UI responsiveness, rendering, leaks, profiling and Android runtime constraints.

## Responsiveness and rendering

### ANR

ANR (Application Not Responding) - a state where Android considers the app frozen because the main thread has not responded to events for too long.

Typical causes: heavy work on the main thread, synchronous I/O, long database/network operations, deadlock, blocking the main thread with `wait()` / `join()` / `sleep()` or an overly heavy `BroadcastReceiver`.

For `Activity`, ANR usually occurs if the app does not respond to input events for about 5 seconds. For `BroadcastReceiver`, limits depend on receiver type and Android version, so receiver work should be short and long-running tasks should be delegated to `WorkManager` / foreground service.

Prevention: do not block the main thread, move I/O and CPU-heavy work to appropriate dispatchers/thread pools, watch locks, use `StrictMode`, traces and Android Studio Profiler.

**In short:** ANR happens when the main thread is blocked long enough that the system cannot process input or lifecycle messages.

### Jank

Jank - visible UI stutter when frames are not rendered on time.

At 60 Hz, an app has roughly 16.6 ms per frame; at 120 Hz, about 8.3 ms. If the main thread or render thread is busy for too long, a frame is missed and the user sees lag.

Causes of jank: heavy layout/draw, deep hierarchy, synchronous work on the main thread, frequent allocations and GC, complex `RecyclerView` bind, large images and incorrect animation handling.

Tools: Layout Inspector, Android Profiler, System Trace/Perfetto, Profile GPU Rendering, Macrobenchmark/JankStats.

**In short:** jank is missed frame deadlines; fix it by reducing main-thread work, layout/draw cost, allocations and expensive binds.

### Overdraw

Overdraw - a situation where the same pixel is drawn several times in one frame.

For example, if `Activity` background, root layout background and Card background overlap, the GPU does unnecessary work.

Overdraw is not always critical, but heavy overdraw can hurt rendering performance, especially on weaker devices or complex screens.

Optimization: remove unnecessary backgrounds, flatten hierarchy, avoid drawing invisible layers, use alpha/shadows carefully and inspect UI with debugging tools and profiler.

**In short:** overdraw is drawing the same pixels multiple times; reduce redundant backgrounds and unnecessary overlapping layers.

## Memory and tooling

### Memory leaks in Android

Memory leak in Android happens when an object is no longer needed, but is still held by a strong reference and cannot be collected by GC.

Classic causes: storing `Activity` / `Fragment` / `View Context` in a singleton, static references to `View`, callback/listener without unsubscribe, long-lived coroutine with a UI reference, `Handler` / `Runnable`, `ViewBinding` after `onDestroyView()`.

It is especially important to remember Fragment view lifecycle: a `Fragment` can live longer than its `View`, so binding must be cleared in `onDestroyView()`, and UI observers should be tied to `viewLifecycleOwner`.

Prevention: use `applicationContext` for long-lived objects, lifecycle-aware collection, weak references only when truly appropriate, clear callbacks/listeners and do not store `View` in `ViewModel`.

**In short:** leaks happen when obsolete Android components remain reachable from GC roots, often through singletons, callbacks, static references or wrong lifecycle scope.

### Android Profiler

Android Profiler - an Android Studio tool for analyzing CPU, memory, network, energy and app behavior at runtime.

CPU profiler helps find long methods, hot paths, main-thread blocking and expensive frames. Memory profiler shows allocations, heap usage, GC activity and helps find retained objects.

Network profiler is useful for evaluating requests, payload size and timing, although OkHttp/Retrofit setups often also use logging/interceptors and backend tracing.

Profiler is best used with real scenarios: slow startup, scrolling, opening a heavy screen, loading data and animation.

**In short:** Android Profiler helps verify performance hypotheses instead of guessing; it shows CPU, memory, network and energy behavior under real app usage.

### LeakCanary

LeakCanary - a library for automatic memory leak detection in Android debug builds.

It watches destroyed `Activity`, `Fragment`, `View` and other objects that should be garbage collected, but remain reachable.

If an object is not collected, LeakCanary analyzes the heap dump and shows the reference chain from a GC root to the leaked object.

Typical findings: Fragment view binding leak, listener/callback leak, retained `Activity` context, adapter/view reference, coroutine or lambda holding UI.

LeakCanary does not fix leaks automatically, but it quickly shows the reference chain and helps find the owner of the unnecessary reference.

**In short:** LeakCanary detects retained objects and shows the reference path that keeps them alive.

### dex / multidex

DEX (Dalvik Executable) - the bytecode format executed by Android Runtime. Java/Kotlin code is compiled to JVM bytecode, and then Android build tools transform it into DEX.

DEX has a historical limit of about 65K method references per dex file. If an app exceeds this limit, multidex is needed: the app is split into several dex files.

On Android 5.0+, ART supports loading multiple dex files natively. On older versions, the multidex support library and special initialization were required.

Reasons for method count growth: large libraries, full Google Play Services, DI/generated code and legacy dependencies. Solutions: remove unnecessary dependencies, use narrower artifacts, R8 shrinking, minification, proguard rules and modularization.

**In short:** multidex is a solution for the 64K DEX method reference limit, but first you should reduce method count with dependency cleanup and shrinking.
