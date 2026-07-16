# Обзор инструментов

Android tooling полезен, когда выбор начинается с инженерного вопроса: каких данных не хватает, кому они нужны и где их можно безопасно получить? Название библиотеки само по себе не является стратегией.

Стабильные категории включают разработку приложения, local debugging, automated testing, network и memory diagnostics, UI/performance analysis, production monitoring и поддержку QA investigations. Один инструмент может относиться к нескольким категориям, но его operational boundary должна оставаться понятной.

## Инструменты по задачам

| Задача | Инструмент или подход | Где работает | Статус | Главное ограничение |
|---|---|---|---|---|
| Удерживаемые объекты | LeakCanary | Debug-приложение/устройство | Рекомендуемый вариант диагностики | Ищет удержание, а не стоимость recomposition |
| Heap и allocations | Android Studio Memory Profiler | IDE и устройство | Стандартный platform tool | Требует ручного анализа сценария |
| Просмотр HTTP на устройстве | Chucker | Debug/internal build | Полезен разработчикам и QA | Может раскрыть чувствительные payloads |
| HTTP-логи | OkHttp Logging Interceptor | Приложение/Logcat | Полезен при узкой настройке | Body logging опасен и создает шум |
| Live traffic поддерживаемых clients | Network Inspector | Android Studio | Стандартный локальный инструмент | В основном поддерживает OkHttp и `HttpsURLConnection` |
| Легкий logging facade | Timber | Приложение | Зрелый необязательный выбор | Сам по себе не дает structured logging |
| Структурированная диагностика | Собственная абстракция logger | Приложение и настроенные sinks | Рекомендуется сложным продуктам | Требует проектирования и поддержки |
| Системный timing | Perfetto / System Trace | Устройство и desktop | Стандартный deep profiling tool | Нужно уметь читать traces |
| CPU, memory и jank | Android Studio Profiler | IDE и устройство | Стандартный локальный инструмент | Overhead и неконтролируемые сценарии |
| Повторяемые user journeys | Macrobenchmark | Benchmark device/CI | Рекомендуемый measurement tool | Нужны контролируемые условия |
| Подсказки для AOT-оптимизации | Baseline Profiles | Build и установленное приложение | Рекомендуются для critical journeys | Оптимизируют, но не диагностируют и не измеряют |
| Crash и ANR reports | Firebase Crashlytics | Production monitoring | Распространенный production-вариант | Vendor, consent и privacy decisions |
| Более широкая observability ошибок | Sentry или аналог | Production monitoring | Полноценная альтернатива | Стоимость, data governance и объем интеграции |
| Внутренняя диагностика | Beagle или custom debug menu | Debug/internal build | Оценивать под проект | UI и архитектура библиотеки могут не подойти |
| Исторический debug drawer | Hyperion | Debug build | Legacy/reference | View-era design без Compose-aware inspection |

Дополнительные категории включают automated tests, Layout Inspector, Database Inspector, Background Task Inspector, Android vitals в Play Console и backend tracing. Ни один инструмент не одинаково хорошо решает local debugging, воспроизводимые измерения и production monitoring.

## Критерии выбора

Оценивай инструмент по следующим параметрам:

* задача и необходимые диагностические данные;
* runtime cost в debug и production;
* чувствительность данных, redaction, retention и access control;
* совместимость с реальной network/UI/build архитектурой;
* полезность для QA без Android Studio;
* состояние поддержки и стоимость обновлений;
* формат экспорта и корреляция с backend или release data;
* масштаб продукта и процесс работы с инцидентами.

Небольшому приложению могут быть достаточны Logcat, Profiler и crash reporting. Крупному продукту часто также нужны внутренний diagnostic UI, structured logs, request correlation, повторяемые benchmarks и контролируемый экспорт.

**Главная мысль:** выбирай минимальный набор, который делает важные сбои наблюдаемыми и воспроизводимыми. Не добавляй debug inspection или сбор чувствительных данных только потому, что библиотека это умеет.

## Структура раздела

* [In-App Debug Menus](in-app-debug-menus.md)
* [Logging and Diagnostic Data](logging-diagnostics.md)
* [Network Inspection](network-inspection.md)
* [Memory Leak Detection](memory-leaks.md)
* [Performance Profiling and Benchmarking](performance-profiling.md)
* [Crash Reporting and Production Monitoring](crash-monitoring.md)
* [QA-Friendly Debug Builds](qa-debug-builds.md)

## См. также

* [Testing Strategy](../testing/strategy.md)
* [Performance & Memory](../android/performance-memory.md)
* [Background Work & System Behavior](../android/background-work-system-behavior.md)
