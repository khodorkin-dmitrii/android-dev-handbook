# Architecture and UI Strategies

KMP does not require a specific architecture. It can support MVVM, unidirectional data flow (UDF), MVI-like immutable state, feature-based modules, or selectively applied Clean Architecture. The architecture should reflect product complexity rather than the technology used to compile shared code.

```text
Platform or shared UI
        ↓ UserAction
Shared state holder / ViewModel
        ↓
Use cases or repositories
        ↓
Local and remote data sources
        ↓
StateFlow<UiState>
```

UDF with immutable `UiState`, actions, and `StateFlow` can live inside MVVM. Those choices do not automatically make an architecture MVI.

## Presentation choices

1. **Platform ViewModels and UI.** Data and domain are shared; Android and iOS follow their native state, lifecycle, and navigation conventions.
2. **Shared plain Kotlin state holder with native UI.** Behavior and state are common, while each platform explicitly owns creation, cancellation, and state collection.
3. **Shared AndroidX ViewModel with platform integration.** AndroidX ViewModel supports KMP and can be used from `commonMain`, but lifecycle integration differs. Android components provide standard owners; SwiftUI has no automatic equivalent and needs a `ViewModelStoreOwner`-style bridge and explicit cleanup.
4. **Shared ViewModel and Compose Multiplatform UI.** Presentation and rendering can move together when supported targets and product UX align.
5. **Hybrid per feature.** Each feature shares only what produces value.

A plain state holder can be simpler than exporting AndroidX ViewModel when Android lifecycle semantics are not needed. Hilt is unavailable in `commonMain`, so `@HiltViewModel` cannot wire a shared ViewModel. Use constructor injection and platform composition roots or a compatible multiplatform DI solution.

## Navigation as a boundary

With native UI, each platform can own its navigation stack while shared logic emits navigation results, destinations, or effects. Shared Compose UI can also share more navigation implementation. Neither choice is mandatory: lifecycle, deep links, system back behavior, and platform presentation conventions still need deliberate integration.

## Native, shared, and hybrid UI

| Approach | Strengths | Main costs |
| --- | --- | --- |
| Native UI | Platform UX, accessibility conventions, direct integrations | Duplicate rendering and some presentation work |
| Shared Compose UI | Product parity, one UI implementation, coordinated releases | Cross-platform skills, integration and target-support constraints |
| Hybrid UI | Reuse where valuable, native exceptions where needed | More explicit boundaries and two integration patterns |

Choose using product parity, platform-specific UX, team ownership, release cadence, available skills, maintenance cost, accessibility, and system integrations. Maximum UI reuse is not a universal goal.

See [Shared vs Platform-Specific Code](shared-platform-code.md), [MV Patterns](../architecture/mv-patterns.md), [UI State](../architecture/ui-state.md), [StateFlow & SharedFlow](../coroutines-flow/stateflow-sharedflow.md), and [Dependency Injection](../di/index.md).

## References

- [AndroidX ViewModel for KMP](https://developer.android.com/kotlin/multiplatform/viewmodel)
- [Android KMP guidance](https://developer.android.com/kotlin/multiplatform)
