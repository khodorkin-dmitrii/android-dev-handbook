# Multi-module Architecture

Multi-module architecture splits an Android project into Gradle modules with explicit boundaries, dependencies and ownership. It becomes useful when one application module is difficult to build, test, navigate or maintain.

The goal is not the highest possible module count. Good modules represent real product or technical responsibilities and expose small, stable APIs.

## What problem does modularization solve?

Modularization can provide:

- clearer ownership and dependency boundaries;
- isolated testing and implementation changes;
- reuse across features or applications;
- parallel work with fewer conflicts;
- faster incremental or parallel builds when the dependency graph and build configuration support it.

These benefits are not automatic. Every module adds Gradle configuration, dependency and DI wiring, navigation contracts and maintenance. Excessive or poorly connected modules can make both development and builds slower. A small application may need only packages inside `:app` or a few broad modules.

Aim for **high cohesion** inside a module and **low coupling** between modules.

## Modularization strategies

### Layer-based modularization

Layer-based modularization mirrors architectural layers at the Gradle level:

```text
:app
:presentation
:domain
:data
```

The dependency direction is easy to explain: presentation uses domain contracts, data provides repository implementations, and `:app` assembles the graph.

The drawback is that one product change may span every technical module:

```text
:presentation  -> payment screen, ViewModel, UI state
:domain        -> payment use case and repository contract
:data          -> repository implementation, API and cache
```

This can work in small or medium projects, but broad layer modules often become technical monoliths with unclear feature ownership.

### Feature-based modularization

Feature-based modularization groups code by user-facing capability:

```text
:app
:feature:profile
:feature:payments
:feature:settings
:core:network
:core:database
:core:ui
```

A feature module can own its UI, state, feature-specific logic and navigation entry points. This usually matches how product teams deliver changes and makes a feature easier to isolate, replace or remove.

A feature module can still become a mini-monolith. Shared code may be duplicated or extracted too early, and cross-feature navigation needs explicit contracts.

### Pragmatic hybrid approach

A common practical structure combines feature modules with focused infrastructure and shared business modules:

```text
:app

:core:network
:core:database
:core:designsystem
:core:analytics

:shared:user
:shared:subscriptions

:feature:profile
:feature:payments
:feature:settings
```

The names are conventions, not Android requirements:

- `:app` is the application entry point. It owns startup, root navigation and application assembly, but not all product logic.
- `:core:*` contains focused technical capabilities such as networking, persistence, analytics or a design system. Avoid a generic `core:utils` dumping ground.
- `:shared:*` contains stable business capabilities genuinely reused by several features. Code used by one feature should normally stay in that feature.
- `:feature:*` owns a product capability. It can use internal `presentation`, `domain` and `data` packages without making each package a Gradle module.

Split a large feature further into `api` and `impl`, or presentation/domain/data modules, only when it improves reuse, ownership, dependency control or build performance.

## Module APIs and dependency rules

Expose as little as possible. Kotlin `internal` declarations stay inside the Gradle module, which helps keep implementation details out of other modules. Place only stable entry points, models and contracts in the public API.

For Gradle dependencies:

- `implementation(project(...))` keeps the dependency from leaking to consumers and should be the default;
- `api(project(...))` exposes the dependency to consumers and should be used only when it is part of the module's public API.

A simple default graph is:

```text
feature -> core
feature -> shared
feature -> feature  // avoid by default
app     -> features // application assembly
```

Direct feature-to-feature dependencies create hidden coupling and can produce cycles. Prefer a small shared contract or an `api` module, while `:app` or root navigation connects implementations.

For example, `:feature:profile` should not depend on the payments implementation just to open a payment screen. It can emit or use a navigation contract, and the application-level coordinator resolves the destination.

If a dependency cycle appears, reconsider the boundary. Extract a smaller shared contract, invert the dependency through an interface, or move orchestration upward.

## How to decide

Create a Gradle module when several of these are true:

- the code has a cohesive responsibility and stable boundary;
- it is reused by multiple features or applications;
- a team can own it independently;
- it prevents unwanted dependencies;
- it can be built and tested in isolation;
- build measurements show an isolation or caching benefit;
- it exposes a small, meaningful public API.

Keep code in an existing module when the proposed module only mirrors a folder, has an unstable boundary, is used by one small feature, or makes ordinary changes touch more modules without adding isolation.

Start with the simplest structure that works. Extract modules in response to real ownership, reuse, dependency or measured build problems rather than a target module count.

## Build configuration

More modules can improve incremental compilation, parallel execution and build-cache reuse because unchanged modules may be skipped. They can also increase configuration and task overhead. Measure clean builds and representative incremental changes before and after modularization instead of assuming an improvement.

As the project grows, use convention plugins, version catalogs and consistent module templates to avoid copying Gradle configuration across every `build.gradle.kts`.

## Related topics

- [Architecture Basics](basics.md)
- [MV* Patterns](mv-patterns.md)
- [Gradle & Build System](../android/gradle-build-system.md)
- [Dependency Injection Basics](../di/basics.md)
