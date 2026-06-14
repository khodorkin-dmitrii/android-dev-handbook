# Legacy & Refactoring

Legacy and refactoring in Android require care: existing behavior should be preserved, boundaries should be improved gradually, and migration should not turn into a large risky rewrite.

## Legacy

### Legacy code in an Android project

Legacy code is not necessarily bad code. Usually it is code that has lived in the project for a long time and was written for old requirements, old architectural decisions, outdated libraries or before the current team conventions existed.

In Android, legacy often looks like massive `Activity` / `Fragment`, XML + callbacks, RxJava chains, manual DI/service locator, static singletons, complex inheritance hierarchies, old navigation approaches or mixing UI, business logic and data access in one class.

Working with legacy code requires caution: first understand the current behavior, cover critical scenarios with tests or at least characterization tests, and only then change the structure.

The main principle is not to rewrite everything for a "beautiful architecture", but to reduce risk and gradually improve boundaries: move data access into repository, business logic into use case/domain, UI state into `ViewModel`, and make side effects explicit.

**In short:** legacy code is code with existing behavior and constraints; refactor it incrementally, first protecting behavior with tests or checks, then improving boundaries and reducing coupling.

### Incremental refactoring

Incremental refactoring is improving code gradually through small safe steps without a large big bang rewrite.

In Android this is especially important because a feature can be connected to lifecycle, navigation, analytics, caching, push/deep links, permissions and different OS versions. A large rewrite can easily break hidden scenarios.

A practical process: find a pain point, capture current behavior, add tests or a manual checklist, create small seams, then move logic piece by piece.

Examples of small steps: move a network call from `Activity` into repository, replace a callback with a suspend function/Flow, introduce `UiState`, separate a mapper, add an interface for a legacy dependency, cover `ViewModel` with tests, gradually remove duplication.

Keep public contracts stable and migrate call sites gradually. If an API needs to change, it is better to add a new path first, move clients to it, and then remove the old one.

**In short:** incremental refactoring reduces risk by changing one boundary at a time, keeping behavior stable and continuously verifying the result.

## Migration

### Migration from XML/RxJava to Compose/Flow

Migration from XML/RxJava to Compose/Flow should usually be gradual because in a real Android project UI, navigation, lifecycle, DI, analytics and the data layer are often tightly connected.

For UI, interoperability can help: add Compose through `ComposeView` inside XML/Fragment or, conversely, embed `AndroidView` / `ViewBinding` in Compose if an old `View` needs to be reused temporarily.

For state management, it is useful to move the screen to `ViewModel` + `UiState` first, and only then change the rendering layer. If `ViewModel` exposes a stable `StateFlow<UiState>`, UI can be replaced from XML to Compose with less risk.

For RxJava migration, avoid mechanically replacing operators. Understand the semantics: cold/hot streams, backpressure, schedulers, error handling, cancellation/disposal and lifecycle. Rx `Observable` / `Single` / `Completable` can be gradually adapted to suspend functions or `Flow` at layer boundaries.

A practical path: first isolate Rx inside repository/data layer, expose suspend/Flow APIs for new code, then gradually rewrite the internal implementation. For UI collection, use lifecycle-aware APIs: `collectAsStateWithLifecycle()` in Compose and `repeatOnLifecycle()` in the View System.

**Important:** do not change the UI framework, reactive stack and business logic at the same time without clear behavior checks. It is better to separate migration steps and keep changes rollback-friendly.

**In short:** prefer migration in layers: first stabilize state contracts, then bridge old and new UI/reactive APIs, and only then replace implementations gradually.
