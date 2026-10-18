# Architecture

This section covers Android application architecture: responsibility boundaries, state ownership, unidirectional data flow, MV* patterns, modularization, and incremental change in legacy systems.

For a practical learning path, start with architecture basics and UI state. Then compare MV* patterns as alternative ways to organize presentation logic. Study multi-module architecture when the codebase and team need clearer boundaries, and use the legacy section when changing an existing system safely.

## Design and state

- [Architecture Basics](basics.md) - layers, dependency direction, repositories, optional domain logic, unidirectional data flow, and sources of truth.
- [UI State Architecture](ui-state.md) - state ownership, immutable UI models, events, effects, lifecycle boundaries, and state restoration.
- [MV* Patterns](mv-patterns.md) - MVC, MVP, MVVM, and MVI responsibilities, reducers, effects, and pragmatic pattern selection.

## Scale and change

- [Multi-module Architecture](multi-module.md) - module boundaries, public APIs, dependency rules, Gradle configurations, and measurement-driven modularization.
- [Legacy & Refactoring](legacy-refactoring.md) - behavior-preserving changes, safety checks, incremental migration, lifecycle risks, and replacing legacy UI or reactive code.
