# Logging and Diagnostic Data

Logs are useful only when their purpose, audience, lifetime, and privacy boundary are clear.

## Different signals

* **Development logs** are temporary details for a developer and usually stay in Logcat.
* **Diagnostic logs** are structured evidence for reproducing a defect and may be exported with consent.
* **Crash breadcrumbs** describe important actions leading to a crash or ANR.
* **Analytics events** measure product behavior and are not a debugging transcript.
* **Audit/security logs** record security-relevant actions under stricter integrity and retention rules.

Do not send one stream to every destination. The fields and retention appropriate for local debugging may be unacceptable for analytics or production monitoring.

## Timber or an application-owned abstraction

Timber remains a mature lightweight facade over Android logging. It is useful for call-site convenience, tags, and pluggable trees, but it is optional and does not define a complete structured diagnostic model.

Products that need categories, structured fields, file export, correlation IDs, redaction, multiple sinks, or privacy controls often benefit from an application-owned boundary:

```kotlin
interface AppLogger {
    fun log(
        level: LogLevel,
        category: String,
        message: String,
        fields: Map<String, String> = emptyMap(),
        error: Throwable? = null,
    )
}

class DiagnosticLogger(
    private val sinks: List<LogSink>,
    private val redactor: LogRedactor,
) : AppLogger {
    override fun log(
        level: LogLevel,
        category: String,
        message: String,
        fields: Map<String, String>,
        error: Throwable?,
    ) {
        val event = redactor.redact(LogEvent(level, category, message, fields, error))
        sinks.forEach { it.write(event) }
    }
}
```

`LogcatSink`, a bounded file sink, and a crash-monitoring sink can have different filters. Business code depends only on `AppLogger`.

## Sensitive data

Never log tokens, passwords, payment data, unrestricted request/response bodies, precise location, or personal data by default. Prefer allowlisted fields, irreversible account references where justified, bounded retention, and redaction before data reaches any sink.

Debug builds are not automatically safe. QA devices can contain production-like accounts, exported reports can leave the device, and a debug log call can accidentally remain active in release configuration.

**Practical rule:** decide whether a field is allowed at event creation, then apply central redaction again at the output boundary.

## See also

* [Crash Reporting and Production Monitoring](crash-monitoring.md)
* [QA-Friendly Debug Builds](qa-debug-builds.md)
* [Network Inspection](network-inspection.md)

