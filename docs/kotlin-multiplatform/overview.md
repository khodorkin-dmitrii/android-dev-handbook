# Kotlin Multiplatform Overview

Kotlin Multiplatform (KMP) lets a project compile shared Kotlin code for several declared targets. The same source is compiled separately for each target into the relevant form, such as JVM bytecode, JavaScript, or a native binary. It is not executed through one universal runtime.

`commonMain` contains code intended for every target of a multiplatform module. It can use common Kotlin APIs and multiplatform libraries, but it cannot directly call an API that is absent from any target, such as Android framework or JDK-only APIs in a module that also targets iOS. Platform integrations belong behind abstractions or in narrower [platform source sets](shared-platform-code.md).

## What can be shared

KMP does not prescribe a sharing percentage or an application architecture. A project may share:

- focused libraries, models, validation, and algorithms;
- networking, serialization, persistence, repositories, and synchronization;
- business rules, use cases, and presentation state;
- selected UI components or complete Compose Multiplatform screens.

Shared UI is optional. Jetpack Compose on Android and SwiftUI on iOS can consume the same shared logic, while another product may share Compose UI as well. See [KMP vs KMM vs Compose Multiplatform](kmp-kmm-compose.md) for the terminology.

## Platform categories

KMP supports several platform families, with different tooling and ecosystem maturity:

- Android and other JVM targets;
- iOS and other Apple targets through Kotlin/Native;
- JVM desktop and server-side applications;
- JavaScript and Wasm for the web;
- native targets including Linux and Windows.

Windows has two distinct approaches. A JVM desktop application can run on Windows and use Compose Multiplatform Desktop. A Windows Native target such as `mingwX64` produces native code and has different APIs, dependencies, and tooling. General Kotlin target support also does not imply the same stability for Compose Multiplatform UI on that target.

## Choosing KMP deliberately

KMP is most useful when platforms share meaningful behavior and the team can own both common code and native integration. The technical boundary may stop at a small core or extend through data, domain, presentation, and UI. That decision should follow product needs, library compatibility, lifecycle and interoperability costs, not a maximum shared-code metric.

Continue with [Project Structure and Source Sets](project-structure.md) for the build model, [Shared vs Platform-Specific Code](shared-platform-code.md) for boundary choices, and [KMP Adoption and Trade-offs](adoption-tradeoffs.md) for the decision framework.

## References

- [Kotlin Multiplatform documentation](https://kotlinlang.org/docs/multiplatform/)
- [Stability of supported platforms](https://kotlinlang.org/docs/multiplatform/supported-platforms.html)
