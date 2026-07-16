# Retrofit / OkHttp

Retrofit обычно описывает type-safe API layer, а OkHttp выполняет реальную HTTP-работу: connections, requests, responses, interceptors, cache и timeouts.

## Clients

### Retrofit

Retrofit - type-safe HTTP client layer для Android/JVM, который описывает backend API через Kotlin/Java interfaces и annotations.

Он превращает methods вроде `@GET`, `@POST`, `@PUT`, `@PATCH`, `@DELETE`, `@Path`, `@Query`, `@Body` и `@Header` в HTTP calls и обычно работает поверх OkHttp.

В modern Kotlin code Retrofit часто отдаёт `suspend` functions из data layer:

```kotlin
interface UserApi {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") id: String): UserDto

    @POST("users")
    suspend fun createUser(@Body body: CreateUserRequest): UserDto
}
```

Retrofit также может возвращать `Response<T>`, когда caller-у нужен ручной доступ к HTTP status code, headers или error body.

```kotlin
@GET("users/{id}")
suspend fun getUserResponse(@Path("id") id: String): Response<UserDto>
```

**Важно:** Retrofit service не должен быть напрямую доступен UI или `ViewModel`. Держи его в data layer и маппь DTOs/errors в domain или UI models.

**Коротко:** Retrofit описывает REST API как typed interfaces и делегирует реальную HTTP-работу OkHttp.

### OkHttp

OkHttp - low-level HTTP client, который выполняет network requests и управляет connections, timeouts, redirects, cache и connection pooling.

Retrofit обычно использует OkHttp под капотом, но OkHttp можно использовать напрямую, когда нужен ручной контроль над request/response.

В Android нужно настраивать timeouts, cache, TLS/certificates при необходимости и не выполнять synchronous calls на main thread.

Typical OkHttp configuration включает:

- connection timeout;
- read/write timeout;
- interceptors;
- cache;
- TLS/certificate configuration;
- connection pooling.

**Коротко:** OkHttp - реальный HTTP client; Retrofit - удобный typed API layer поверх него.

### Interceptors

OkHttp interceptor - middleware вокруг request/response. Он может добавлять headers, auth token, logging, metrics, retry или обрабатывать common network behavior.

Application interceptors видят logical request, а network interceptors ближе к реальному network exchange и могут видеть redirects, cache и network details.

Common cases:

- Authorization header;
- refresh token flow;
- logging in debug builds;
- common headers;
- user-agent;
- app version;
- locale;
- error normalization;
- metrics and timing.

Типичная упрощённая chain выглядит так:

```text
App code
  ↓
Retrofit service
  ↓
OkHttp interceptors
  ↓
Network
  ↓
Backend
```

**Важно:** не логируй sensitive data и не запускай heavy/blocking logic внутри interceptor без необходимости.

**Коротко:** interceptors централизуют cross-cutting network logic вроде auth, logging, metrics и common headers.

### Authentication interceptors

Authentication часто реализуют через interceptor, который автоматически прикрепляет common headers к каждому request.

Typical responsibilities:

- adding the `Authorization` header;
- attaching access tokens;
- adding app version or locale headers;
- refreshing tokens when appropriate;
- keeping auth logic out of every Retrofit service method.

Example:

```kotlin
class AuthInterceptor(
    private val tokenProvider: TokenProvider
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val token = tokenProvider.accessToken()

        val request = chain.request()
            .newBuilder()
            .addHeader("Authorization", "Bearer $token")
            .build()

        return chain.proceed(request)
    }
}
```

Token refresh нужно проектировать аккуратно. Если несколько requests одновременно получают `401`, app должен избегать нескольких конкурирующих refresh calls.

**Коротко:** auth interceptors убирают дублирование header logic, но token refresh требует аккуратной concurrency и failure handling.

## Payload and Errors

### Serialization

Serialization - преобразование JSON/protobuf/raw response в Kotlin/Java models и обратно.

С Retrofit это обычно делается через converter: Gson, Moshi, kotlinx.serialization или protobuf converter. Converter превращает response body в DTO, а request body - в нужный wire format.

Pitfalls:

- nullable fields;
- unknown fields;
- date/time formats;
- enum evolution;
- default values;
- missing fields;
- mismatch between API contract and DTO;
- backend returning a different shape for error responses.

DTOs обычно должны оставаться в data layer. Repository маппит их в domain или UI models перед тем, как отдавать в остальную часть app.

**Коротко:** serialization маппит network payloads в DTOs; app code должен validate и map DTOs перед тем, как отдавать domain/UI models.

### Network error handling

Network error handling лучше держать в repository/data layer: `IOException` / timeout, HTTP non-2xx, parsing error и backend business error превращаются в понятную app error model.

Retrofit может возвращать `Response<T>` для ручной проверки `code` / `body` или бросать exception в зависимости от call adapter и API signature. Для suspend calls cancellation нужно обрабатывать отдельно.

UI не должен знать детали OkHttp exceptions, `Retrofit Response.errorBody()` или JSON error schema. Он должен получать clear state: loading/content/error/retry.

Common data-layer model может разделять несколько категорий:

```kotlin
sealed interface NetworkResult<out T> {
    data class Success<T>(val data: T) : NetworkResult<T>
    data class HttpError(val code: Int, val message: String?) : NetworkResult<Nothing>
    data class NetworkError(val cause: Throwable) : NetworkResult<Nothing>
    data class SerializationError(val cause: Throwable) : NetworkResult<Nothing>
}
```

Точная model зависит от проекта, но идея стабильна: превращать low-level networking details в app-level errors на boundary.

**Коротко:** маппь Retrofit/OkHttp errors в domain/UI errors на data boundary, а не внутри UI code.

## Debugging API Requests

### Reading HTTP responses

Хотя HTTP status codes относятся к самому HTTP protocol, это одна из первых вещей, которую Android developers проверяют при debugging API requests.

Вместо того чтобы обрабатывать все errors одинаково, сначала определи response category и проверь наиболее вероятную причину.

| Status | First things to check |
|--------|------------------------|
| `400` | Request body, JSON serialization, query/path parameters |
| `401` | Authorization header, access token, refresh token flow |
| `403` | Backend permissions, user roles, feature flags |
| `404` | Base URL, endpoint, API version, resource ID |
| `409` | Resource version, duplicate request, business state |
| `422` | Request payload validation |
| `429` | Rate limiting, `Retry-After` header |
| `500` | Backend failure |
| `502` | Gateway or upstream service |
| `503` | Temporary maintenance or overload |
| `504` | Backend timeout |

Эта table не заменяет понимание HTTP status codes. Она служит practical debugging checklist для Android applications.

### Logging

Logging interceptor - один из самых полезных debugging tools во время development.

Он позволяет developers смотреть outgoing requests и incoming responses, включая URLs, headers, payloads, response codes и execution time.

В Android projects network logging обычно включают только в debug builds:

```kotlin
val logging = HttpLoggingInterceptor().apply {
    level = if (BuildConfig.DEBUG) {
        HttpLoggingInterceptor.Level.BODY
    } else {
        HttpLoggingInterceptor.Level.NONE
    }
}
```

Request и response bodies часто содержат sensitive information и не должны логироваться в production.

**Коротко:** logging interceptors отлично подходят для debugging, но body logging обычно нужно ограничивать debug builds.

### Practical debugging checklist

Прежде чем считать, что backend сломан, проверь:

- Base URL
- Endpoint path
- HTTP method
- Request headers
- Authorization token
- Serialized request body
- Query and path parameters
- Network logs
- Response body
- HTTP status code
- Retrofit annotations
- Converter configuration
- Timeout configuration
- Interceptor registration order

Многие API issues можно быстро найти, если системно проверить эти пункты.

### Common Retrofit / OkHttp mistakes

Типичные проблемы в Android projects:

- wrong base URL;
- missing trailing slash in Retrofit base URL;
- wrong `@Path` or `@Query` usage;
- using `@Body` with an unexpected DTO shape;
- missing `Content-Type`;
- missing or stale `Authorization` header;
- interceptor not registered in the OkHttp client used by Retrofit;
- logging interceptor enabled too late or not enabled in debug builds;
- DTO nullability not matching backend response;
- enum value added by backend but not handled by the app;
- timeout too short for slow networks;
- retrying non-idempotent requests without backend support;
- catching `Exception` and accidentally swallowing coroutine cancellation.

**Коротко:** многие networking bugs возникают из-за небольших mismatches между Retrofit annotations, DTOs, headers, interceptors и backend contract.

### Production recommendations

On-device inspectors, IDE tooling, proxies, request correlation и безопасность payloads разобраны в [Network Inspection](../tools/network-inspection.md).

По возможности держи network logging выключенным в production builds.

Никогда не логируй sensitive information:

- access tokens;
- refresh tokens;
- passwords;
- personal user data;
- payment information;
- full request/response bodies containing private data.

Для production diagnostics лучше использовать более безопасную observability:

- response codes;
- endpoint names without sensitive parameters;
- request duration;
- failure category;
- correlation/request IDs;
- Crashlytics/Sentry breadcrumbs without private payloads.

Logging interceptor очень полезен для development, но production logging всегда должен балансировать debugging needs с security и privacy requirements.

**Коротко:** production networking logs должны помогать диагностировать failures, не раскрывая secrets или personal data.
