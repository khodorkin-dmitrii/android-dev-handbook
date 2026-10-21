# Networking

This section covers how an Android client communicates with APIs: HTTP semantics, transport libraries, alternative API protocols, and the boundary between network responses and application models.

## Suggested path

Start with HTTP and REST, then see how Retrofit and OkHttp implement requests on Android. Explore GraphQL or gRPC when your backend uses those contracts. Across all approaches, consider timeouts, cancellation, error mapping, authentication, and unreliable connections. See [Security](../security/index.md) for TLS and token handling; see [Offline-First Mobile Application](../engineering/system-design/offline-first-mobile.md) for local data and synchronization.

## Articles

- [HTTP / REST](http-rest.md) - methods, status codes, caching, retries, and API contracts.
- [Retrofit / OkHttp](retrofit-okhttp.md) - request construction, interceptors, serialization, and error handling.
- [GraphQL](graphql.md) - queries, mutations, schema-driven clients, and caching trade-offs.
- [gRPC / Protobuf](grpc-protobuf.md) - typed contracts, serialization, streaming, and mobile constraints.
