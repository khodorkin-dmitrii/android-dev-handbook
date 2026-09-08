# Performance & Memory

Performance work is about keeping interactions responsive, rendering frames on time, and using memory within the device's limits. Start with a reproducible user scenario and measurements; optimize only after locating a real bottleneck.

## Responsiveness and rendering

### ANR

ANR (Application Not Responding) means that the system decided an app component did not respond within its deadline. The best-known case is an input event waiting about five seconds, but services, broadcast receivers, and `JobService` callbacks also have their own time limits.

Common causes include synchronous I/O or expensive computation on the main thread, slow Binder calls, lock contention, deadlocks, and blocking calls such as `wait()`, `join()`, or `sleep()`. A `BroadcastReceiver` can also trigger an ANR by doing too much work in `onReceive()` or by using `goAsync()` without finishing its `PendingResult` in time.

Keep component callbacks short, move blocking I/O and CPU-heavy work to suitable dispatchers or executors, and avoid holding locks while calling slow code. Use `StrictMode` during development and inspect ANR traces or Android vitals in production. Moving work off the main thread helps responsiveness, but it does not make unsafe shared state or unbounded work correct.

See [Background Work & System Behavior](background-work-system-behavior.md) for choosing between `WorkManager`, foreground services, and other background APIs.

### Jank

Jank is visible stutter caused by frames missing their display deadlines. At 60 Hz a frame interval is about 16.7 ms; at 90 Hz it is about 11.1 ms, and at 120 Hz about 8.3 ms. Work on the main thread, RenderThread, GPU, or other parts of the rendering pipeline can all contribute.

Typical causes are expensive measure/layout/draw passes, heavy composition or binding, synchronous work on the main thread, frequent allocations and garbage collection, image decoding, and poorly coordinated animations. A frame budget is an end-to-end deadline, not a safe allowance for one application method.

Reproduce the problem in a release-like build, preferably on a representative slower device. Use System Trace or Perfetto to locate slow frames, then narrow the cause with Android Studio Profiler, Layout Inspector, custom trace sections, JankStats, or Macrobenchmark. Measure again after the change.

### Overdraw

Overdraw occurs when the same pixel is drawn multiple times in one frame. For example, a window background, root background, and opaque card may cover each other while all being rendered.

Some overdraw is normal and is not automatically a performance problem. Investigate it when traces or GPU rendering tools point to fill cost, especially on complex screens or weaker devices. Remove redundant backgrounds and invisible layers, reduce unnecessary overlap, and use transparency, clipping, shadows, and offscreen rendering deliberately. Flattening a hierarchy is useful only when it reduces measured layout or drawing cost.

## Memory and tooling

### Memory leaks and memory pressure

A memory leak occurs when an object is no longer useful but remains strongly reachable from a GC root. Android-specific examples include a singleton retaining an `Activity`, a callback that is never removed, a long-lived coroutine capturing a `View`, or Fragment view binding retained after `onDestroyView()`.

A `Fragment` can outlive its view. Clear view binding and view-owned adapters or listeners in `onDestroyView()`, and collect UI data with `viewLifecycleOwner`. Long-lived objects should receive `applicationContext` when that is sufficient, and a `ViewModel` should not retain `Activity`, `Fragment`, or `View` instances. Weak references are not a general substitute for correct ownership.

High memory use is not always a leak. Large bitmaps, unbounded caches, excessive allocations, or loading an entire dataset can cause GC pressure or `OutOfMemoryError` even when objects eventually become collectible. Distinguish retained objects from temporary allocation churn before choosing a fix.

### Android Studio Profiler

Android Studio's profiling tools help test performance hypotheses. CPU recordings reveal hot paths, thread activity, lock contention, and main-thread work. Heap dumps and allocation recordings show object counts, allocation sites, and reference paths. Network inspection helps examine request timing and payloads.

Profile a concrete scenario such as cold startup, scrolling, opening a heavy screen, or loading and animating data. Debug builds and instrumented method tracing can add overhead, so use a release-like or profileable build when results need to represent user experience. Compare the same scenario before and after an optimization.

For a repeatable workflow, see [Performance Profiling and Benchmarking](../tools/performance-profiling.md). Leak investigation is covered in [Memory Leak Detection](../tools/memory-leaks.md).

### LeakCanary

LeakCanary detects objects that should have become collectible in debug builds. When a watched object remains retained, it analyzes a heap dump and reports a reference path from a GC root to that object.

Typical findings include a Fragment view-binding leak, an uncleared listener, an adapter retaining a destroyed view, an `Activity` context held by a singleton, or a coroutine capturing UI state. LeakCanary points to the retention chain; the developer must still identify the incorrect owner or lifecycle and fix it. Not every retained object is a permanent leak, so confirm the scenario and path.

### DEX and multidex

DEX (Dalvik Executable) is the bytecode format consumed by Android Runtime. Android build tools transform compiled Java and Kotlin bytecode into one or more DEX files.

A single DEX file can reference at most 65,536 methods. Apps with `minSdk` 21 or higher have native multidex support; older versions require the multidex support library and startup handling. Modern projects often cross this boundary without manual work, but dependency growth still affects build time, download size, startup, and maintainability.

Prefer narrow dependencies, remove unused libraries, and enable R8 shrinking for release builds. Treat multidex as packaging support, not as a replacement for dependency hygiene. Keep rules affect what R8 may remove, so verify optimized release builds with tests.

