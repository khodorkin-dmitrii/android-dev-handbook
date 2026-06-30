# Retrofit / OkHttp

Retrofit usually describes a type-safe API layer, while OkHttp performs the actual HTTP work: connections, requests, responses, interceptors, cache and timeouts.

## Clients

### Retrofit

Retrofit is a type-safe HTTP client layer for Android/JVM that describes backend API through Kotlin/Java interfaces and annotations.

It turns methods such as `@GET`, `@POST`, `@PUT`, `@PATCH`, `@DELETE`, `@Path`, `@Query`, `@Body` and `@Header` into HTTP calls and usually works on top of OkHttp.

In modern Kotlin code, Retrofit commonly exposes `suspend` functions from the data layer:

```kotlin
interface UserApi {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") id: String): UserDto

    @POST("users")
    suspend fun createUser(@Body body: CreateUserRequest): UserDto
}
```

Retrofit can also return `Response<T>` when the caller needs manual access to the HTTP status code, headers or error body.

```kotlin
@GET("users/{id}")
suspend fun getUserResponse(@Path("id") id: String): Response<UserDto>
```

**Important:** Retrofit service should not be exposed directly to UI or `ViewModel`. Keep it in the data layer and map DTOs/errors into domain or UI models.

**In short:** Retrofit describes REST API as typed interfaces and delegates actual HTTP work to OkHttp.

### OkHttp

OkHttp is a low-level HTTP client that performs network requests and manages connections, timeouts, redirects, cache and connection pooling.

Retrofit usually uses OkHttp under the hood, but OkHttp can also be used directly when manual control over request/response is needed.

In Android, configure timeouts, cache, TLS/certificates when needed, and do not execute synchronous calls on the main thread.

Typical OkHttp configuration includes:

- connection timeout;
- read/write timeout;
- interceptors;
- cache;
- TLS/certificate configuration;
- connection pooling.

**In short:** OkHttp is the actual HTTP client; Retrofit is a convenient typed API layer on top of it.

### Interceptors

An OkHttp interceptor is middleware around request/response. It can add headers, auth token, logging, metrics, retry or handle common network behavior.

Application interceptors see the logical request, while network interceptors are closer to the real network exchange and can see redirects, cache and network details.

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

A typical simplified chain looks like this:

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

**Important:** do not log sensitive data and do not run heavy/blocking logic inside an interceptor without a need.

**In short:** interceptors centralize cross-cutting network logic like auth, logging, metrics and common headers.

### Authentication interceptors

Authentication is often implemented through an interceptor that automatically attaches common headers to every request.

Typical responsibilities include:

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

Token refresh should be designed carefully. If several requests fail with `401` at the same time, the app should avoid triggering multiple competing refresh calls.

**In short:** auth interceptors remove duplicated header logic, but token refresh needs careful concurrency and failure handling.

## Payload and Errors

### Serialization

Serialization is converting JSON/protobuf/raw response into Kotlin/Java models and back.

With Retrofit this is usually done through a converter: Gson, Moshi, kotlinx.serialization or protobuf converter. The converter turns response body into DTO, and request body into the required wire format.

Pitfalls:

- nullable fields;
- unknown fields;
- date/time formats;
- enum evolution;
- default values;
- missing fields;
- mismatch between API contract and DTO;
- backend returning a different shape for error responses.

DTOs should usually stay in the data layer. The repository maps them into domain or UI models before exposing them to the rest of the app.

**In short:** serialization maps network payloads to DTOs; app code should validate and map DTOs before exposing domain/UI models.

### Network error handling

Network error handling should stay in the repository/data layer: `IOException` / timeout, HTTP non-2xx, parsing error and backend business error are converted into a clear app error model.

Retrofit can return `Response<T>` for manual `code` / `body` checks or throw an exception depending on the call adapter and API signature. For suspend calls, cancellation should be handled separately.

UI should not know details of OkHttp exceptions, `Retrofit Response.errorBody()` or JSON error schema. It should receive clear state: loading/content/error/retry.

A common data-layer model can separate several categories:

```kotlin
sealed interface NetworkResult<out T> {
    data class Success<T>(val data: T) : NetworkResult<T>
    data class HttpError(val code: Int, val message: String?) : NetworkResult<Nothing>
    data class NetworkError(val cause: Throwable) : NetworkResult<Nothing>
    data class SerializationError(val cause: Throwable) : NetworkResult<Nothing>
}
```

The exact model depends on the project, but the idea is stable: convert low-level networking details into app-level errors at the boundary.

**In short:** map Retrofit/OkHttp errors into domain/UI errors at the data boundary, not inside UI code.

## Debugging API Requests

### Reading HTTP responses

Although HTTP status codes belong to the HTTP protocol itself, they are one of the first things Android developers inspect while debugging API requests.

Rather than treating every error the same way, start by identifying the response category and checking the most likely cause.

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

This table is not a replacement for understanding HTTP status codes. Instead, it serves as a practical debugging checklist for Android applications.

### Logging

A logging interceptor is one of the most valuable debugging tools during development.

It allows developers to inspect outgoing requests and incoming responses, including URLs, headers, payloads, response codes and execution time.

In Android projects, network logging is commonly enabled only in debug builds:

```kotlin
val logging = HttpLoggingInterceptor().apply {
    level = if (BuildConfig.DEBUG) {
        HttpLoggingInterceptor.Level.BODY
    } else {
        HttpLoggingInterceptor.Level.NONE
    }
}
```

Request and response bodies often contain sensitive information and should not be logged in production.

**In short:** logging interceptors are excellent for debugging, but body logging should normally be limited to debug builds.

### Practical debugging checklist

Before assuming the backend is broken, verify:

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

Many API issues can be identified quickly by systematically checking these items.

### Common Retrofit / OkHttp mistakes

Typical problems in Android projects include:

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

**In short:** many networking bugs come from small mismatches between Retrofit annotations, DTOs, headers, interceptors and backend contract.

### Production recommendations

Keep network logging disabled in production builds whenever possible.

Never log sensitive information such as:

- access tokens;
- refresh tokens;
- passwords;
- personal user data;
- payment information;
- full request/response bodies containing private data.

For production diagnostics, prefer safer observability:

- response codes;
- endpoint names without sensitive parameters;
- request duration;
- failure category;
- correlation/request IDs;
- Crashlytics/Sentry breadcrumbs without private payloads.

A logging interceptor is extremely valuable for development, but production logging should always balance debugging needs with security and privacy requirements.

**In short:** production networking logs should help diagnose failures without exposing secrets or personal data.