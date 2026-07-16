# Tools Overview

Android tooling is most useful when it starts from an engineering question: what evidence is missing, who needs it, and where can it be collected safely? A library name is not a strategy.

Stable categories include application development, local debugging, automated testing, network and memory diagnostics, UI/performance analysis, production monitoring, and QA investigation support. The same tool can contribute to several categories, but its operating boundary should stay clear.

## Tooling by problem

| Problem | Tool or approach | Where it runs | Status | Main limitation |
|---|---|---|---|---|
| Retained objects | LeakCanary | Debug app/device | Recommended diagnostic option | Detects retention, not recomposition cost |
| Heap and allocations | Android Studio Memory Profiler | IDE and device | Standard platform tool | Manual, scenario-dependent analysis |
| On-device HTTP inspection | Chucker | Debug/internal app | Useful for developers and QA | Can expose sensitive payloads |
| HTTP log output | OkHttp Logging Interceptor | App/Logcat | Useful when narrowly configured | Body logging is risky and noisy |
| Live supported-client traffic | Network Inspector | Android Studio | Standard local tool | Primarily supports OkHttp and `HttpsURLConnection` |
| Lightweight logging facade | Timber | App | Mature optional choice | Not a structured logging system by itself |
| Structured diagnostics | Application-owned logger | App and configured sinks | Recommended for complex products | Requires design and maintenance |
| System-wide timing | Perfetto / System Trace | Device and desktop | Standard deep profiling tool | Trace interpretation has a learning curve |
| CPU, memory, and jank investigation | Android Studio Profiler | IDE and device | Standard local tool | Profiling overhead and uncontrolled scenarios |
| Repeatable user journeys | Macrobenchmark | Benchmark device/CI | Recommended measurement tool | Requires controlled setup and stable scenarios |
| Ahead-of-time optimization hints | Baseline Profiles | Build and installed app | Recommended for critical journeys | Optimization, not diagnosis or measurement |
| Crash and ANR reports | Firebase Crashlytics | Production monitoring | Common production option | Vendor, consent, and privacy decisions |
| Broader error observability | Sentry or equivalent | Production monitoring | Valid alternative | Cost, data governance, and integration scope |
| Internal diagnostics | Beagle or custom debug menu | Debug/internal app | Evaluate per project | Library UI and architecture may not fit the app |
| Historical debug drawer | Hyperion | Debug app | Legacy/reference | View-era design and no Compose-aware inspection |

Other categories include automated tests, Layout Inspector, Database Inspector, Background Task Inspector, Play Console Android vitals, and backend tracing. No single tool covers local debugging, reproducible measurement, and production monitoring equally well.

## Selection criteria

Evaluate a tool by:

* the problem and required evidence;
* debug-only versus production runtime cost;
* data sensitivity, redaction, retention, and access control;
* compatibility with the actual network/UI/build architecture;
* usefulness to QA without Android Studio;
* maintenance status and upgrade cost;
* export format and correlation with backend or release data;
* product scale and incident-response workflow.

A small application may need Logcat, Profiler, and crash reporting. A larger product may also need an internal diagnostic surface, structured logs, request correlation, repeatable benchmarks, and controlled exports.

**Key idea:** choose the smallest set that makes important failures observable and reproducible. Do not ship debug inspection or sensitive data collection merely because a library supports it.

## Section structure

* [In-App Debug Menus](in-app-debug-menus.md)
* [Logging and Diagnostic Data](logging-diagnostics.md)
* [Network Inspection](network-inspection.md)
* [Memory Leak Detection](memory-leaks.md)
* [Performance Profiling and Benchmarking](performance-profiling.md)
* [Crash Reporting and Production Monitoring](crash-monitoring.md)
* [QA-Friendly Debug Builds](qa-debug-builds.md)

## See also

* [Testing Strategy](../testing/strategy.md)
* [Performance & Memory](../android/performance-memory.md)
* [Background Work & System Behavior](../android/background-work-system-behavior.md)
