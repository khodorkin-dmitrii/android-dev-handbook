# Performance Profiling and Benchmarking

Profiling and benchmarking answer different questions:

* **profiling:** where is the application spending time or memory;
* **benchmarking:** did a defined scenario become measurably faster or slower?

Use a profile to form and verify a hypothesis. Use a benchmark to detect change under controlled conditions.

## Profiling

Android Studio CPU and Memory Profilers support method/call-stack analysis, allocations, and heap inspection. System Trace and Perfetto show scheduling, CPU state, frames, binder/system activity, and interactions across processes. Layout Inspector helps inspect View or Compose hierarchy; Compose tooling can expose recomposition and layout behavior.

Useful investigations include:

* cold/warm startup and initialization on the main thread;
* jank, missed frame deadlines, composition/layout/draw cost;
* allocations, GC pressure, and retained memory;
* database and disk I/O;
* network latency separated from UI processing;
* locks, binder calls, and background work competing for resources.

Record the smallest reproducible scenario. Profiling a long uncontrolled session creates a large trace without a clear question.

## Benchmarking

Macrobenchmark measures app-level journeys such as startup, scrolling, navigation, and animation. Run it against a profileable, release-like target on stable physical devices or controlled CI. Define setup, compilation mode, iterations, device state, and success thresholds.

Do not compare one noisy run. Track distributions and traces, and investigate changes large enough to matter to users.

## Baseline Profiles

Baseline Profiles describe important code paths so ART can precompile them for installed builds. They can improve startup and critical interactions from first launch, but they do not locate a bottleneck and do not prove a regression was fixed.

Generate profiles from representative critical user journeys, then benchmark the result. Keep profiling, benchmarks, and profiles as complementary tools.

## See also

* [Performance & Memory](../android/performance-memory.md) - ANR, jank, leaks, and Profiler basics
* [Compose Performance](../compose/performance.md)
* [Android UI Testing](../testing/android-ui-testing.md)
* [Memory Leak Detection](memory-leaks.md)

