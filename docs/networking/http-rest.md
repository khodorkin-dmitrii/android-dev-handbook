# HTTP / REST

HTTP и REST - базовый foundation большинства Android network APIs: request/response, status codes, headers, JSON body и правила обработки ошибок.

## HTTP

### Что такое HTTP?

HTTP (Hypertext Transfer Protocol) - application-layer протокол для обмена данными между client и server по модели request/response.

В Android HTTP используется почти во всех network API: приложение отправляет request с method, URL, headers и optional body, а server возвращает response со status code, headers и optional body, чаще всего JSON.

HTTP сам по себе stateless: между двумя запросами нет встроенной связи. Session/auth обычно строятся поверх HTTP через cookies, tokens или headers.

**Коротко:** HTTP is a stateless application-layer request/response protocol; Android apps usually use it through OkHttp/Retrofit to communicate with backend APIs.

### Что такое REST?

REST (Representational State Transfer) - architectural style для client-server API, где данные представлены как resources, обычно доступные по URLs.

Операции над resources выражаются через HTTP methods: `GET` читает, `POST` создаёт или запускает action, `PUT` / `PATCH` обновляют, `DELETE` удаляет. Response обычно содержит representation ресурса, например JSON.

Ключевые идеи REST: client-server separation, stateless requests, cacheability, uniform interface и понятная работа со status codes.

**Важно:** не каждый JSON-over-HTTP API является строгим REST, но в Android-практике важно понимать practical REST API и корректно работать с methods/status codes.

**Коротко:** REST is a resource-oriented API style over HTTP: resources have URLs, operations use HTTP methods, requests are stateless, and responses use status codes and representations like JSON.

### GET vs POST

`GET` используется для чтения resource. Он должен быть safe и idempotent: повторный `GET` не должен менять состояние server. Параметры часто передаются в query string, а response может кэшироваться.

`POST` используется для отправки данных: создание resource, submit формы, запуск command/action. `POST` обычно имеет request body и не гарантирует idempotency: повтор может создать дубликат или выполнить действие дважды.

В Android важно не класть sensitive или большие данные в query parameters и осторожно ретраить `POST`. Для критичных операций backend должен поддерживать idempotency key или безопасную проверку статуса операции.

**Коротко:** `GET` is for safe resource reads, `POST` is for sending data or creating actions; retrying `GET` is usually safer than retrying `POST`.

### HTTP status codes

HTTP status code показывает результат обработки request. Для клиента это первый сигнал, как интерпретировать response.

Основные группы: `1xx` - informational, `2xx` - success, `3xx` - redirection, `4xx` - client error, `5xx` - server error.

Частые коды: `200 OK`, `201 Created`, `204 No Content`, `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `409 Conflict`, `422 Validation Error`, `429 Too Many Requests`, `500 Internal Server Error`, `503 Service Unavailable`.

В Android не стоит маппить все non-2xx в один общий error. `401` может вести к logout/refresh token, `403` - к access denied, `404` - к empty/not found state, `429` / `5xx` - к retry/backoff или temporary error.

**Коротко:** status codes are part of the API contract; client code should distinguish success, auth, validation, not found, rate limit and server errors.

### Error mapping in Android

Network error handling лучше разделять на уровни: transport errors, HTTP protocol errors, serialization errors и business errors.

Transport errors - нет сети, timeout, DNS/TLS problem, cancelled request. HTTP errors - server ответил, но status code non-2xx. Serialization errors - response не удалось распарсить. Business errors - backend вернул валидный response с domain-specific проблемой.

Хорошее место для mapping - data/repository layer: Retrofit/OkHttp exceptions и backend error body превращаются в domain/UI error model. UI не должен напрямую разбирать HTTP codes, JSON error body или `IOException`.

Retry подходит для transient problems: timeout, connection issue, `5xx`, иногда `429` с backoff. Не стоит ретраить validation errors, invalid credentials, forbidden access или non-idempotent operations без idempotency.

**Коротко:** in Android, map low-level network/protocol/serialization errors into app-level errors in repository/domain layer, then let UI render a clear user-facing state.
