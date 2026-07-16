# Memory Leak Detection

Memory leak - это ошибка ownership: объект, который должен стать недостижимым, остается связан с GC root. Инструменты дают evidence, но исправление обычно находится в lifecycle или владении references.

## LeakCanary и Memory Profiler

LeakCanary наблюдает за Android/JVM objects, которые должны стать доступными для GC, запускает heap analysis и показывает reference chain до retained object. Он остается полезен в Compose-приложениях, потому что Compose все равно работает поверх Android и JVM. Это не profiler recomposition или layout.

Android Studio Memory Profiler дополняет его recording allocations, heap dumps, просмотром class instances и ручным сравнением memory behavior. Он полезен, когда рост не связан с конкретным lifecycle object или allocation pressure важнее одной retained instance.

Heap dump является snapshot. Retained object не всегда означает опасную утечку: caches, framework behavior, debugger references и незавершенная работа требуют контекста. Решающее значение имеют reference chain и ожидаемый lifecycle.

## Типичные источники

* `Activity` или `Fragment`, удерживаемые singleton;
* не удаленные listeners, callbacks, observers или SDK registrations;
* coroutine scopes, живущие дольше владельца;
* Fragment View binding после `onDestroyView()`;
* долгоживущие ссылки на `Activity` `Context`;
* custom Views, adapters или drawables, удерживающие экран;
* неограниченные caches и queues.

## Процесс исследования

1. Повторить одинаковый сценарий открытия/закрытия или rotation.
2. Убедиться, что объект остается retained после ожидаемого cleanup.
3. Изучить кратчайший полезный путь от GC root.
4. Определить компонент, который должен владеть reference.
5. Исправить ownership, scope, unregistering или cleanup.
6. Повторить сценарий и снова проверить memory behavior.

Не используй `WeakReference` как исправление по умолчанию. Он может скрыть неясный ownership и добавить исчезающие данные. Лучше исправить lifecycle boundary.

## См. также

* [Performance & Memory](../android/performance-memory.md)
* [Activity, Fragment & Lifecycle](../android/activity-fragment-lifecycle.md)
* [Coroutine Scopes & Cancellation](../coroutines-flow/scopes-cancellation.md)
* [Performance Profiling and Benchmarking](performance-profiling.md)

