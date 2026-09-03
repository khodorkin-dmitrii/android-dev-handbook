# Pages Review Tracker
This is an internal editorial tracker for Android Dev Handbook article review.
It is intentionally kept as an unlisted service page: available by direct URL, but not part of the main learning navigation.
The initial priority order is based on `pages_review_priority.txt`.

## Status legend
1. `TODO` - the article has not passed the focused review/update pass yet.
1. `UPDATED` - the article was reviewed and meaningfully updated; the paired Russian version is expected to be synchronized as part of the normal workflow.

## Current snapshot
1. Last tracker update: 2026-09-03
1. Total articles tracked: 71
1. Updated: 18
1. TODO: 53

| Priority | Total | Updated | TODO |
|---|---|---|---|
| P0 | 26 | 15 | 11 |
| P1 | 27 | 2 | 25 |
| P2 | 18 | 1 | 17 |

## Tracker

1. P0, **UPDATED**, 2026-06-29, `compose/state-recomposition.md`, State & Recomposition, Expanded Compose state basics, mutableStateOf, state ownership, state hoisting, model stability, derivedStateOf, and practical recomposition reduction techniques.
1. P0, **UPDATED**, 2026-06-29, `coroutines-flow/basics.md`, Coroutines Basics, Expanded coroutine fundamentals: blocking vs suspending, threads, concurrency vs parallelism, suspend, CPU-bound vs I/O-bound work, dispatchers, withContext, launch vs async, builders, and runBlocking.
1. P0, **UPDATED**, 2026-07-03, `compose/basics.md`, Compose Basics, Expanded Compose basics with Compose vs View System comparison, state-driven UI example, clearer recomposition wording, composable anti-patterns, and related topic links.
1. P0, **UPDATED**, 2026-07-09, `compose/side-effects.md`, Side Effects, Expanded side-effect guidance with an API selection table, Kotlin examples, `rememberUpdatedState`, `snapshotFlow`, common mistakes, and related topic links.
1. P0, **UPDATED**, 2026-08-11, `compose/performance.md`, Compose Performance, Expanded measurement guidance, lazy list identity and reuse, composition work, frequently changing state, `derivedStateOf`, stability, backwards writes, and common performance mistakes.
1. P0, **UPDATED**, 2026-08-11, `coroutines-flow/scopes-cancellation.md`, Coroutine Scopes & Cancellation, Expanded scope ownership, structured concurrency, Job hierarchy, supervision, cooperative cancellation, cleanup, timeout handling, and practical Android lifecycle guidance.
1. P0, **UPDATED**, 2026-08-29, `coroutines-flow/flow-basics.md`, Flow Basics, clarified the Flow pipeline, collection semantics, context, cancellation, and error handling.
1. P0, **UPDATED**, 2026-08-29, `coroutines-flow/flow-operators.md`, Flow Operators, reorganized operator selection and clarified flattening, combining, buffering, retry, and terminal semantics.
1. P0, **UPDATED**, 2026-08-30, `coroutines-flow/stateflow-sharedflow.md`, StateFlow & SharedFlow, clarified delivery semantics, added stateIn/shareIn, and improved lifecycle guidance.
1. P0, **UPDATED**, 2026-08-31, `coroutines-flow/lifecycle-aware-collection.md`, Lifecycle-aware Collection, Clarified cancellation and restart semantics, StateFlow and Flow collection, parallel collectors, Compose effect handling, and the lifecycle limitations of LaunchedEffect.
1. P0, **UPDATED**, 2026-09-03, `architecture/basics.md`, Architecture Basics, Clarified layer responsibilities, unidirectional data flow, Clean Architecture dependency semantics, repository boundaries, domain-layer trade-offs, and single-source-of-truth ownership.
1. P0, **UPDATED**, 2026-07-03, `architecture/ui-state.md`, UI State Architecture, Added state restoration guidance: state ownership, lifecycle boundaries, SavedStateHandle, repository/storage, temporary UI scopes, and feature design restoration decisions.
1. P0, **UPDATED**, 2026-09-03, `architecture/mv-patterns.md`, MV* Patterns, Clarified MVC, MVP, MVVM and MVI responsibilities, distinguished Jetpack ViewModel from MVVM, explained reducer and effect boundaries, and added a pragmatic MVVM/MVI comparison.
1. P0, **UPDATED**, 2026-09-03, `architecture/multi-module.md`, Multi-module Architecture, Streamlined modularization strategies, clarified module APIs and dependency rules, added Gradle api/implementation guidance, and made build-performance recommendations measurement-driven.
1. P0, **UPDATED**, 2026-08-23, `android/activity-fragment-lifecycle.md`, Activity, Fragment & Lifecycle
1. P0, **TODO**, , `android/components.md`, Android Components
1. P0, **TODO**, , `android/view-system-xml-ui.md`, View System / XML UI
1. P0, **TODO**, , `android/background-work-system-behavior.md`, Background Work & System Behavior
1. P0, **TODO**, , `android/gradle-build-system.md`, Gradle & Build System
1. P0, **TODO**, , `android/performance-memory.md`, Performance & Memory
1. P0, **TODO**, , `di/basics.md`, DI Basics
1. P0, **TODO**, , `di/dagger-hilt.md`, Dagger / Hilt
1. P0, **TODO**, , `di/koin.md`, Koin
1. P0, **TODO**, , `testing/strategy.md`, Testing Strategy
1. P0, **TODO**, , `testing/viewmodel-testing.md`, ViewModel Testing
1. P0, **TODO**, , `testing/coroutines-flow-testing.md`, Coroutines & Flow Testing
1. P1, **TODO**, , `kotlin/basics.md`, Kotlin Basics
1. P1, **TODO**, , `kotlin/kotlin-vs-java.md`, Kotlin vs Java
1. P1, **TODO**, , `kotlin/classes-and-types.md`, Classes & Types
1. P1, **TODO**, , `kotlin/collections.md`, Collections
1. P1, **TODO**, , `kotlin/functions.md`, Functions
1. P1, **TODO**, , `kotlin/generics.md`, Generics
1. P1, **TODO**, , `java/core.md`, Java Core
1. P1, **TODO**, , `java/concurrency.md`, Java Concurrency
1. P1, **TODO**, , `java/exceptions.md`, Java Exceptions
1. P1, **TODO**, , `java/jvm-android-runtime.md`, JVM / Android Runtime
1. P1, **TODO**, , `android/storage.md`, Storage
1. P1, **TODO**, , `android/context-resources.md`, Context & Resources
1. P1, **UPDATED**, 2026-06-30, `networking/http-rest.md`, HTTP / REST, Expanded HTTP/REST fundamentals: HTTP methods, safe/idempotent semantics, GET vs POST, status codes table, headers/body, and Android error mapping.
1. P1, **UPDATED**, 2026-06-30, `networking/retrofit-okhttp.md`, Retrofit / OkHttp, Expanded Retrofit/OkHttp: service API examples, Response<T>, OkHttp setup, interceptors, auth interceptor, serialization pitfalls, NetworkResult, request debugging, logging, common mistakes, and production recommendations.
1. P1, **TODO**, , `networking/graphql.md`, GraphQL
1. P1, **TODO**, , `networking/grpc-protobuf.md`, gRPC / Protobuf
1. P1, **TODO**, , `testing/android-ui-testing.md`, Android UI Testing
1. P1, **TODO**, , `engineering/code-quality.md`, Code Quality
1. P1, **TODO**, , `engineering/code-review.md`, Code Review
1. P1, **TODO**, , `engineering/oop.md`, OOP
1. P1, **TODO**, , `engineering/solid.md`, SOLID
1. P1, **TODO**, , `engineering/design-patterns.md`, Design Patterns
1. P1, **TODO**, , `engineering/algorithms-complexity.md`, Algorithms & Complexity
1. P1, **TODO**, , `engineering/memory-runtime-basics.md`, Memory & Runtime Basics
1. P1, **TODO**, , `architecture/legacy-refactoring.md`, Legacy & Refactoring
1. P1, **TODO**, , `di/legacy-di.md`, Legacy DI
1. P1, **TODO**, , `legacy/rxjava.md`, RxJava
1. P2, **UPDATED**, 2026-06-30, `index.md`, Home, Added GitHub repository link to the author/support block.
1. P2, **TODO**, , `android/index.md`, Android Overview
1. P2, **TODO**, , `kotlin/index.md`, Kotlin Overview
1. P2, **TODO**, , `compose/index.md`, Compose Overview
1. P2, **TODO**, , `coroutines-flow/index.md`, Coroutines & Flow Overview
1. P2, **TODO**, , `architecture/index.md`, Architecture Overview
1. P2, **TODO**, , `java/index.md`, Java Overview
1. P2, **TODO**, , `di/index.md`, DI Overview
1. P2, **TODO**, , `networking/index.md`, Networking Overview
1. P2, **TODO**, , `testing/index.md`, Testing Overview
1. P2, **TODO**, , `engineering/index.md`, Engineering Overview
1. P2, **TODO**, , `legacy/index.md`, Legacy Overview
1. P2, **TODO**, , `compose/testing.md`, Compose Testing
1. P2, **TODO**, , `android/canvas.md`, Android Canvas
1. P2, **TODO**, , `android/opengl-es.md`, OpenGL ES
1. P2, **TODO**, , `android/vulkan.md`, Vulkan
1. P2, **TODO**, , `android/google-filament.md`, Google Filament
1. P2, **TODO**, , `android/2d-3d-rendering.md`, 2D and 3D Rendering
