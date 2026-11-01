# KMP vs KMM vs Compose Multiplatform

These terms describe different scopes: Kotlin Multiplatform shares Kotlin code; Compose Multiplatform is an optional way to share UI.

| Term | Meaning | Typical use |
| --- | --- | --- |
| KMP | Kotlin Multiplatform | Share selected code across declared targets |
| KMM | Deprecated name for Kotlin Multiplatform Mobile | Older Android–iOS articles and projects |
| Jetpack Compose | Google's Android UI toolkit | Build Android UI |
| Compose Multiplatform | JetBrains' multiplatform UI framework | Share Compose UI across supported targets |

## Kotlin Multiplatform and KMM

KMP is the current name for the technology that compiles shared Kotlin code for multiple targets. KMM was the mobile-focused product name for Android and iOS code sharing; JetBrains deprecated that name in 2023. It is not a separate technology to choose instead of KMP.

Shared code can contain models, networking, business rules, and presentation logic. Platform-specific APIs still need platform code or an abstraction. For the compilation model, see [Kotlin Multiplatform Overview](overview.md).

## Jetpack Compose and Compose Multiplatform

Jetpack Compose is Android's declarative UI toolkit. Compose Multiplatform extends its programming model and APIs to other supported platforms. It is built on KMP, but KMP does not require it. On Android, Compose Multiplatform dependencies use Google's Jetpack Compose artifacts; Android-only APIs are not automatically available in common code.

Check [platform stability](https://kotlinlang.org/docs/multiplatform/supported-platforms.html) for KMP and Compose Multiplatform separately. Support for a Kotlin target does not imply the same Compose UI support or stability. Also check [Compose compatibility and versions](https://kotlinlang.org/docs/multiplatform/compose-compatibility-and-versioning.html) when choosing dependencies.

## Valid combinations

- Share data and domain logic with Jetpack Compose on Android and SwiftUI on iOS.
- Share presentation state while keeping native UI on each platform.
- Share Compose UI across supported targets.
- Share only selected screens and keep the rest native.

Choose based on product requirements, platform UX, team skills, and integration cost. See [Architecture and UI Strategies](architecture-ui.md) for the trade-offs.

## References

- [JetBrains: Kotlin Multiplatform naming update](https://blog.jetbrains.com/kotlin/2023/07/update-on-the-name-of-kotlin-multiplatform/)
- [Compose Multiplatform and Jetpack Compose](https://kotlinlang.org/docs/multiplatform/compose-multiplatform-and-jetpack-compose.html)
- [Kotlin Multiplatform supported platforms and stability](https://kotlinlang.org/docs/multiplatform/supported-platforms.html)
- [Compose Multiplatform compatibility and versions](https://kotlinlang.org/docs/multiplatform/compose-compatibility-and-versioning.html)
