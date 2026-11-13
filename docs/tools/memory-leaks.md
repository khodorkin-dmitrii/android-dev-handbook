# Memory Leak Detection

On Android, a memory leak occurs when an object remains reachable from a GC root after its intended lifetime. The key question is which reference keeps it alive and who should release that reference.

## LeakCanary and Memory Profiler

LeakCanary watches objects such as destroyed `Activity` and `Fragment` instances, analyzes a heap dump when they remain retained, and shows a reference path to them. It also helps in Compose apps: a composable can still capture an `Activity`, `View`, or callback in a longer-lived object. LeakCanary does not measure recomposition or layout cost.

Android Studio Memory Profiler can record allocations and inspect heap dumps and class instances. Use it to investigate steady memory growth or excessive allocation when no single lifecycle object explains the problem.

A heap dump is a snapshot. A retained object is evidence to investigate, not proof of a leak: an active operation, a bounded cache, or a debugger may keep it alive temporarily. Check the expected lifetime and the strong-reference path before changing code.

## Typical sources

* A singleton or long-lived `ViewModel` holding an `Activity`, `View`, or callback that captures them.
* A listener, observer, or SDK registration not removed when its owner ends.
* A coroutine job or callback that keeps a screen alive after its lifecycle ends.
* A Fragment view binding kept past `onDestroyView()`.
* An unbounded cache or queue retaining screens or large data.

For Fragment view binding, clear the stored reference in `onDestroyView()`; the Fragment instance can outlive its view. In Compose, avoid passing an `Activity` context into a longer-lived holder. Ordinary composition state is released when its composition is disposed, unless another reference retains it.

## Investigation workflow

1. Repeat a specific scenario, such as opening and closing a screen or rotating the device.
2. Identify the object expected to be released and confirm that it remains retained after cleanup.
3. Follow the reference path from a GC root to that object.
4. Find the owner whose lifetime is too long; fix the scope, reference, or missing unregister/cleanup.
5. Repeat the scenario and compare retained objects and memory behavior.

Do not use `WeakReference` as a routine fix: it can mask incorrect ownership and make values disappear unexpectedly. Correct the lifecycle boundary instead.

## See also

* [Performance & Memory](../android/performance-memory.md)
* [Activity, Fragment & Lifecycle](../android/activity-fragment-lifecycle.md)
* [Coroutine Scopes & Cancellation](../coroutines-flow/scopes-cancellation.md)
* [Performance Profiling and Benchmarking](performance-profiling.md)
