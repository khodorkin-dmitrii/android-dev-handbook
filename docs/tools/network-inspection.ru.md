# Network Inspection

Network diagnostics должны отвечать, что произошло, сколько это заняло и как mobile request связан с backend evidence. Вывод raw bodies недостаточен и не всегда безопасен.

## Выбор способа диагностики

| Подход | Когда полезен | Главный компромисс |
|---|---|---|
| OkHttp Logging Interceptor | Быстрые developer logs, headers и timing | Шум в Logcat и риск раскрытия payload |
| Chucker | История запросов на устройстве для developers и QA | Дополнительный code/runtime surface в приложении |
| Android Studio Network Inspector | Live local inspection без custom UI | Нужны IDE attachment и поддерживаемый client |
| Charles, Proxyman или другой proxy | Cross-app traffic, rewriting и throttling | Настройка certificates и ограничения pinning |
| Request/backend correlation | Диагностика distributed incidents | Требует совместной поддержки mobile и backend |

Android Studio Network Inspector поддерживает OkHttp и `HttpsURLConnection`; traffic других stacks может не декодироваться. Proxy видит направленный через него traffic, но TLS certificate pinning может намеренно запрещать interception.

## Chucker во внутренних builds

Chucker записывает OkHttp requests/responses и предоставляет on-device UI, notifications, search и sharing. Это полезно, когда QA не может подключить IDE. Debug artifact должен использоваться только в контролируемых variants; no-op release artifact может сохранить общий API, если это необходимо.

Настрой retention, максимальный body size и redaction. Exported traffic может содержать credentials, personal data или business-sensitive payloads, поэтому sharing должен быть осознанным и контролируемым.

## Диагностические metadata

Полезные поля:

* request ID и backend correlation ID;
* method и endpoint template вместо чувствительного полного URL;
* status code и нормализованная error category;
* duration, retry count и connectivity state;
* app version, environment и выбранный API host.

Application interceptor может добавлять request ID и записывать ограниченный summary. Authentication headers и bodies не должны попадать в общие logs.

## Ограничения

Возможности inspection зависят от protocol и client architecture. Для WebSockets, streaming, encrypted custom protocols, gRPC/protobuf payloads и traffic вне проверяемого OkHttp client нужны специализированные инструменты. Human-readable body viewer не объясняет HTTP/2 framing, retry policy, DNS/TLS latency или backend processing time.

По умолчанию используй `BASIC` или metadata-oriented logging. Полные bodies стоит включать только для конкретного контролируемого расследования с redaction перед отображением или экспортом.

## См. также

* [Retrofit / OkHttp](../networking/retrofit-okhttp.md)
* [HTTP / REST](../networking/http-rest.md)
* [gRPC / Protobuf](../networking/grpc-protobuf.md)
* [Logging and Diagnostic Data](logging-diagnostics.md)

