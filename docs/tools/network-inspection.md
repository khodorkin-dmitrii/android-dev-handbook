# Network Inspection

Network diagnostics should show what failed, how long the request took, and how to find the matching backend trace. Choose the tool based on where the request runs and how much detail you need.

## Choosing an inspection method

| Approach | Best use | Limitation |
|---|---|---|
| OkHttp Logging Interceptor | Quick request/response logs in a controlled build | Can expose URLs, headers, and bodies in Logcat |
| Chucker | On-device request history for developers and QA | Adds an inspector to the app build |
| Android Studio Network Inspector | Live inspection while attached to a debuggable app | Supports `OkHttp` and `HttpsURLConnection` traffic |
| Charles, Proxyman, or another proxy | Traffic routed through a proxy; rewriting or throttling | Needs proxy/TLS setup; certificate pinning may block interception |
| Request/backend correlation | Diagnosing failures across app and server | Needs a shared request or trace ID |

Network Inspector may miss traffic from other clients. A proxy sees only traffic configured to pass through it; it cannot decrypt a pinned TLS connection simply by installing a local certificate.

## Chucker in internal builds

Chucker captures OkHttp requests and responses and provides an on-device history. It helps QA inspect a failure without attaching Android Studio. Include the inspector only in controlled variants; the no-op artifact can keep the same integration in release builds.

Set retention and maximum body size, and redact sensitive headers and content before capture or export. Treat exported traffic as sensitive: it can contain tokens, personal data, and business payloads.

## Record diagnostic metadata

For routine diagnostics, record a bounded summary:

* request or trace ID shared with the backend;
* HTTP method and endpoint template, without sensitive path or query values;
* status code or normalized failure category;
* elapsed time and retry count;
* app version, environment, and relevant connectivity state.

An OkHttp application interceptor can add a request ID and record the outcome once per logical call. If you need DNS, connection, TLS, or per-attempt timings, use an OkHttp `EventListener` or a dedicated trace; a request/response log does not provide that breakdown.

## Limitations and safe defaults

WebSockets, streaming, gRPC/protobuf payloads, and traffic outside the inspected client may need specialized tools. A body viewer also cannot identify server processing time on its own.

Keep routine logs to approved metadata. `HttpLoggingInterceptor.Level.BASIC` omits headers and bodies, but still logs the URL, which may contain sensitive path or query values. Use it only when URLs are safe; enable `BODY` briefly in a controlled build with redaction, and never ship unrestricted body logging.

## See also

* [Retrofit / OkHttp](../networking/retrofit-okhttp.md)
* [HTTP / REST](../networking/http-rest.md)
* [gRPC / Protobuf](../networking/grpc-protobuf.md)
* [Logging and Diagnostic Data](logging-diagnostics.md)
