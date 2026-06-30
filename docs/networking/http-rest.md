# HTTP / REST

HTTP and REST are the foundation of most Android network APIs: request/response, status codes, headers, JSON body and error handling rules.

## HTTP

HTTP (Hypertext Transfer Protocol) is an application-layer protocol for exchanging data between client and server using the request/response model.

In Android, HTTP is used in almost all network APIs: the app sends a request with method, URL, headers and optional body, and the server returns a response with status code, headers and optional body, most often JSON.

HTTP itself is stateless: there is no built-in connection between two requests. Session and authentication are usually built on top of HTTP through cookies, tokens or headers.

**In short:** HTTP is a stateless application-layer request/response protocol; Android apps usually use it through OkHttp/Retrofit to communicate with backend APIs.

### What is REST?

REST (Representational State Transfer) is an architectural style for client-server APIs where data is represented as resources, usually available through URLs.

Operations on resources are expressed through HTTP methods. The response usually contains a representation of the resource, for example JSON.

Key REST ideas:

- client-server separation;
- stateless requests;
- cacheability;
- uniform interface;
- clear resource URLs;
- meaningful HTTP methods and status codes.

**Important:** not every JSON-over-HTTP API is strict REST. In Android practice, it is usually more important to understand practical REST-like APIs and work correctly with methods, headers, status codes and error responses.

**In short:** REST is a resource-oriented API style over HTTP: resources have URLs, operations use HTTP methods, requests are stateless, and responses use status codes and representations like JSON.

### HTTP methods

HTTP methods describe what the client wants to do with a resource.

| Method | Typical purpose | Safe | Idempotent |
|--------|-----------------|------|------------|
| `GET` | Read a resource | Yes | Yes |
| `POST` | Create a resource or start an action | No | Usually no |
| `PUT` | Replace a resource | No | Yes |
| `PATCH` | Partially update a resource | No | Usually no |
| `DELETE` | Delete a resource | No | Yes |

`GET` is used to read a resource. It should be safe and idempotent: repeating `GET` should not change server state. Parameters are often passed in the query string, and the response can be cached.

`POST` is used to send data: create a resource, submit a form, start a command or trigger an action. `POST` usually has a request body and does not guarantee idempotency: a retry can create a duplicate or execute an action twice.

`PUT` usually replaces a resource with a full new representation. It is normally idempotent: sending the same `PUT` request multiple times should produce the same final state.

`PATCH` partially updates a resource. It is useful when the client sends only changed fields, but its idempotency depends on API design.

`DELETE` removes a resource. It is normally idempotent: deleting the same resource again should not create a different result, although the server may return `404` after the first deletion.

In Android, avoid putting sensitive or large data into query parameters and retry non-idempotent requests carefully. For critical operations, the backend should support an idempotency key or safe operation status checks.

**In short:** HTTP methods are part of the API contract. `GET` reads, `POST` creates or starts actions, `PUT` replaces, `PATCH` partially updates, and `DELETE` removes.

### GET vs POST

`GET` is for safe resource reads. It should not change server state, and it is usually cacheable.

`POST` is for sending data to the server. It is often used for creation, form submission, commands, payments, login and other actions.

The practical difference matters for retries. Retrying `GET` is usually safe. Retrying `POST` can be dangerous if the server does not support idempotency, because the same operation may be executed more than once.

For example, retrying a failed profile fetch is usually fine. Retrying a payment confirmation without an idempotency key may create an incorrect user experience or duplicate operation.

**In short:** `GET` is for safe reads, `POST` is for sending data or starting actions; retrying `GET` is usually safer than retrying `POST`.

### HTTP status codes

An HTTP status code tells the client how the server processed a request. It is part of the HTTP protocol and should be treated as part of the API contract rather than just an error indicator.

Status codes are grouped into five categories:

- `1xx` - Informational
- `2xx` - Success
- `3xx` - Redirection
- `4xx` - Client error
- `5xx` - Server error

The most common codes are:

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

Some status codes deserve special attention in mobile apps:

- `401` usually means authentication is required or the access token has expired.
- `403` means authentication succeeded, but the client does not have permission to perform the operation.
- `404` may mean wrong endpoint, wrong ID, deleted resource or an API version mismatch.
- `409` indicates a conflict with the current resource state, for example optimistic locking or duplicate operations.
- `422` means the request format is correct, but business validation failed.
- `429` indicates rate limiting. Clients should respect the `Retry-After` header if it is present.
- `5xx` errors usually mean the server or upstream dependency failed, but the app still needs to show a useful temporary error state.

In Android, do not map all non-2xx responses into one generic error. `401` can lead to token refresh or logout, `403` to access denied, `404` to empty/not found state, and `429` / `5xx` to retry, backoff or temporary error.

**In short:** HTTP status codes describe the outcome of a request and form part of the API contract. Clients should distinguish authentication, authorization, validation, conflicts, rate limiting and server failures instead of treating every non-2xx response as a generic error.

### Headers and body

HTTP headers carry metadata about the request or response.

Common request headers include:

- `Authorization` - access token or credentials;
- `Content-Type` - format of the request body;
- `Accept` - expected response format;
- `User-Agent` - client information;
- custom headers for app version, locale, device or feature flags.

The request body contains data sent to the server. In Android APIs it is often JSON, but it can also be multipart form data, protobuf or another format.

The response body contains returned data or error details. A successful response usually maps to a DTO, while an error response may contain backend-specific error code, message and validation details.

**In short:** headers describe metadata and authentication; body carries request or response payload.

### Error mapping in Android

Network error handling is better separated into levels: transport errors, HTTP protocol errors, serialization errors and business errors.

Transport errors mean no network, timeout, DNS/TLS problem or cancelled request. In Kotlin/OkHttp-based code these often appear as `IOException` or timeout-related failures.

HTTP errors mean the server responded, but the status code is non-2xx.

Serialization errors mean the response could not be parsed because the payload does not match the expected model or converter configuration.

Business errors mean the backend returned a valid response with a domain-specific problem, for example validation failure, insufficient funds, unavailable feature or invalid operation state.

A good place for mapping is the data/repository layer: Retrofit/OkHttp exceptions and backend error body are converted into a domain/UI error model. UI should not parse HTTP codes, JSON error body or `IOException` directly.

Retry fits transient problems: timeout, connection issue, `5xx`, sometimes `429` with backoff. Do not retry validation errors, invalid credentials, forbidden access or non-idempotent operations without idempotency.

**In short:** in Android, map low-level network, protocol, serialization and business errors into app-level errors in the repository/domain layer, then let UI render a clear user-facing state.