# Architecture Basics

Modern Android architecture is a pragmatic approach to separating responsibilities between UI, state holders, domain logic and data sources.

## Layers

### Modern Android architecture

Modern Android architecture is usually a layered architecture where the app is split into a UI layer, a data layer and an optional domain layer.

The main idea is separation of concerns: `Activity`, `Fragment` and composable functions should not contain all application logic, and each layer should have clear responsibilities and boundaries.

Modern Android commonly uses `ViewModel` as a state holder, immutable UI state, unidirectional data flow, repositories, Coroutines/Flow and dependency injection.

**In short:** modern Android architecture is usually a pragmatic layered architecture with clear responsibilities: UI renders state, `ViewModel` produces UI state, repositories hide data sources, and domain/use cases are added when they reduce complexity.

### UI layer / domain layer / data layer

The UI layer is responsible for displaying application data and handling user interaction. In Android this usually includes composable functions, `Fragment`, `Activity`, `ViewModel`, UI state, UI events and UI-specific formatting.

The data layer owns application data and business logic related to creating, storing and changing data. It usually includes repositories, remote/local data sources, API services, Room/DataStore/cache, DTO/entity models and mappers.

The domain layer is an optional layer between UI and data. It contains use cases/interactors, business rules, validation and scenario orchestration when logic is complex or reused by several `ViewModel` classes.

Good layer separation means the UI does not know API/database details, the data layer does not depend on Android UI, and business rules are not spread across composable functions or `Activity`.

**In short:** the UI layer shows state and sends user actions, the data layer owns data and repositories, and the domain layer is optional and contains reusable business logic.

### Clean Architecture

Clean Architecture is an approach to separation of concerns where UI, business logic and data access are separated, and dependencies point toward more stable abstractions.

In Android this often looks like UI layer -> `ViewModel` -> use case/domain -> repository -> data sources. But Clean Architecture does not have to mean the same folder structure everywhere or a use case for every tiny action.

Benefits: code is easier to test, business logic is easier to reuse, data sources can be replaced without rewriting UI, and large classes are easier to split.

Trade-off: overly strict Clean Architecture in a simple CRUD/API-to-UI screen can add boilerplate and slow development without real benefit.

**In short:** use Clean Architecture pragmatically: keep clear boundaries and testable business logic, but avoid adding layers that do not solve a real problem.

### When is a domain layer needed?

The domain layer is not always needed. It is useful when there is complex business logic, scenarios are reused by several `ViewModel` classes, several repositories need to be combined, or business rules need to be tested separately from UI and data details.

Typical examples: payment flow, authorization rules, permissions, validation, combining user + subscription + feature flags, complex error mapping, and orchestration of several remote/local sources.

If a screen simply loads a list and displays it, a separate use case for every small operation may be unnecessary. In that case `ViewModel` can call a repository directly if this matches the project conventions and layer boundaries remain clear.

**In short:** the domain layer is optional; add it when it reduces duplication, hides complex business logic, or makes behavior easier to test.

## Data ownership

### Repository pattern

Repository is a facade over data sources that gives the rest of the app a single API for working with data.

Repository hides where data comes from: network, database, cache, DataStore, file or websocket. It can centralize data changes, resolve conflicts between sources, perform mapping and encapsulate caching/offline-first logic.

`ViewModel` or a use case should not depend directly on a Retrofit service, DAO or DataSource if repository is already the entry point into the data layer.

**Important:** a repository should not be a meaningless thin wrapper. It is useful when it actually hides data sources, caching rules, mapping, error handling or orchestration.

**In short:** repository abstracts data sources and exposes a clean API to the rest of the app, so UI/domain code does not know whether data comes from API, database or cache.

### Single source of truth

Single source of truth is a principle where a particular piece of state has one main owner, and the rest of the system reads data from it instead of storing competing copies.

For UI this means the screen should render from one current UI state instead of assembling conflicting values from multiple mutable fields. For data this is often repository/database/cache as the main source from which an observable stream is built.

Single source of truth reduces the risk of desynchronization, race conditions and bugs after recreation/configuration change.

**Important:** do not mutate UI state directly in UI if the data owner is `ViewModel` or the data layer.

**In short:** single source of truth means one clear owner of state; UI observes it and sends events back instead of maintaining competing copies.
