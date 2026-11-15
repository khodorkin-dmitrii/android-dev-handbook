# Crash Reporting and Production Monitoring

Production monitoring should turn a failure into an actionable, privacy-safe incident record. It serves a different purpose from local logging and product analytics.

## Different responsibilities

* **Crash reporting** groups fatal crashes, supported ANRs, and selected non-fatal errors with stack traces.
* **Logging** records diagnostic events locally or in controlled sinks.
* **Analytics** measures product behavior and funnels.
* **Performance monitoring** measures latency, startup, rendering, or network spans.

One platform may cover several of these areas, but collection, sampling, retention, and access policies still need separate decisions.

## Crashlytics, Sentry, and alternatives

Firebase Crashlytics supports Android crashes, recorded non-fatals, custom keys, logs, and ANRs from Android 11 onward. Sentry and similar platforms can combine errors with breadcrumbs, releases, environments, and tracing. Compare the signals and alerting you need, mapping and native-symbol upload, regional storage, privacy controls, cost, and integration with backend monitoring.

Verify a release build end to end: trigger a test crash and a recorded non-fatal, then check that events reach the correct release with readable stacks. Keep the R8 mapping file and native symbols matched to that exact build; unreadable stacks make production triage much harder. ANR coverage varies by platform and reporting mechanism, so compare trends with Android vitals rather than assuming identical counts.

## Useful incident context

Attach a small, bounded set of metadata:

* release version, build number, and commit SHA;
* environment and relevant feature-flag state;
* device/OS, screen or flow, and normalized error category;
* backend correlation ID when it can be safely shared;
* a pseudonymous user/session reference only when necessary and permitted.

Prefer stable categories for filtering; unique IDs are for tracing a specific incident, not grouping. Breadcrumbs should capture meaningful transitions, not every tap. Report unexpected, actionable non-fatals; routine handled errors can overwhelm the signal.

Never send tokens, passwords, payment data, raw request bodies, or unrestricted personal data. Review exception messages and breadcrumbs too, redact before calling the SDK, and configure collection, retention, deletion, and console access for the product's privacy requirements.

## Questions monitoring should answer

* What failed, and which releases and users are affected?
* What state preceded the failure, and can it be reproduced or correlated with backend evidence?
* Did the rate change after a release or feature rollout?

Use a defined denominator and comparable release windows when interpreting crash-free users or sessions; event counts alone do not show impact.

## See also

* [Performance & Memory](../android/performance-memory.md) - ANR fundamentals
* [Logging and Diagnostic Data](logging-diagnostics.md)
* [QA-Friendly Debug Builds](qa-debug-builds.md)
