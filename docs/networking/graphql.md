# GraphQL

GraphQL is an API query language: a client selects fields from a server-defined schema. It is useful when a screen needs related data in a specific shape, but does not automatically eliminate latency or make caching simple.

## Operations and schema

- A **query** reads data. A **mutation** performs a write or server-side action; do not blindly retry it because it may not be idempotent.
- A **subscription** delivers updates over time. The transport (often WebSocket) depends on the client and server, not on the GraphQL query language itself.
- The **schema** defines types, fields, arguments and nullability. Client operations select fields from that contract; a generated Kotlin type represents the selected result, not necessarily the entire schema type.

Use variables for dynamic values rather than building query strings by interpolation:

```graphql
query RobotStatus($id: ID!) {
  robot(id: $id) {
    id
    name
    batteryPercent
  }
}
```

The client supplies `$id` separately. `ID!` means the variable cannot be null. The server may still return a nullable `robot` if the schema declares it nullable. Fragments can share field selections across operations.

## Responses and errors

A response can contain `data` and `errors` together: one field may fail while other data remains usable. Treat a transport failure, a GraphQL execution error, and a domain-level failure represented in `data` as distinct cases. Check schema nullability and decide explicitly whether partial data is acceptable for the screen. An HTTP success status alone does not mean the operation succeeded without GraphQL errors.

## GraphQL vs REST

REST commonly offers resource-oriented endpoints with server-defined response shapes; GraphQL usually exposes a schema through a single endpoint and lets clients choose fields. This can reduce overfetching and some round trips, but a complex query may still be expensive on the server. HTTP caching and request inspection are generally simpler with conventional REST; GraphQL often needs operation-aware tooling and a deliberate client cache strategy. Choose by API and product needs, not by a blanket performance claim.

## Apollo Kotlin on Android

Apollo Kotlin generates type-safe Kotlin models from a schema and `.graphql` operations, and executes queries, mutations and subscriptions. Keep the client in the data layer; repositories can map generated response types into stable domain or UI models. Treat schema updates as a build-time compatibility concern.

Configure fetch and cache behavior deliberately. Apollo's normalized cache is an option, not an automatic guarantee that every operation has correct offline behavior; record identity and mutation updates matter. Also plan lifecycle-aware subscription collection, reconnection, and cancellation.

Related: [HTTP / REST](http-rest.md), [Retrofit / OkHttp](retrofit-okhttp.md), [StateFlow & SharedFlow](../coroutines-flow/stateflow-sharedflow.md).

Sources: [GraphQL queries](https://graphql.org/learn/queries/), [GraphQL responses](https://graphql.org/learn/response/), [Apollo Kotlin](https://www.apollographql.com/docs/kotlin), [Apollo normalized cache](https://www.apollographql.com/docs/kotlin/caching/normalized-cache).
