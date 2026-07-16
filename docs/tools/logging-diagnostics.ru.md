# Logging and Diagnostic Data

Логи полезны только тогда, когда понятны их назначение, аудитория, срок хранения и privacy boundary.

## Разные виды сигналов

* **Development logs** - временные детали для разработчика, обычно остающиеся в Logcat.
* **Diagnostic logs** - структурированные данные для воспроизведения дефекта, которые можно экспортировать с согласия пользователя.
* **Crash breadcrumbs** - важные действия перед crash или ANR.
* **Analytics events** - измерение поведения продукта, а не подробный debug transcript.
* **Audit/security logs** - security-relevant действия с более строгими правилами integrity и retention.

Не отправляй один поток во все destinations. Поля и retention, допустимые для local debugging, могут быть неприемлемы для analytics или production monitoring.

## Timber или собственная абстракция

Timber остается зрелым lightweight facade над Android logging. Он удобен для call sites, tags и подключаемых trees, но не обязателен и сам по себе не определяет полную модель structured diagnostics.

Продуктам с categories, structured fields, file export, correlation IDs, redaction, несколькими sinks или privacy controls часто полезна собственная boundary:

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

`LogcatSink`, bounded file sink и crash-monitoring sink могут иметь разные filters. Business code зависит только от `AppLogger`.

## Чувствительные данные

По умолчанию нельзя логировать tokens, passwords, payment data, полные request/response bodies, precise location или personal data. Предпочтительны allowlisted fields, необратимые ссылки на account, когда они оправданы, ограниченный retention и redaction до попадания данных в любой sink.

Debug build не становится безопасным автоматически. На QA devices могут использоваться production-like accounts, exported reports могут покинуть устройство, а debug logging случайно остаться активным в release configuration.

**Практическое правило:** решай, допустимо ли поле, при создании event, а затем повторно применяй централизованный redaction на output boundary.

## См. также

* [Crash Reporting and Production Monitoring](crash-monitoring.md)
* [QA-Friendly Debug Builds](qa-debug-builds.md)
* [Network Inspection](network-inspection.md)

