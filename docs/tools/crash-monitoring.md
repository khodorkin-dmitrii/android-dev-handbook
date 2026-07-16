# Crash Reporting and Production Monitoring

Production monitoring should turn a failure into an actionable, privacy-safe incident record. It is different from local logging and product analytics.

## Different responsibilities

* **Crash reporting** groups fatal crashes, ANRs, and selected non-fatal errors with stack traces.
* **Logging** records diagnostic events locally or in controlled sinks.
* **Analytics** measures product behavior and funnels.
* **Performance monitoring** measures latency, startup, rendering, or network spans.

One platform may offer several capabilities, but their data models, sampling, retention, and access policies should remain explicit.

## Crashlytics, Sentry, and alternatives

Firebase Crashlytics is a common Android option for crashes, non-fatals, ANRs on supported Android versions, custom keys, logs, and release grouping. Sentry and equivalent platforms can combine errors with breadcrumbs, releases, environments, tracing, and wider cross-platform observability.

Choose based on required signals, alerting, symbol/mapping upload, release workflow, regional storage, consent, cost, self-hosting needs, and existing backend observability. Avoid selecting a platform only because another Firebase or monitoring product is already present.

## Useful incident context

Attach bounded, low-cardinality metadata:

* release version, build number, and commit SHA;
* environment and relevant feature-flag values;
* device/OS and app process state;
* screen or flow name;
* normalized error category;
* mobile request ID and backend correlation ID;
* privacy-safe user/session reference when truly necessary.

Breadcrumbs should describe meaningful transitions, not every tap. Non-fatal reporting should be reserved for actionable unexpected failures; reporting every handled error destroys signal quality.

Never send tokens, passwords, payment data, raw request bodies, or unrestricted personal data. Apply consent and deletion requirements, redaction before SDK calls, and role-based console access.

## Questions monitoring should answer

* What failed, and what is the likely root area?
* Which release and environment are affected?
* How many users or sessions are affected?
* What application state preceded the failure?
* Can the scenario be reproduced or correlated with backend evidence?
* Did the issue begin or regress after a particular release?

## See also

* [Performance & Memory](../android/performance-memory.md) - ANR fundamentals
* [Logging and Diagnostic Data](logging-diagnostics.md)
* [QA-Friendly Debug Builds](qa-debug-builds.md)

