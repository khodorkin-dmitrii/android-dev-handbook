# gRPC / Protobuf

gRPC is an RPC framework built around typed service methods. Protocol Buffers (protobuf) is its default Interface Definition Language and message format, although the two technologies can also be used separately. They are useful when an API needs code-generated contracts, compact binary messages or streaming.

## Service contract and generated code

A `.proto` file describes messages and service methods. The compiler and gRPC plugins generate message classes and client/server APIs for the selected languages.

```proto
syntax = "proto3";

message RobotRequest {
  string robot_id = 1;
}

message RobotStatus {
  string robot_id = 1;
  int32 battery_percent = 2;
}

service RobotService {
  rpc GetStatus(RobotRequest) returns (RobotStatus);
  rpc ObserveStatus(RobotRequest) returns (stream RobotStatus);
}
```

Field numbers identify protobuf fields on the wire. Names improve source readability, but renaming a field does not change its binary identity. Generated protobuf types are transport-contract models; map them to domain or UI models when the layers have different needs.

## RPC types

gRPC defines four method shapes:

- **Unary**: one request, one response.
- **Server streaming**: one request, a stream of responses.
- **Client streaming**: a stream of requests, one response.
- **Bidirectional streaming**: both sides exchange independent streams. Message order is preserved within each stream of one RPC.

With gRPC Kotlin, generated coroutine stubs can expose unary calls as `suspend` functions and streams as `Flow`. A stream still needs lifecycle-aware collection, cancellation and an explicit reconnection policy. Flow control exists at the gRPC transport level, but application buffering and slow-consumer behavior must still be designed.

## Android client responsibilities

Keep the generated stub and channel in the data layer and normally reuse the channel instead of creating one per request. Configure transport security for production and close long-lived resources when their owner is destroyed.

Set a deadline for calls: otherwise a client may wait indefinitely, depending on the API defaults. Coroutine cancellation should propagate to the RPC, but cancellation does not roll back work already completed on the server.

Map gRPC statuses such as `UNAUTHENTICATED`, `PERMISSION_DENIED`, `NOT_FOUND`, `UNAVAILABLE` and `DEADLINE_EXCEEDED` into application errors. Retry only transient failures and only when the operation is safe to repeat or has an idempotency mechanism; exponential backoff does not make a non-idempotent call safe.

## Protobuf compatibility

Schema evolution is safe only when wire-compatibility rules are respected:

- add new fields with new numbers;
- never renumber fields or reuse a deleted number;
- reserve the number and preferably the name of a removed field;
- avoid changing a field type or semantic meaning in place;
- do not assume a scalar's default value means it was explicitly sent - use field presence (`optional`) when that distinction matters;
- keep an enum zero value such as `STATUS_UNSPECIFIED` for an unknown or unset state.

Old readers normally preserve or ignore unknown fields depending on how a message is processed, so avoid converting through representations that discard them during read-modify-write flows.

## gRPC vs REST

REST is commonly resource-oriented and uses human-readable JSON, which is convenient for public APIs and ordinary HTTP tooling. gRPC is service-method-oriented, usually runs over HTTP/2, provides generated types and supports streaming directly. Binary messages can reduce payload size, but real performance depends on the request pattern, backend and network. For a conventional mobile CRUD API, REST with Retrofit may be simpler; gRPC is compelling when the backend already uses protobuf, strict cross-platform contracts or streaming.

Related: [HTTP / REST](http-rest.md), [Retrofit / OkHttp](retrofit-okhttp.md), [Flow Basics](../coroutines-flow/flow-basics.md).

Sources: [gRPC core concepts](https://grpc.io/docs/what-is-grpc/core-concepts/), [gRPC deadlines](https://grpc.io/docs/guides/deadlines/), [Proto3 language guide](https://protobuf.dev/programming-guides/proto3/), [Protobuf best practices](https://protobuf.dev/best-practices/dos-donts/).
