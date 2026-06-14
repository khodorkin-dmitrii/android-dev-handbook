# HTTP / REST

HTTP and REST are the foundation of most Android network APIs: request/response, status codes, headers, JSON body and error handling rules.

## HTTP

### What is HTTP?

HTTP (Hypertext Transfer Protocol) is an application-layer protocol for exchanging data between client and server using the request/response model.

In Android, HTTP is used in almost all network APIs: the app sends a request with method, URL, headers and optional body, and the server returns a response with status code, headers and optional body, most often JSON.

HTTP itself is stateless: there is no built-in connection between two requests. Session/auth is usually built on top of HTTP through cookies, tokens or headers.

**In short:** HTTP is a stateless application-layer request/response protocol; Android apps usually use it through OkHttp/Retrofit to communicate with backend APIs.

### What is REST?

REST (Representational State Transfer) is an architectural style for client-server APIs where data is represented as resources, usually available through URLs.

Operations on resources are expressed through HTTP methods: `GET` reads, `POST` creates or starts an action, `PUT` / `PATCH` update, and `DELETE` removes. The response usually contains a representation of the resource, for example JSON.

Key REST ideas: client-server separation, stateless requests, cacheability, uniform interface and clear status code usage.

**Important:** not every JSON-over-HTTP API is strict REST, but in Android practice it is important to understand practical REST APIs and work correctly with methods/status codes.

**In short:** REST is a resource-oriented API style over HTTP: resources have URLs, operations use HTTP methods, requests are stateless, and responses use status codes and representations like JSON.

### GET vs POST

`GET` is used to read a resource. It should be safe and idempotent: repeating `GET` should not change server state. Parameters are often passed in the query string, and the response can be cached.

`POST` is used to send data: create a resource, submit a form, start a command/action. `POST` usually has a request body and does not guarantee idempotency: a retry can create a duplicate or execute an action twice.

In Android, avoid putting sensitive or large data into query parameters and retry `POST` carefully. For critical operations, the backend should support an idempotency key or safe operation status checks.

**In short:** `GET` is for safe resource reads, `POST` is for sending data or creating actions; retrying `GET` is usually safer than retrying `POST`.

### HTTP status codes

HTTP status code shows the result of processing a request. For the client, it is the first signal for interpreting the response.

Main groups: `1xx` - informational, `2xx` - success, `3xx` - redirection, `4xx` - client error, `5xx` - server error.

Common codes: `200 OK`, `201 Created`, `204 No Content`, `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `409 Conflict`, `422 Validation Error`, `429 Too Many Requests`, `500 Internal Server Error`, `503 Service Unavailable`.

In Android, do not map all non-2xx responses into one generic error. `401` can lead to logout/refresh token, `403` to access denied, `404` to empty/not found state, and `429` / `5xx` to retry/backoff or temporary error.

**In short:** status codes are part of the API contract; client code should distinguish success, auth, validation, not found, rate limit and server errors.

### Error mapping in Android

Network error handling is better separated into levels: transport errors, HTTP protocol errors, serialization errors and business errors.

Transport errors mean no network, timeout, DNS/TLS problem or cancelled request. HTTP errors mean the server responded, but the status code is non-2xx. Serialization errors mean the response could not be parsed. Business errors mean the backend returned a valid response with a domain-specific problem.

A good place for mapping is the data/repository layer: Retrofit/OkHttp exceptions and backend error body are converted into a domain/UI error model. UI should not parse HTTP codes, JSON error body or `IOException` directly.

Retry fits transient problems: timeout, connection issue, `5xx`, sometimes `429` with backoff. Do not retry validation errors, invalid credentials, forbidden access or non-idempotent operations without idempotency.

**In short:** in Android, map low-level network/protocol/serialization errors into app-level errors in repository/domain layer, then let UI render a clear user-facing state.
