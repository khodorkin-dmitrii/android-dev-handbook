# Shared vs Platform-Specific Code

KMP allows different sharing boundaries. Choose the boundary that removes useful duplication without forcing platform-specific behavior into common code.

| Strategy | Shared | Platform-specific | Typical use |
| --- | --- | --- | --- |
| Shared core | Models, formatting, algorithms | Most application code | Libraries or first KMP adoption |
| Shared data | API, serialization, persistence logic, repositories | Presentation and UI | Incremental adoption |
| Shared data + domain | Data, repositories, business rules, use cases | ViewModels and UI | Separate native presentation teams |
| Shared presentation | Data, domain, UI state and state holders | Native UI and navigation | Consistent behavior with native UI |
| Shared UI | Shared logic and Compose UI | Entry points and platform integrations | Similar products across platforms |
| Hybrid | Selected features, layers, or UI components | Everything else | Different needs across platforms |

## Boundary by responsibility

### Data sources and repositories

HTTP behavior, serialization, DTOs, SQL queries, cache policy, pagination, retry, and synchronization can often be shared. Database setup, filesystem paths, secure storage, connectivity observation, background work, and push notifications may need platform implementations. Check library support for every target before placing an API in common code.

Sharing repositories is useful when they coordinate local and remote data, define the source of truth *within each app*, and apply the same offline and freshness rules. Sharing repository code does not make Android and iOS installations share one database or cache.

### Domain and presentation

Domain models, validation, filtering, sorting, and business rules are often portable. Add a use case when it represents a meaningful operation or orchestration, not just to wrap every repository method.

Presentation may share `UiState`, actions, state holders or ViewModels, and loading, error, offline, and retry behavior through `StateFlow`. Decide separately who owns lifecycle, saved state, navigation, and permissions on each platform. Also account for Kotlin/Swift interoperability when native iOS UI consumes shared state.

UI can remain Jetpack Compose plus SwiftUI, use Compose Multiplatform for selected screens, or share Android/Desktop Compose UI while iOS stays native. See [Architecture and UI Strategies](architecture-ui.md).

## Interfaces and `expect`/`actual`

Use an interface with injected implementations for replaceable behavior such as opening links, storage, connectivity, and analytics:

```kotlin
// commonMain
interface ExternalLinks {
    fun open(url: String)
}

class HelpPresenter(private val links: ExternalLinks) {
    fun openHelp() = links.open("https://example.com/help")
}
```

Use `expect`/`actual` for a small platform bridge with the same API on each target:

```kotlin
// commonMain
expect fun platformName(): String

// androidMain
actual fun platformName(): String = "Android"

// iosMain (covers the declared iOS device and simulator targets)
actual fun platformName(): String = "iOS"
```

The compiler requires a matching `actual` declaration for every target; an intermediate source set such as `iosMain` can provide one for several targets. Expected and actual classes are still Beta, so functions or properties are often a smaller bridge. Interfaces are easier to fake and to replace with multiple implementations on one platform.

See [Project Structure and Source Sets](project-structure.md) for placement and [KMP Adoption and Trade-offs](adoption-tradeoffs.md) for choosing the scope of sharing.

## References

- [Use platform-specific APIs](https://kotlinlang.org/docs/multiplatform/multiplatform-connect-to-apis.html)
- [Expected and actual declarations](https://kotlinlang.org/docs/multiplatform/multiplatform-expect-actual.html)
