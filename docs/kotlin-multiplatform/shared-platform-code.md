# Shared vs Platform-Specific Code

KMP provides several valid sharing boundaries. They are options, not a maturity ladder; a hybrid product is not a failed attempt at full sharing.

| Strategy | Shared | Platform-specific | Typical use |
| --- | --- | --- | --- |
| Shared core | Models, formatting, algorithms | Most application code | Libraries, experiments, first KMP adoption |
| Shared data | API, serialization, database logic, repositories | Presentation and UI | Incremental adoption |
| Shared data + domain | Data, repositories, business rules, use cases | ViewModels and UI | Independent native presentation teams |
| Shared presentation | Data, domain, state holders, UI state | Native UI and navigation | Consistent behavior with native UI |
| Shared UI | Most application code and Compose UI | Entry points and integrations | Small cross-platform teams and aligned products |
| Hybrid | Selected features, layers, or UI components | Everything else | Mature products with different platform needs |

## Boundary by responsibility

### Data sources and repositories

HTTP behavior, serialization, DTOs, SQL queries, cache policy, pagination, retry, and synchronization are often good shared candidates. Database drivers or factories, filesystem paths, secure storage, connectivity observation, background work, and push notifications commonly need platform adapters. The exact boundary depends on library target support and product requirements.

Repositories are especially valuable to share when they define a single source of truth, coordinate remote and local data, apply offline-first and freshness policies, and map DTO, database, and domain models. This keeps business behavior consistent rather than merely reusing transport code.

### Domain and presentation

Domain models, validation, filtering, sorting, and real business rules are usually portable. Use cases should represent meaningful operations or orchestration, not wrap every repository method to imitate a layer diagram.

Presentation can share immutable `UiState`, actions, state holders or ViewModels, and loading, error, offline, retry, and recovery behavior exposed through `StateFlow`. Difficult boundaries remain: lifecycle ownership, saved state, navigation, permissions, SwiftUI and Compose conventions, and Kotlin/Swift interoperability.

UI may remain Jetpack Compose plus SwiftUI, use shared Compose Multiplatform screens, share only selected components, or share Android/Desktop Compose UI while iOS remains SwiftUI.

## Interfaces and `expect`/`actual`

Prefer interfaces and injected implementations for behavior and replaceable dependencies such as storage, connectivity, clocks, analytics, external links, and other platform services:

```kotlin
interface ExternalLinks {
    fun open(url: String)
}

class HelpPresenter(private val links: ExternalLinks) {
    fun openHelp() = links.open("https://example.com/help")
}
```

Use `expect`/`actual` as a narrow bridge when an API has the same conceptual shape but needs target-specific implementation:

```kotlin
// commonMain
expect fun platformName(): String

// androidMain
actual fun platformName(): String = "Android"
```

Expected and actual classes are currently Beta; functions and properties can still be useful narrow bridges. Interfaces remain easier to fake, replace, or provide multiple times on one platform.

**Practical heuristic:** prefer interfaces for behavior and dependencies. Use `expect`/`actual` as a narrow bridge to platform APIs rather than as a replacement for architectural abstractions.

See [Project Structure and Source Sets](project-structure.md) for placement and [Architecture and UI Strategies](architecture-ui.md) for application-level choices.

## References

- [Expected and actual declarations](https://kotlinlang.org/docs/multiplatform/multiplatform-expect-actual.html)
