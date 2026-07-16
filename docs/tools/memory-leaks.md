# Memory Leak Detection

A memory leak is an ownership failure: an object that should be unreachable remains connected to a GC root. Detection tools provide evidence, but the fix usually belongs in lifecycle or reference ownership.

## LeakCanary and Memory Profiler

LeakCanary watches Android/JVM objects expected to become collectible, triggers heap analysis, and shows a reference chain to the retained object. It remains useful in Compose applications because Compose still runs on Android and the JVM. It is not a recomposition or layout profiler.

Android Studio Memory Profiler complements it with allocation recording, heap dumps, class-instance inspection, and manual comparison of memory behavior. Use it when growth is not tied to a lifecycle object or when allocation pressure matters more than one retained instance.

Heap dumps are snapshots. A retained object is not automatically a harmful leak: caches, framework behavior, debugger references, and work still in progress need context. The reference chain and expected lifecycle are decisive.

## Typical sources

* an `Activity` or `Fragment` retained by a singleton;
* listeners, callbacks, observers, or SDK registrations not removed;
* coroutine scopes that outlive their owner;
* Fragment View binding retained after `onDestroyView()`;
* long-lived references to `Activity` `Context`;
* custom Views, adapters, or drawables holding a screen;
* unbounded caches and queues.

## Investigation workflow

1. Reproduce the same open/close or rotation scenario.
2. Confirm that the object stays retained after expected cleanup.
3. Inspect the shortest useful path from a GC root.
4. Identify which component should own the reference.
5. Fix ownership, scope, unregistering, or cleanup.
6. Repeat the scenario and check memory behavior again.

Avoid treating `WeakReference` as the default fix. It can hide unclear ownership while introducing disappearing data. Prefer correcting the lifecycle boundary.

## See also

* [Performance & Memory](../android/performance-memory.md)
* [Activity, Fragment & Lifecycle](../android/activity-fragment-lifecycle.md)
* [Coroutine Scopes & Cancellation](../coroutines-flow/scopes-cancellation.md)
* [Performance Profiling and Benchmarking](performance-profiling.md)

