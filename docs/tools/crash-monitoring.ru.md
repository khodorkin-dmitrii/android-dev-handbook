# Crash Reporting and Production Monitoring

Production monitoring должен превращать сбой в actionable и privacy-safe incident record. Это не то же самое, что local logging или product analytics.

## Разные зоны ответственности

* **Crash reporting** группирует fatal crashes, ANR и выбранные non-fatal errors со stack traces.
* **Logging** записывает diagnostic events локально или в контролируемые sinks.
* **Analytics** измеряет product behavior и funnels.
* **Performance monitoring** измеряет latency, startup, rendering или network spans.

Одна платформа может предоставлять несколько возможностей, но их data models, sampling, retention и access policies должны оставаться явными.

## Crashlytics, Sentry и альтернативы

Firebase Crashlytics - распространенный Android-вариант для crashes, non-fatals, ANR на поддерживаемых версиях Android, custom keys, logs и release grouping. Sentry и аналогичные платформы могут объединять errors с breadcrumbs, releases, environments, tracing и более широкой cross-platform observability.

Выбор зависит от нужных signals, alerting, загрузки symbols/mappings, release workflow, регионального хранения, consent, стоимости, self-hosting и существующей backend observability. Не выбирай платформу только потому, что в проекте уже используется другой продукт Firebase или monitoring vendor.

## Полезный контекст инцидента

Добавляй ограниченные low-cardinality metadata:

* release version, build number и commit SHA;
* environment и релевантные feature-flag values;
* device/OS и app process state;
* screen или flow name;
* нормализованную error category;
* mobile request ID и backend correlation ID;
* privacy-safe ссылку на user/session только при реальной необходимости.

Breadcrumbs должны описывать значимые transitions, а не каждый tap. Non-fatal reporting нужен для actionable неожиданных failures; отправка каждой обработанной ошибки уничтожает качество сигнала.

Нельзя отправлять tokens, passwords, payment data, raw request bodies или неограниченные personal data. Нужны consent и deletion requirements, redaction до вызова SDK и role-based доступ к console.

## На какие вопросы должен отвечать monitoring

* Что сломалось и где вероятная root area?
* Какие release и environment затронуты?
* Сколько users или sessions пострадало?
* Какой application state предшествовал сбою?
* Можно ли воспроизвести сценарий или связать его с backend evidence?
* Началась ли проблема или regression после определенного release?

## См. также

* [Performance & Memory](../android/performance-memory.md) - основы ANR
* [Logging and Diagnostic Data](logging-diagnostics.md)
* [QA-Friendly Debug Builds](qa-debug-builds.md)

