# Performance Profiling and Benchmarking

Profiling и benchmarking отвечают на разные вопросы:

* **profiling:** где приложение тратит время или memory;
* **benchmarking:** стал ли определенный сценарий измеримо быстрее или медленнее?

Profile помогает сформулировать и проверить гипотезу. Benchmark обнаруживает изменение в контролируемых условиях.

## Profiling

Android Studio CPU и Memory Profilers поддерживают method/call-stack analysis, allocations и heap inspection. System Trace и Perfetto показывают scheduling, CPU state, frames, binder/system activity и взаимодействие процессов. Layout Inspector помогает исследовать View или Compose hierarchy; Compose tooling показывает recomposition и layout behavior.

Полезные направления исследования:

* cold/warm startup и initialization на main thread;
* jank, пропущенные frame deadlines, стоимость composition/layout/draw;
* allocations, GC pressure и retained memory;
* database и disk I/O;
* network latency отдельно от UI processing;
* locks, binder calls и background work, конкурирующие за ресурсы.

Записывай минимальный воспроизводимый сценарий. Profiling длинной неконтролируемой сессии создает большой trace без ясного вопроса.

## Benchmarking

Macrobenchmark измеряет app-level journeys: startup, scrolling, navigation и animation. Запускай его для profileable release-like target на стабильных физических устройствах или контролируемом CI. Фиксируй setup, compilation mode, iterations, device state и success thresholds.

Не сравнивай один noisy run. Следи за distributions и traces, исследуй изменения, достаточно большие для влияния на пользователя.

## Baseline Profiles

Baseline Profiles описывают важные code paths, чтобы ART мог заранее скомпилировать их для установленного build. Они улучшают startup и critical interactions с первого запуска, но не находят bottleneck и не доказывают исправление regression.

Генерируй profiles из репрезентативных critical user journeys, затем измеряй результат benchmark. Profiling, benchmarks и profiles дополняют друг друга.

## См. также

* [Performance & Memory](../android/performance-memory.md) - ANR, jank, leaks и основы Profiler
* [Compose Performance](../compose/performance.md)
* [Android UI Testing](../testing/android-ui-testing.md)
* [Memory Leak Detection](memory-leaks.md)

