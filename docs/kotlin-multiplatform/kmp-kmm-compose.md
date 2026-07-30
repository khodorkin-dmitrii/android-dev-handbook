# KMP vs KMM vs Compose Multiplatform

The terms describe related but different scopes. Kotlin Multiplatform is the code-sharing technology; Compose frameworks concern UI.

| Term | Meaning | What may be shared |
| --- | --- | --- |
| KMP | Multiplatform Kotlin technology | Logic, data, presentation, UI, or selected components |
| KMM | Former mobile-focused name | Historically Android and iOS shared code |
| Jetpack Compose | Android UI toolkit | Android UI |
| Compose Multiplatform | Multiplatform Compose UI framework | UI across its supported targets |

## Kotlin Multiplatform and KMM

Kotlin Multiplatform, or KMP, is the current umbrella name for sharing Kotlin code across declared targets. Kotlin Multiplatform Mobile, or KMM, was the former mobile-focused name. It may still appear in older articles, repositories, and tool names, but it is not a separate modern alternative to KMP.

For the underlying compilation model, see [Kotlin Multiplatform Overview](overview.md).

## Jetpack Compose and Compose Multiplatform

Jetpack Compose is Android's declarative UI toolkit. Compose Multiplatform extends the Compose programming model and APIs to supported non-Android platforms. It is a UI framework built on top of the wider multiplatform ecosystem, not another name for KMP.

Kotlin target support and Compose Multiplatform UI support must be evaluated separately. A target may be supported by Kotlin while Compose UI for that platform has a different stability level or is unavailable. Current stability is documented per platform rather than implied by the word "multiplatform."

## Valid combinations

Using KMP does not require Compose Multiplatform:

- shared KMP data and domain logic with Jetpack Compose on Android and SwiftUI on iOS;
- shared presentation state with native UI on each platform;
- shared Compose UI across supported targets;
- a hybrid where some screens are shared and others remain native.

The right combination depends on product parity, platform UX, team ownership, and integration cost. See [Architecture and UI Strategies](architecture-ui.md) for those choices.

## References

- [Kotlin Multiplatform supported platforms and stability](https://kotlinlang.org/docs/multiplatform/supported-platforms.html)
- [Compose Multiplatform compatibility and versions](https://kotlinlang.org/docs/multiplatform/compose-compatibility-and-versioning.html)
