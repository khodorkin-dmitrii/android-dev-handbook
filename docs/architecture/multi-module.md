# Multi-module Architecture

Multi-module architecture helps split a large Android project into Gradle modules with clear boundaries, dependencies and responsibilities.

## Modules

### What is a multi-module project?

A multi-module project is an Android/Gradle project split into several modules instead of one large app module.

Modules can be feature modules, core/library modules, data, domain, design system, testing utilities or platform-specific wrappers. Each module has its own `build.gradle`, dependencies and public API.

Why it is useful: faster incremental builds, lower coupling, clearer ownership between teams, code reuse, easier testing and hiding internal implementation details.

Trade-off: multi-module architecture adds complexity to Gradle configuration, dependency graph, navigation, DI setup and version management. A small project may not need it.

**In short:** multi-module architecture splits a large app into Gradle modules to improve boundaries, build performance, ownership and testability, but it should be introduced pragmatically.

### Feature modules

A feature module contains code for a specific feature or user flow: login, profile, payments, product details, settings, onboarding.

A feature module usually includes UI, `ViewModel` / state holder, feature-specific models, a navigation entry point and sometimes feature-specific domain logic. Shared things should not be copied into every feature; they should live in core modules.

Feature modules help isolate responsibility: a team can change a feature without touching the whole app module. They can also speed up builds and improve architectural boundaries.

**Important:** feature modules should not directly depend on each other chaotically. Communication between features often uses navigation contracts, interfaces, shared domain models or an app-level coordinator.

**In short:** feature modules isolate user-facing features and should depend on shared core/domain contracts rather than directly knowing about every other feature.

### Core modules

Core modules contain reusable infrastructure and shared code needed by several features.

Typical core modules: `core:network`, `core:database`, `core:ui` / `designsystem`, `core:common`, `core:model`, `core:analytics`, `core:testing`, `core:datastore`.

A good core module has a clear responsibility and a stable public API. It should not become a dumping ground for everything.

Core modules usually should not depend on feature modules. Dependencies usually go from features to core, while the app module wires everything together.

**Important:** overly generic `core:utils` quickly turns into a junk module. It is better to create small modules by responsibility: formatting, date/time, dispatchers, logging, permissions, design system.

**In short:** core modules hold reusable infrastructure and shared contracts, but they must stay focused and not become a global utils dump.

## Dependencies

### Dependency graph

Dependency graph shows which modules depend on each other. In a good architecture it is directed and clear: app module assembles features, features depend on domain/core contracts, data modules implement repositories and depend on network/database.

The main goal is to avoid chaotic dependencies where any module can import any other module. That breaks boundaries and makes changes expensive.

A common principle: low-level shared modules do not depend on high-level feature modules. Domain/contracts should be more stable than concrete data/UI implementations.

DI helps connect implementations to abstractions: a feature or domain layer can depend on a `Repository` interface, while the app/data layer provides the implementation through a Hilt/Dagger module.

**In short:** module dependency graph should be acyclic and layered; app wiring and DI connect modules without breaking boundaries.

### Cyclic dependencies

A cyclic dependency appears when module A depends on module B, and B directly or indirectly depends on A.

Gradle usually does not allow direct cycles, but architectural cycles can appear through shared modules, callbacks, navigation and misplaced interfaces.

The problem with cycles is that modules cannot be built, tested and reused independently. Any change pulls the dependency chain backwards and defeats the purpose of modularization.

The solution is to move the shared contract into a separate module, invert the dependency through an interface, use DI, an event/navigation contract or an app-level coordinator.

Example: if feature A needs to open feature B, A should not depend directly on implementation B. A Route/Navigation contract can be moved into a shared module, and the app module performs the actual navigation.

**In short:** cyclic dependencies mean module boundaries are wrong; usually the cycle is broken by extracting a contract module or inverting the dependency.
