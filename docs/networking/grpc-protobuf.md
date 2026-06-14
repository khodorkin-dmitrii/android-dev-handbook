# gRPC / Protobuf

gRPC and Protocol Buffers are more common in projects that need a strict typed contract, binary serialization, streaming or a shared API contract across several platforms.

## gRPC

### What is gRPC?

gRPC is an RPC framework where the client calls remote methods on the server almost like regular functions, and the API contract is described in `.proto` files.

Under the hood, gRPC usually uses HTTP/2, binary serialization through Protocol Buffers, typed service definitions and code generation for client/server stubs.

In Android, gRPC can be useful when a strict contract, efficient binary protocol, streaming, low-latency communication or shared API contract across several platforms is needed.

Drawbacks: harder debugging without special tools, less readable payload compared with JSON, required code generation and careful schema evolution.

**In short:** gRPC is a type-safe RPC framework where API methods and messages are defined in proto files and client/server code is generated from that contract.

### What are Protocol Buffers?

Protocol Buffers, or protobuf, is a language-neutral binary serialization format and IDL for describing message structure.

The `.proto` file describes messages, fields, field numbers, types, enums and services. Kotlin/Java models and gRPC stubs are generated from this contract.

```proto
message User {
  string id = 1;
  string name = 2;
  int32 age = 3;
}
```

The key idea: in protobuf, field numbers matter more than field names. Therefore old field numbers must not be reused with a different meaning when the schema changes.

Benefits of protobuf: compact binary payload, fast parsing, strict schema and code generation. Drawbacks: payload is not human-readable like JSON, and schema evolution requires discipline.

**In short:** protobuf defines strongly typed messages and serializes them into compact binary data; field numbers are part of the compatibility contract.

### REST vs gRPC

REST is usually built around resources, URLs and HTTP methods: `GET /users/1`, `POST /orders`. gRPC is built around service methods: `UserService.GetUser`, `OrderService.CreateOrder`.

REST usually uses JSON, is easier to debug with regular HTTP tools and is convenient for public APIs, browser clients and simple CRUD scenarios.

gRPC is usually more efficient in payload size and latency, provides a strict contract, code generation and strong streaming support over HTTP/2.

In Android, the choice depends on the backend ecosystem and the task. For a regular mobile API, REST + Retrofit is often enough. gRPC is useful if the project is already built around protobuf/gRPC, needs streaming updates, typed contracts or high network-layer efficiency.

**Important:** gRPC does not automatically make architecture better. Repository/data layer, error mapping, timeout/retry policy, cancellation and mapping generated models into domain/UI models are still needed.

**In short:** REST is resource-oriented and human-readable, gRPC is service-method-oriented, strongly typed and efficient, but requires generated code and tooling.

### Unary / streaming calls

Unary call is the simplest gRPC call type: the client sends one request and receives one response. It is similar to a regular HTTP request/response.

Server streaming means the client sends one request, and the server returns a stream of responses. Examples: subscription to live status, progress updates or timeline events.

Client streaming means the client sends a stream of requests, and the server returns one response. Examples: uploading a series of chunks or a set of events after which the server returns a final result.

Bidirectional streaming means client and server exchange streams at the same time. It is similar to a persistent realtime channel and works for chat-like, telemetry or interactive flows.

In Android, streaming is convenient to map into `Flow`, but lifecycle-aware collection, cancellation, reconnect strategy and backpressure/buffering at the chosen gRPC/Kotlin wrapper level should be considered.

**In short:** gRPC supports unary, server streaming, client streaming and bidirectional streaming calls; streaming is one of its main advantages over typical REST APIs.

### gRPC in Android

In Android, a gRPC client is usually generated from `.proto` contracts. The data layer calls generated stubs, and repository maps protobuf responses into domain/UI models.

For Kotlin code, coroutine-friendly stubs are often used: unary calls look like suspend functions, and streaming calls can be represented as `Flow`.

Generated protobuf models should not be passed directly into UI / `ViewModel`. They are network contract models, not necessarily convenient domain models.

Error handling differs from REST: instead of HTTP status codes, the client often works with gRPC status codes such as `OK`, `CANCELLED`, `UNKNOWN`, `INVALID_ARGUMENT`, `NOT_FOUND`, `PERMISSION_DENIED`, `UNAUTHENTICATED`, `UNAVAILABLE`, `DEADLINE_EXCEEDED`.

**In short:** on Android, gRPC belongs in the data layer; repositories should hide generated stubs and map protobuf/status errors into app-level models.

### Schema evolution / backward compatibility

Protobuf supports backward/forward compatibility well if schema-change rules are followed.

New fields with new field numbers can be added: old clients will ignore them, and new clients can read them if the server sends them.

Do not reuse deleted field numbers or change the meaning of an existing field. If a field is removed, its number and name should be marked as `reserved`.

Changing the type of an existing field is dangerous because old and new clients may start reading data incorrectly. For a new meaning, add a new field with a new number.

**In short:** protobuf compatibility is based on stable field numbers; add new fields safely, but do not reuse or repurpose old field numbers.
