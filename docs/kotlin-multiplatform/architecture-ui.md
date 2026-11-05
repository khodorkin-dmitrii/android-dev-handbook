# Architecture and UI Strategies

KMP does not require a specific architecture. It can support MVVM, unidirectional data flow (UDF), MVI-like immutable state, feature-based modules, or selectively applied Clean Architecture. Choose boundaries based on product complexity and platform needs.

```text
UI ── UserAction ──> State holder / ViewModel ──> Repositories ──> Data sources
UI <── StateFlow<UiState> ── State holder <── results ──────── Repositories
```

This is a conceptual flow: the state holder owns and exposes `StateFlow<UiState>`; the UI collects it. UDF with immutable `UiState` and actions can live inside MVVM. These choices do not automatically make an architecture MVI.

## Presentation choices

1. **Platform ViewModels and UI.** Data and domain are shared; Android and iOS follow native state, lifecycle, and navigation conventions.
2. **Shared plain Kotlin state holder with native UI.** Behavior and state are common; each platform owns creation, cancellation, and state observation. Define who cancels work when the screen disappears.
3. **Shared AndroidX ViewModel with platform integration.** AndroidX ViewModel can be used in `commonMain`. Android provides standard owners; SwiftUI needs an explicit `ViewModelStoreOwner` integration and cleanup. Observing Kotlin `Flow` in SwiftUI also needs an interop strategy.
4. **Shared ViewModel and Compose Multiplatform UI.** Presentation and rendering can move together when target support and product UX align.
5. **Hybrid per feature.** Each feature shares only what produces value.

A plain state holder can be simpler when AndroidX ViewModel ownership is unnecessary. Hilt cannot annotate a shared `commonMain` ViewModel with `@HiltViewModel`; use constructor injection with platform composition roots or a compatible multiplatform DI solution.

## Navigation as a boundary

With native UI, each platform can own its navigation stack while shared logic communicates navigation intents or results through an explicit contract. Decide which layer consumes one-time actions and how it handles repeated collection. Shared Compose UI can share more navigation implementation, but deep links, system back behavior, lifecycle, and platform presentation still need integration.

## Native, shared, and hybrid UI

| Approach | Strengths | Main costs |
| --- | --- | --- |
| Native UI | Platform UX, accessibility conventions, direct integrations | Duplicate rendering and some presentation work |
| Shared Compose UI | Product parity, one UI implementation, coordinated releases | Cross-platform skills, integration and target-support constraints |
| Hybrid UI | Reuse where valuable, native exceptions where needed | Explicit boundaries and two integration patterns |

Choose using product parity, platform-specific UX, team ownership, release cadence, skills, maintenance cost, accessibility, and system integrations. Maximum UI reuse is not a universal goal.

See [Shared vs Platform-Specific Code](shared-platform-code.md), [MV Patterns](../architecture/mv-patterns.md), [UI State](../architecture/ui-state.md), [StateFlow & SharedFlow](../coroutines-flow/stateflow-sharedflow.md), and [Dependency Injection](../di/index.md).

## References

- [AndroidX ViewModel for KMP](https://developer.android.com/kotlin/multiplatform/viewmodel)
- [Android KMP guidance](https://developer.android.com/kotlin/multiplatform)
