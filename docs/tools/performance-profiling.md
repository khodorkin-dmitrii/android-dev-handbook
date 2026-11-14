# Performance Profiling and Benchmarking

Profiling finds where time or memory goes. Benchmarking measures whether a defined workload changed. Start with a reproducible symptom, profile it to form a hypothesis, then benchmark a user-visible result.

## Profiling

Android Studio CPU and Memory Profilers help inspect call stacks, allocations, and heap contents. A System Trace or Perfetto recording shows scheduling, frame timing, CPU activity, and work across threads and processes. Layout Inspector helps inspect View or Compose hierarchy and recomposition behavior.

Choose a tool for the question:

* Slow startup: inspect main-thread initialization and a startup trace.
* Jank: find the missed frame deadline and check composition, layout, draw, or competing work.
* Memory growth: compare allocations and retained objects; use [Memory Leak Detection](memory-leaks.md) for ownership failures.
* Stalls: look for disk I/O, locks, binder calls, or work blocking the main thread.

Capture the shortest scenario that reproduces the issue. A long trace without a specific question is harder to interpret. Profiling itself adds overhead, so use traces to locate causes rather than as the sole measure of a speedup.

## Benchmarking

Use Macrobenchmark for app-level journeys such as startup, scrolling, and navigation. Use Microbenchmark for a small, repeatable code path; it cannot establish that an entire screen feels faster.

Benchmark a release-like, profileable app on stable devices. Keep the scenario, compilation mode, iterations, device state, and build variant consistent. Control warmup, background activity, and thermal effects. Compare a distribution of runs against a baseline, and inspect traces when a meaningful regression appears; one run is too noisy to decide.

## Baseline Profiles

Baseline Profiles identify critical code paths for ahead-of-time compilation by ART. They can improve startup and important interactions, including early runs after install, but they do not identify a bottleneck or replace a benchmark.

Generate a profile from representative user journeys, package it with the app, and compare benchmarks with and without it under the same compilation and device conditions. Keep the generated profile current as those journeys change.

## See also

* [Performance & Memory](../android/performance-memory.md)
* [Compose Performance](../compose/performance.md)
* [Android UI Testing](../testing/android-ui-testing.md)
* [Memory Leak Detection](memory-leaks.md)
