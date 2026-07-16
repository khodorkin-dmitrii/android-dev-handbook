# QA-Friendly Debug Builds

Мобильное приложение не должно быть black box для QA. Полезный internal build показывает достаточно состояния, чтобы воспроизвести и классифицировать дефект без доступа к source code или Android Studio.

## Что должен показывать internal build

Ценные диагностические данные:

* active environment, API host, app version, build number и commit SHA;
* состояние account/session без credentials;
* feature flags и experiment assignments;
* summaries local database и cache;
* recent request history, application logs и последние нормализованные errors;
* статус регистрации push token без его бесконтрольного отображения;
* background-work и sync status;
* permissions и релевантные device metadata;
* diagnostic ID, связывающий mobile, backend и test evidence.

Предпочитай summaries и безопасные actions вместо неограниченного просмотра database/files. Цель - investigation, а не обход границ приложения.

## Diagnostic bundle

```text
diagnostic-report/
├── app-metadata.json
├── device-metadata.json
├── feature-flags.json
├── recent-logs.txt
├── network-summary.json
├── local-state-summary.json
└── screenshot-or-screen-recording
```

По возможности формируй bundle из immutable snapshots. Добавляй timestamps, schema version, app version и report ID. Ограничивай количество logs и размер файлов. Применяй redaction до записи, затем проверяй финальный archive по allowlist.

По умолчанию нельзя включать passwords, auth tokens, payment data, неограниченные production records или полные payloads. Export требует явного действия пользователя, короткого retention, безопасного sharing и понятного ownership после выхода данных с устройства.

## Полезные debug actions

* reset onboarding или clear local cache;
* безопасно expire текущую session;
* включить force offline mode;
* симулировать server error, empty state или degraded response;
* запустить sync или разрешенный background work;
* скопировать diagnostic ID;
* открыть конкретный internal screen;
* обновить feature flags;
* воспроизвести predefined application state.

По возможности actions должны использовать те же application services, что и реальные flows. Прямое редактирование storage может создать невозможные states и misleading defect reports. Simulated state нужно обозначать в UI, а reset behavior делать предсказуемым.

## Архитектура и безопасность

Diagnostic contracts стоит держать в application-owned interfaces, а implementations - в debug/internal source sets:

```text
QA / Debug UI
      ↓
Diagnostic queries and controlled commands
      ↓
Repositories, work manager, feature flags, logger, network summaries
```

Мощным internal builds все равно нужны access control, environment restrictions, signed distribution, remote revocation при необходимости и audit опасных операций. Production-like data требуют production-like обращения, даже если APK не публичный.

Диагностические возможности стоит проверять вместе с QA, mobile, backend, security и privacy stakeholders. Хороший internal build показывает данные, которые сокращают реальное investigation, а не все значения, которые приложение технически может прочитать.

## См. также

* [In-App Debug Menus](in-app-debug-menus.md)
* [Network Inspection](network-inspection.md)
* [Logging and Diagnostic Data](logging-diagnostics.md)
* [Background Work & System Behavior](../android/background-work-system-behavior.md)
* [Testing Strategy](../testing/strategy.md)

