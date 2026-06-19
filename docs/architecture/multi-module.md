# Multi-module Architecture

Multi-module architecture splits an Android project into Gradle modules with explicit boundaries, dependencies and ownership. It is useful when a project is large enough that one application module becomes hard to build, test, navigate and maintain.

The goal is not to create as many modules as possible. The goal is to make boundaries match real product and technical responsibilities.

## What problem multi-module architecture solves

Multi-module architecture can help with build scalability, clearer code ownership, reusable shared logic and stricter dependency boundaries. A feature can often be built, tested, rewritten or migrated with less impact on the rest of the app.

It also helps large teams work in parallel. When modules have stable public APIs, teams can own features or shared capabilities without constantly changing the same files.

The trade-off is real: more modules mean more Gradle configuration, more dependency coordination, more DI wiring, more navigation contracts and more decisions about where code belongs. A small app may be better served by a simple package structure inside one or a few modules.

**In short:** multi-module architecture is useful when isolation, ownership and build scalability justify the Gradle and coordination cost.

## Layer-based modularization

Layer-based modularization mirrors Clean Architecture layers at the Gradle module level:

```text
:app
:presentation
:domain
:data
```

This can look clean because dependency direction is obvious: UI depends on domain contracts, data implements repositories, and the app module wires everything together. It can be useful for learning Clean Architecture, separating concerns and testing domain logic independently.

The limitation is that product features often get scattered across technical buckets. A payments change may require touching `:presentation`, `:domain` and `:data` at the same time:

```text
:presentation  -> payments screen, ViewModel, UI state
:domain        -> payments use cases, entities, repository interface
:data          -> payments repository implementation, API, local cache
```

For small or medium projects this may be acceptable. For larger product apps, these modules can become large technical monoliths: every feature lives in every layer, ownership is unclear, and adding a feature touches several broad modules.

Layer-based modules are not useless. They can help with dependency direction, testability and explicit architecture boundaries. The problem is applying them mechanically as the main modularization strategy for the whole app.

**Pros:**

- clear dependency direction;
- easy to explain Clean Architecture boundaries;
- useful for small and medium apps;
- domain logic can be tested separately;
- technical responsibilities are visible.

**Cons:**

- feature code is scattered across modules;
- ownership is often unclear;
- modules can become large technical buckets;
- adding a feature may require touching many modules;
- reuse does not happen automatically;
- it can become the same monolith split into several technical parts.

## Feature-based modularization

Feature-based modularization groups code by product functionality:

```text
:app
:feature:profile
:feature:payments
:feature:offers
:feature:settings
:core:network
:core:database
:core:ui
```

A feature module owns a user-facing capability or flow: profile, payments, checkout, offers, settings, onboarding. This often matches how teams work and how changes are delivered.

Feature modules keep related UI, state, feature-specific business logic and navigation entry points close together. A team can change or rewrite a feature without spreading the work across global technical modules.

Feature-based modularization is not magic. Without internal rules, a feature module can become a mini-monolith. Shared logic can be duplicated, moved too early into `core`, or coupled through unstable contracts. Navigation and DI boundaries also become more important.

**Pros:**

- feature code is closer together;
- ownership is easier to define;
- features are easier to isolate, delete, rewrite or migrate;
- large apps and multiple teams usually scale better;
- module boundaries are closer to product boundaries.

**Cons:**

- feature modules can become mini-monoliths;
- shared logic may be duplicated or extracted too early;
- clear dependency rules are required;
- navigation contracts and DI setup need more care;
- cross-feature flows require explicit coordination.

## Pragmatic hybrid approach

For many real Android projects, the best default is a hybrid structure: feature modules for product areas, core modules for technical infrastructure, and shared modules only where reuse is real.

```text
:app

:core:network
:core:database
:core:datetime
:core:ui
:core:analytics

:shared:user
:shared:payments
:shared:offers

:feature:profile
:feature:payments
:feature:checkout
:feature:settings
```

### `:app`

The `:app` module is the application entry point. It owns startup logic, root navigation, app-level DI wiring, global configuration and assembly of features.

It should coordinate the application, not contain all product logic.

### `:core`

`core` modules contain reusable technical infrastructure: network clients, database setup, logging, analytics, dispatchers, date/time, design system, common UI components and testing utilities.

Good `core` modules are small and focused. Avoid a vague `core:utils` module that becomes a dumping ground for unrelated helpers.

### `:shared`

`shared` modules contain reusable business or domain capabilities used by multiple features: user, payments, offers, permissions, subscriptions.

They should be created only when there is real reuse or a stable boundary. If code belongs to one feature only, it usually should stay inside that feature.

### `:feature`

Feature modules encapsulate product functionality. A feature can contain internal packages such as `presentation`, `domain` and `data`:

```text
:feature:payments
  presentation/
  domain/
  data/
```

This keeps Clean Architecture separation where it helps, without forcing every layer into a separate Gradle module.

Split feature internals into separate Gradle modules only when the feature is large enough, reused independently, owned independently or has a build-performance reason.

## How to decide

Use a separate Gradle module when:

- the code is reused by multiple features;
- the boundary is stable;
- a team can own it independently;
- it improves build performance or isolation;
- it prevents unwanted dependencies;
- it can be tested independently;
- it exposes a clear public API.

Do not create a separate Gradle module when:

- it only mirrors a folder or package;
- it is used by one feature only;
- it adds Gradle boilerplate without isolation;
- it makes simple changes require touching many modules;
- the boundary is still unstable;
- the module would become a generic dumping ground.

**Practical approach:** multi-module architecture is useful when the project is large enough to benefit from isolation, ownership and build scalability. Avoid splitting the whole app only by Clean Architecture layers such as `data`, `domain` and `presentation`, because this can scatter features across technical modules. For larger Android apps, prefer a feature-based structure with focused `core` technical modules and `shared` domain modules where reuse is real. Inside a feature, keep `presentation`, `domain` and `data` separation as packages, and extract them into Gradle modules only when there is a practical reason.

## Dependency rules

A good module graph is directed and boring. Low-level shared modules should not depend on high-level feature modules. Feature modules should not depend on each other randomly. The `:app` module often wires features together through navigation, DI and app-level coordination.

When a cycle appears, the boundary is usually wrong. Move the shared contract into a smaller module, invert the dependency through an interface, or let `:app` coordinate the interaction.

Example: if `:feature:profile` needs to open `:feature:payments`, profile should not depend directly on the payments implementation. A route or navigation contract can live in a shared contract module, and `:app` can perform the actual navigation.

**Key idea:** feature-based modularization is usually the better default direction for large product apps, but layer separation still matters. It often belongs inside features as packages, and becomes separate Gradle modules only when reuse, ownership or build isolation justifies the cost.
