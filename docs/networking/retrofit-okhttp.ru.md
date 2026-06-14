# Retrofit / OkHttp

Retrofit обычно описывает type-safe API layer, а OkHttp выполняет реальную HTTP-работу: connections, requests, responses, interceptors, cache и timeouts.

## Clients

### Retrofit

Retrofit - type-safe HTTP client layer для Android/JVM, который описывает backend API через Kotlin/Java interface и annotations.

Он превращает методы вроде `@GET`, `@POST`, `@Path`, `@Query`, `@Body` в HTTP calls и обычно работает поверх OkHttp. В modern Kotlin-коде Retrofit часто возвращает suspend functions или `Flow` / `Result` через repository layer.

**Важно:** Retrofit service не должен торчать прямо в UI / `ViewModel`. Лучше держать его в data layer и маппить DTO/errors в domain или UI models.

**Коротко:** Retrofit describes REST API as interfaces and delegates actual HTTP work to OkHttp.

### OkHttp

OkHttp - низкоуровневый HTTP client, который выполняет network requests, управляет connections, timeouts, redirects, cache и connection pooling.

Retrofit обычно использует OkHttp под капотом, но OkHttp можно использовать и напрямую, если нужен ручной control над request/response.

В Android важно настраивать timeouts, cache, TLS/certificates при необходимости и не выполнять synchronous calls на main thread.

**Коротко:** OkHttp is the actual HTTP client; Retrofit is a convenient typed API layer on top of it.

### Interceptors

Interceptor в OkHttp - middleware вокруг request/response. Он может добавить headers, auth token, logging, metrics, retry или обработать common network behavior.

Application interceptors видят logical request, network interceptors ближе к реальному network exchange и могут видеть redirects/cache/network details.

Частые кейсы: Authorization header, refresh token flow, logging в debug builds, common headers, user-agent, error normalization.

**Важно:** не логируй sensitive данные и не делай тяжёлую/blocking логику внутри interceptor без необходимости.

**Коротко:** interceptors centralize cross-cutting network logic like auth, logging and common headers.

## Payload и errors

### Serialization

Serialization - преобразование JSON/protobuf/raw response в Kotlin/Java models и обратно.

С Retrofit это обычно делается через converter: Gson, Moshi, kotlinx.serialization или protobuf converter. Converter превращает response body в DTO, а request body - в нужный wire format.

Pitfalls: nullable поля, unknown fields, date/time formats, enum evolution, default values и несовпадение API contract с DTO.

**Коротко:** serialization maps network payloads to DTOs; app code should validate and map DTOs before exposing domain/UI models.

### Network error handling

Network error handling лучше держать в repository/data layer: `IOException` / timeout, HTTP non-2xx, parsing error и backend business error превращаются в понятную app error model.

Retrofit может вернуть `Response<T>` для ручной проверки `code` / `body` или бросить exception в зависимости от call adapter и сигнатуры API. Для suspend calls важно отдельно учитывать cancellation.

UI не должен знать детали OkHttp exception, `Retrofit Response.errorBody()` или JSON error schema. Он должен получать clear state: loading/content/error/retry.

**Коротко:** map Retrofit/OkHttp errors into domain/UI errors at the data boundary, not inside UI code.
