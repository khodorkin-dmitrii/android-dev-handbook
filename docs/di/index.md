# DI

This section covers dependency injection in Android: dependency ownership, composition roots, constructor injection, scopes, graph validation, testing, and framework trade-offs.

For a practical learning path, start with the DI principles and manual wiring. Continue with Dagger and Hilt to understand compile-time graphs and Android component lifetimes, then compare Koin's runtime DSL. Use the legacy article when maintaining an older project or planning an incremental migration.

## Foundations

- [DI Basics](basics.md) - dependencies, composition roots, constructor injection, runtime values, scopes, Service Locator trade-offs, and singleton lifetime risks.

## Android DI frameworks

- [Dagger / Hilt](dagger-hilt.md) - compile-time graphs, constructor and module bindings, qualifiers, component visibility, scopes, and ViewModel integration.
- [Koin](koin.md) - runtime definitions, constructor DSL, qualifiers, parameters, lifecycle-aware scopes, validation, and test isolation.

## Legacy projects and migration

- [Legacy DI](legacy-di.md) - older Dagger versions, Toothpick, Moxy-related lifecycle concerns, scope ownership, migration checks, and safe replacement strategies.
