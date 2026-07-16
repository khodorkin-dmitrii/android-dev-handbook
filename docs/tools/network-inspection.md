# Network Inspection

Network diagnostics should answer what happened, how long it took, and how the mobile request maps to backend evidence. Dumping raw bodies is neither sufficient nor always safe.

## Choosing an inspection method

| Approach | Best use | Main trade-off |
|---|---|---|
| OkHttp Logging Interceptor | Quick developer logs and headers/timing | Logcat noise and payload exposure |
| Chucker | On-device request history for developers and QA | Code/runtime surface in the app |
| Android Studio Network Inspector | Live local inspection without custom UI | Requires IDE attachment and supported clients |
| Charles, Proxyman, or another proxy | Cross-app traffic, rewriting, throttling | Certificate setup and pinning restrictions |
| Request/backend correlation | Distributed incident diagnosis | Requires mobile and backend cooperation |

Android Studio Network Inspector supports OkHttp and `HttpsURLConnection`; traffic from other stacks may not be decoded. A proxy sees traffic routed through it, but TLS certificate pinning can intentionally prevent interception.

## Chucker in internal builds

Chucker records OkHttp requests and responses and provides an on-device UI, notifications, search, and sharing. This makes it useful when QA cannot attach an IDE. Use its debug artifact only in controlled variants; a no-op release artifact can preserve the shared API when necessary.

Configure retention, maximum body size, and redaction. Exported traffic may contain credentials, personal data, or business-sensitive payloads, so sharing must be deliberate and access-controlled.

## Record diagnostic metadata

Useful fields include:

* request ID and backend correlation ID;
* method/endpoint template, not a sensitive full URL;
* status code and normalized error category;
* duration, retry count, and connectivity state;
* app version, environment, and selected API host.

An application interceptor can attach a generated request ID and record a bounded summary. Keep authentication headers and bodies out of generic logs.

## Limitations

Inspection depends on protocol and client architecture. WebSockets, streaming, encrypted custom protocols, gRPC/protobuf payloads, and traffic outside the inspected OkHttp client need specialized tooling. A human-readable body viewer does not explain HTTP/2 framing, retry policy, DNS/TLS latency, or backend processing time.

Use `BASIC` or metadata-oriented logging by default. Enable full bodies only for a specific controlled investigation and redact before display or export.

## See also

* [Retrofit / OkHttp](../networking/retrofit-okhttp.md)
* [HTTP / REST](../networking/http-rest.md)
* [gRPC / Protobuf](../networking/grpc-protobuf.md)
* [Logging and Diagnostic Data](logging-diagnostics.md)

