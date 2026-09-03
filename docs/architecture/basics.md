# Architecture Basics

Modern Android architecture separates UI, state management, business rules and data access so that each part has a clear responsibility and can evolve independently.

## Layers

### Modern Android architecture

A typical Android app has a UI layer, a data layer and, when useful, a domain layer. This is a practical application of separation of concerns, not a requirement to create the same folders and classes in every feature.

The UI observes immutable state and sends user actions back to a state holder, usually a `ViewModel`. The state holder coordinates work through repositories or use cases and exposes the result as UI state. This creates unidirectional data flow:

```text
UI events -> state holder -> domain/data layer
UI state  <- state holder <- domain/data layer
```

`Activity`, `Fragment` and composable functions should focus on rendering and platform/UI interaction. They should not contain data-access details or business rules that belong to longer-lived, independently testable components.

### UI layer / data layer / domain layer

The **UI layer** displays application data and handles user interaction. It includes composable functions or Views, Android UI components, screen-level state holders, UI models and UI-specific formatting.

The **data layer** exposes application data through repositories. It coordinates remote and local data sources such as API services, Room, DataStore, files and caches, and owns rules for reading, updating, mapping and synchronizing that data. UI code should not depend directly on Retrofit services, DAOs or concrete data sources.

The **domain layer** is optional. It contains use cases or interactors when business logic is complex, reused by multiple state holders, or combines several repositories. A simple screen may let its `ViewModel` call a repository directly without violating the architecture.

Layer boundaries should make dependency ownership clear: UI depends on domain or data APIs, while the data layer must not depend on Android UI.

### Clean Architecture

Clean Architecture keeps business rules independent from UI frameworks and implementation details. Its dependency rule points source-code dependencies toward stable policies or abstractions. A diagram such as `UI -> ViewModel -> use case -> repository -> data source` usually describes calls and data flow; it does not by itself define the direction of every compile-time dependency.

On Android, apply this pragmatically. Introduce interfaces where implementations vary, tests benefit from substitution, or modules need isolation. Avoid a use case, mapper and interface for every trivial operation. Clearer ownership and testability should justify the additional indirection.

### When is a domain layer needed?

Add a domain layer when it simplifies the feature, for example when:

- business rules are substantial and should be tested independently;
- the same operation is reused by several `ViewModel` classes;
- one scenario combines multiple repositories;
- validation, authorization or error mapping is more than UI-specific formatting;
- a workflow coordinates several steps or data sources.

Payments, checkout and subscription eligibility are common examples. Loading a list from one repository usually does not require a dedicated use case.

## Data ownership

### Repository pattern

A repository is the public entry point to a part of the data layer. It hides whether data comes from the network, database, cache, DataStore, a file or a websocket, and exposes operations that make sense to the rest of the app.

A repository can coordinate sources, map models, enforce caching rules and implement offline-first behavior. It should not become an unrelated collection of all business logic. Even a small repository is useful when it establishes a clear data boundary; extra wrappers inside it should still earn their complexity.

### Single source of truth

Single source of truth means that each type of application data has one authoritative owner. Other components observe or request changes through that owner instead of maintaining competing mutable copies.

For an offline-first feature, a local database is often the source of truth: network responses update it, and UI observes it through the repository. In a simpler feature, the source may be a backend or repository-managed in-memory state. The choice depends on persistence, offline and consistency requirements.

UI state has the same ownership principle. A screen should render from one state holder instead of combining unrelated mutable fields in the UI. User actions go back to the owner, which updates the state. This reduces desynchronization, race conditions and bugs after recreation.

## Related topics

- [UI State Architecture](ui-state.md)
- [MV* Patterns](mv-patterns.md)
- [Multi-module Architecture](multi-module.md)
