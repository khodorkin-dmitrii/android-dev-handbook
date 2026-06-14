# gRPC / Protobuf

gRPC и Protocol Buffers чаще встречаются в проектах, где нужен строгий typed contract, binary serialization, streaming или единый API contract между несколькими платформами.

## gRPC

### Что такое gRPC?

gRPC - RPC framework, где client вызывает remote methods на server почти как обычные функции, а контракт API описывается в `.proto` файлах.

Под капотом gRPC обычно использует HTTP/2, binary serialization через Protocol Buffers, typed service definitions и code generation для client/server stubs.

В Android gRPC может быть полезен, когда нужен строгий contract, эффективный binary protocol, streaming, low-latency communication или единый API contract между несколькими платформами.

Минусы: сложнее дебажить без специальных tools, хуже читаемость payload по сравнению с JSON, нужна генерация кода и аккуратная работа с schema evolution.

**Коротко:** gRPC is a type-safe RPC framework where API methods and messages are defined in proto files and client/server code is generated from that contract.

### Что такое Protocol Buffers?

Protocol Buffers, или protobuf, - language-neutral binary serialization format и IDL для описания структуры сообщений.

В `.proto` файле описываются messages, fields, field numbers, types, enums и services. По этому контракту генерируются Kotlin/Java models и gRPC stubs.

```proto
message User {
  string id = 1;
  string name = 2;
  int32 age = 3;
}
```

Главная идея: в protobuf важны не имена полей, а field numbers. Поэтому при изменении схемы нельзя переиспользовать старые номера полей под другой смысл.

Плюсы protobuf: компактный binary payload, быстрый parsing, строгая схема и code generation. Минусы: payload не человекочитаемый как JSON, а schema evolution требует дисциплины.

**Коротко:** protobuf defines strongly typed messages and serializes them into compact binary data; field numbers are part of the compatibility contract.

### REST vs gRPC

REST обычно строится вокруг resources, URLs и HTTP methods: `GET /users/1`, `POST /orders`. gRPC строится вокруг service methods: `UserService.GetUser`, `OrderService.CreateOrder`.

REST чаще использует JSON, проще дебажится обычными HTTP tools и удобен для public API, browser clients и простых CRUD сценариев.

gRPC обычно эффективнее по payload size и latency, даёт строгий contract, code generation и хорошо поддерживает streaming через HTTP/2.

В Android выбор зависит от backend ecosystem и задачи. Для обычного mobile API часто достаточно REST + Retrofit. gRPC полезен, если проект уже построен вокруг protobuf/gRPC, нужны streaming updates, typed contracts или высокая эффективность network layer.

**Важно:** gRPC не делает архитектуру автоматически лучше. Всё равно нужны repository/data layer, error mapping, timeout/retry policy, cancellation и mapping generated models в domain/UI models.

**Коротко:** REST is resource-oriented and human-readable, gRPC is service-method-oriented, strongly typed and efficient, but requires generated code and tooling.

### Unary / streaming calls

Unary call - самый простой тип gRPC вызова: client отправляет один request и получает один response. Это похоже на обычный HTTP request/response.

Server streaming - client отправляет один request, а server возвращает stream responses. Например, подписка на live status, progress updates или timeline events.

Client streaming - client отправляет stream requests, а server возвращает один response. Например, upload серии chunks или набор событий, после которых server возвращает итог.

Bidirectional streaming - client и server обмениваются streams одновременно. Это похоже на постоянный realtime channel и подходит для chat-like, telemetry или interactive flows.

В Android streaming удобно маппить в `Flow`, но важно учитывать lifecycle-aware collection, cancellation, reconnect strategy и backpressure/буферизацию на уровне выбранной gRPC/Kotlin обёртки.

**Коротко:** gRPC supports unary, server streaming, client streaming and bidirectional streaming calls; streaming is one of its main advantages over typical REST APIs.

### gRPC in Android

В Android gRPC client обычно генерируется из `.proto` contracts. Data layer вызывает generated stubs, а repository маппит protobuf responses в domain/UI models.

Для Kotlin-кода часто используют coroutine-friendly stubs: unary calls выглядят как suspend functions, а streaming calls можно представлять как `Flow`.

Generated protobuf models лучше не протаскивать напрямую в UI / `ViewModel`. Они являются network contract model, а не обязательно удобной domain model.

Error handling отличается от REST: вместо HTTP status codes client часто работает с gRPC status codes, например `OK`, `CANCELLED`, `UNKNOWN`, `INVALID_ARGUMENT`, `NOT_FOUND`, `PERMISSION_DENIED`, `UNAUTHENTICATED`, `UNAVAILABLE`, `DEADLINE_EXCEEDED`.

**Коротко:** on Android, gRPC belongs in the data layer; repositories should hide generated stubs and map protobuf/status errors into app-level models.

### Schema evolution / backward compatibility

Protobuf хорошо поддерживает backward/forward compatibility, если соблюдать правила изменения схемы.

Можно добавлять новые поля с новыми field numbers: старые клиенты их проигнорируют, новые клиенты смогут прочитать, если server их присылает.

Нельзя переиспользовать удалённые field numbers или менять смысл существующего поля. Если поле удалено, его номер и имя лучше пометить как `reserved`.

Менять тип существующего поля опасно, потому что старые и новые клиенты могут начать неправильно читать данные. Для нового смысла лучше добавить новое поле с новым номером.

**Коротко:** protobuf compatibility is based on stable field numbers; add new fields safely, but do not reuse or repurpose old field numbers.
