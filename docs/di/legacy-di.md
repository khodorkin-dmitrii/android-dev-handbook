# Legacy DI

Legacy DI approaches still appear in Android projects, especially near MVP, Moxy, RxJava and older multi-module architecture.

## Legacy frameworks

### Dagger vs Toothpick

Dagger and Toothpick are both DI frameworks, but they differ in graph validation timing and runtime model.

Dagger builds the dependency graph at compile time, generates code and provides compile-time validation. If a binding is missing, a scope is incompatible or the graph cannot be built, the error usually appears during project build.

Toothpick was historically a runtime DI framework: it was easier to introduce into Android legacy code, provided scopes and less compile-time boilerplate, but some errors were discovered only at runtime.

Practical trade-off: Dagger/Hilt is usually faster and safer for large production projects because the graph is validated ahead of time and there is no reflection-heavy runtime lookup. Toothpick could be convenient in legacy projects with MVP/Moxy and custom scopes, but it requires discipline and good tests to avoid catching DI errors too late.

Modern Android usually chooses Hilt on top of Dagger. If a project already uses Toothpick, it is usually not replaced mechanically: first isolate composition root, interfaces and scopes, then migrate feature by feature.

**In short:** Dagger gives generated code and compile-time graph validation, while Toothpick is more runtime-oriented and simpler for some legacy setups, but with later error detection.

### Moxy dependencies / legacy patterns

Moxy is a legacy Android MVP framework that helped separate Presenter from `Activity` / `Fragment` and survive configuration changes through generated delegate/proxy code.

In older Android projects, Moxy often appears together with MVP, Cicerone/RxJava and Dagger/Toothpick. View was usually described by an interface, Presenter held presentation logic, and `Activity` / `Fragment` implemented the View interface and called attach/detach through lifecycle.

The main risk of Moxy/MVP legacy is lifecycle coupling: Presenter can hold a reference to View, callbacks can arrive after screen destruction, and dependencies are often hidden in base classes, custom scopes or service locator-like helpers.

When maintaining this code, do not break the lifecycle contract: first understand who creates Presenter, where injection happens, how View attach/detach is connected to `Fragment` / `Activity` lifecycle and where subscriptions/disposables are stored.

When migrating to modern Android, avoid rewriting everything at once. A practical path is to extract the repository/use case layer, stabilize the UI contract, replace Presenter with `ViewModel` where the feature is ready for migration, and gradually move to `StateFlow` / `UiState`.

**In short:** Moxy is a legacy MVP framework; when refactoring it, first protect lifecycle behavior and then migrate presentation logic toward `ViewModel` and state-driven UI gradually.
