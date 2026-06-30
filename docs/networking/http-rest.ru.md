# HTTP / REST

HTTP и REST - основа большинства Android network APIs: request/response, status codes, headers, JSON body и правила обработки ошибок.

## HTTP

HTTP (Hypertext Transfer Protocol) - application-layer protocol для обмена данными между client и server по модели request/response.

В Android HTTP используется почти во всех network APIs: приложение отправляет request с method, URL, headers и optional body, а server возвращает response со status code, headers и optional body, чаще всего JSON.

HTTP сам по себе stateless: между двумя requests нет встроенной связи. Session и authentication обычно строятся поверх HTTP через cookies, tokens или headers.

**Коротко:** HTTP - это stateless application-layer request/response protocol; Android apps обычно используют его через OkHttp/Retrofit для общения с backend APIs.

### What is REST?

REST (Representational State Transfer) - architectural style для client-server APIs, где данные представлены как resources, обычно доступные через URLs.

Операции над resources выражаются через HTTP methods. Response обычно содержит representation ресурса, например JSON.

Ключевые идеи REST:

- client-server separation;
- stateless requests;
- cacheability;
- uniform interface;
- clear resource URLs;
- meaningful HTTP methods and status codes.

**Важно:** не каждый JSON-over-HTTP API является строгим REST. В Android practice обычно важнее понимать practical REST-like APIs и корректно работать с methods, headers, status codes и error responses.

**Коротко:** REST - resource-oriented API style поверх HTTP: у resources есть URLs, operations используют HTTP methods, requests stateless, а responses используют status codes и representations вроде JSON.

### HTTP methods

HTTP methods описывают, что client хочет сделать с resource.

| Method | Typical purpose | Safe | Idempotent |
|--------|-----------------|------|------------|
| `GET` | Read a resource | Yes | Yes |
| `POST` | Create a resource or start an action | No | Usually no |
| `PUT` | Replace a resource | No | Yes |
| `PATCH` | Partially update a resource | No | Usually no |
| `DELETE` | Delete a resource | No | Yes |

`GET` используется для чтения resource. Он должен быть safe и idempotent: повторный `GET` не должен менять server state. Parameters часто передаются в query string, а response может кэшироваться.

`POST` используется для отправки данных: создать resource, отправить form, запустить command или trigger an action. `POST` обычно имеет request body и не гарантирует idempotency: retry может создать duplicate или выполнить action дважды.

`PUT` обычно заменяет resource полной новой representation. Обычно он idempotent: отправка одного и того же `PUT` request несколько раз должна приводить к одному и тому же final state.

`PATCH` частично обновляет resource. Он полезен, когда client отправляет только изменённые поля, но его idempotency зависит от API design.

`DELETE` удаляет resource. Обычно он idempotent: повторное удаление того же resource не должно создавать другой результат, хотя server может вернуть `404` после первого удаления.

В Android не стоит передавать sensitive или большие данные через query parameters, а non-idempotent requests нужно retry-ить осторожно. Для critical operations backend должен поддерживать idempotency key или безопасную проверку operation status.

**Коротко:** HTTP methods - часть API contract. `GET` читает, `POST` создаёт или запускает actions, `PUT` заменяет, `PATCH` частично обновляет, `DELETE` удаляет.

### GET vs POST

`GET` предназначен для safe resource reads. Он не должен менять server state и обычно cacheable.

`POST` предназначен для отправки данных на server. Его часто используют для creation, form submission, commands, payments, login и других actions.

Практическая разница важна для retries. Retry `GET` обычно безопасен. Retry `POST` может быть опасным, если server не поддерживает idempotency, потому что та же operation может выполниться больше одного раза.

Например, retry failed profile fetch обычно нормален. Retry payment confirmation без idempotency key может создать некорректный user experience или duplicate operation.

**Коротко:** `GET` - для safe reads, `POST` - для отправки данных или запуска actions; retry `GET` обычно безопаснее, чем retry `POST`.

### HTTP status codes

HTTP status code сообщает client, как server обработал request. Это часть HTTP protocol, и его стоит воспринимать как часть API contract, а не просто indicator ошибки.

Status codes группируются в пять категорий:

- `1xx` - Informational
- `2xx` - Success
- `3xx` - Redirection
- `4xx` - Client error
- `5xx` - Server error

Самые частые codes:

| Code | Meaning | Typical use |
|------|---------|-------------|
| `200 OK` | Request succeeded | Successful `GET`, `PUT` or `PATCH` |
| `201 Created` | Resource created | Successful `POST` that creates a new resource |
| `204 No Content` | Success without response body | `DELETE` or update without returned data |
| `301 Moved Permanently` | Resource moved permanently | Client should use the new URL |
| `302 Found` | Temporary redirect | Temporary resource location |
| `304 Not Modified` | Cached resource is still valid | Client should use cached response |
| `400 Bad Request` | Invalid request | Malformed JSON, missing or invalid parameters |
| `401 Unauthorized` | Authentication required or invalid | Missing or expired access token |
| `403 Forbidden` | Authenticated but not allowed | Missing permissions |
| `404 Not Found` | Resource does not exist | Wrong endpoint or missing resource |
| `409 Conflict` | Resource state conflict | Version mismatch, duplicate operation |
| `422 Unprocessable Entity` | Validation failed | Business validation error |
| `429 Too Many Requests` | Rate limit exceeded | Retry later, often with `Retry-After` |
| `500 Internal Server Error` | Unexpected server failure | Backend bug |
| `502 Bad Gateway` | Upstream service failed | Gateway/proxy error |
| `503 Service Unavailable` | Server unavailable | Maintenance or overload |
| `504 Gateway Timeout` | Upstream timeout | Backend responded too slowly |

Некоторые status codes особенно важны в mobile apps:

- `401` обычно означает, что нужна authentication или access token истёк.
- `403` означает, что authentication прошла, но у client нет permission для operation.
- `404` может означать wrong endpoint, wrong ID, deleted resource или API version mismatch.
- `409` указывает на conflict с текущим resource state, например optimistic locking или duplicate operations.
- `422` означает, что request format корректен, но business validation failed.
- `429` означает rate limiting. Clients должны учитывать header `Retry-After`, если он есть.
- `5xx` errors обычно означают, что server или upstream dependency failed, но app всё равно должен показать полезное temporary error state.

В Android не стоит маппить все non-2xx responses в один generic error. `401` может вести к token refresh или logout, `403` - к access denied, `404` - к empty/not found state, а `429` / `5xx` - к retry, backoff или temporary error.

**Коротко:** HTTP status codes описывают outcome request и являются частью API contract. Clients должны различать authentication, authorization, validation, conflicts, rate limiting и server failures, а не воспринимать каждый non-2xx response как generic error.

### Headers and body

HTTP headers передают metadata о request или response.

Common request headers:

- `Authorization` - access token или credentials;
- `Content-Type` - format request body;
- `Accept` - expected response format;
- `User-Agent` - client information;
- custom headers для app version, locale, device или feature flags.

Request body содержит данные, отправляемые на server. В Android APIs это часто JSON, но также может быть multipart form data, protobuf или другой format.

Response body содержит возвращённые данные или error details. Successful response обычно маппится в DTO, а error response может содержать backend-specific error code, message и validation details.

**Коротко:** headers описывают metadata и authentication; body переносит request или response payload.

### Error mapping in Android

Network error handling лучше разделять на уровни: transport errors, HTTP protocol errors, serialization errors и business errors.

Transport errors означают no network, timeout, DNS/TLS problem или cancelled request. В Kotlin/OkHttp-based code они часто выглядят как `IOException` или timeout-related failures.

HTTP errors означают, что server ответил, но status code non-2xx.

Serialization errors означают, что response не удалось распарсить, потому что payload не совпадает с expected model или converter configuration.

Business errors означают, что backend вернул valid response с domain-specific problem, например validation failure, insufficient funds, unavailable feature или invalid operation state.

Хорошее место для mapping - data/repository layer: Retrofit/OkHttp exceptions и backend error body превращаются в domain/UI error model. UI не должен напрямую разбирать HTTP codes, JSON error body или `IOException`.

Retry подходит для transient problems: timeout, connection issue, `5xx`, иногда `429` с backoff. Не стоит retry-ить validation errors, invalid credentials, forbidden access или non-idempotent operations без idempotency.

**Коротко:** в Android low-level network, protocol, serialization и business errors стоит маппить в app-level errors в repository/domain layer, а UI должен только рендерить понятное user-facing state.
