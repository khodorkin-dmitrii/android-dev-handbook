# Retrofit / OkHttp

Retrofit usually describes a type-safe API layer, while OkHttp performs the actual HTTP work: connections, requests, responses, interceptors, cache and timeouts.

## Clients

### Retrofit

Retrofit is a type-safe HTTP client layer for Android/JVM that describes backend API through Kotlin/Java interfaces and annotations.

It turns methods such as `@GET`, `@POST`, `@Path`, `@Query`, `@Body` into HTTP calls and usually works on top of OkHttp. In modern Kotlin code, Retrofit often returns suspend functions or `Flow` / `Result` through the repository layer.

**Important:** Retrofit service should not be exposed directly to UI / `ViewModel`. Keep it in the data layer and map DTOs/errors into domain or UI models.

**In short:** Retrofit describes REST API as interfaces and delegates actual HTTP work to OkHttp.

### OkHttp

OkHttp is a low-level HTTP client that performs network requests and manages connections, timeouts, redirects, cache and connection pooling.

Retrofit usually uses OkHttp under the hood, but OkHttp can also be used directly when manual control over request/response is needed.

In Android, configure timeouts, cache, TLS/certificates when needed, and do not execute synchronous calls on the main thread.

**In short:** OkHttp is the actual HTTP client; Retrofit is a convenient typed API layer on top of it.

### Interceptors

An OkHttp interceptor is middleware around request/response. It can add headers, auth token, logging, metrics, retry or handle common network behavior.

Application interceptors see the logical request, while network interceptors are closer to the real network exchange and can see redirects/cache/network details.

Common cases: Authorization header, refresh token flow, logging in debug builds, common headers, user-agent, error normalization.

**Important:** do not log sensitive data and do not run heavy/blocking logic inside an interceptor without a need.

**In short:** interceptors centralize cross-cutting network logic like auth, logging and common headers.

## Payload and Errors

### Serialization

Serialization is converting JSON/protobuf/raw response into Kotlin/Java models and back.

With Retrofit this is usually done through a converter: Gson, Moshi, kotlinx.serialization or protobuf converter. The converter turns response body into DTO, and request body into the required wire format.

Pitfalls: nullable fields, unknown fields, date/time formats, enum evolution, default values and mismatch between API contract and DTO.

**In short:** serialization maps network payloads to DTOs; app code should validate and map DTOs before exposing domain/UI models.

### Network error handling

Network error handling should stay in the repository/data layer: `IOException` / timeout, HTTP non-2xx, parsing error and backend business error are converted into a clear app error model.

Retrofit can return `Response<T>` for manual `code` / `body` checks or throw an exception depending on the call adapter and API signature. For suspend calls, cancellation should be handled separately.

UI should not know details of OkHttp exceptions, `Retrofit Response.errorBody()` or JSON error schema. It should receive clear state: loading/content/error/retry.

**In short:** map Retrofit/OkHttp errors into domain/UI errors at the data boundary, not inside UI code.
