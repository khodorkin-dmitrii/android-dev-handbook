# Pages Review Tracker
This is an internal editorial tracker for Android Dev Handbook article review.
It is intentionally kept as an unlisted service page: available by direct URL, but not part of the main learning navigation.
The initial priority order is based on `pages_review_priority.txt`.

## Status legend
- `TODO` - the article has not passed the focused review/update pass yet.
- `UPDATED` - the article was reviewed and meaningfully updated; the paired Russian version is expected to be synchronized as part of the normal workflow.

## Current snapshot
- Last tracker update: 2026-07-03
- Total articles tracked: 71
- Updated: 6
- TODO: 65

| Priority | Total | Updated | TODO |
|---|---:|---:|---:|
| P0 | 26 | 3 | 23 |
| P1 | 27 | 2 | 25 |
| P2 | 18 | 1 | 17 |

## Tracker

- P0 - 01, UPDATED, State & Recomposition, `compose/state-recomposition.md`, 2026-07-03, Expanded Compose state basics, mutableStateOf, state ownership, state hoisting, model stability, derivedStateOf, and practical recomposition reduction techniques.
- P0 - 02, UPDATED, Coroutines Basics, `coroutines-flow/basics.md`, 2026-07-03, Expanded coroutine fundamentals: blocking vs suspending, threads, concurrency vs parallelism, suspend, CPU-bound vs I/O-bound work, dispatchers, withContext, launch vs async, builders, and runBlocking.
- P0 - 03, TODO, Compose Basics, `compose/basics.md` 
- P0 - 04, TODO, Side Effects, `compose/side-effects.md` 
- P0 - 05, TODO, Compose Performance, `compose/performance.md` 
- P0 - 06, TODO, Coroutine Scopes & Cancellation, `coroutines-flow/scopes-cancellation.md` 
- P0 - 07, TODO, Flow Basics, `coroutines-flow/flow-basics.md` 
- P0 - 08, TODO, Flow Operators, `coroutines-flow/flow-operators.md` 
- P0 - 09, TODO, StateFlow & SharedFlow, `coroutines-flow/stateflow-sharedflow.md` 
- P0, 10, TODO, Lifecycle-aware Collection, `coroutines-flow/lifecycle-aware-collection.md` 
- P0, 11, TODO, Architecture Basics, `architecture/basics.md` 
- P0, 12, UPDATED, UI State Architecture, `architecture/ui-state.md`, 2026-07-03, Added state restoration guidance: state ownership, lifecycle boundaries, SavedStateHandle, repository/storage, temporary UI scopes, and feature design restoration decisions.
- P0, 13, TODO, MV* Patterns, `architecture/mv-patterns.md` 
- P0, 14, TODO, Multi-module Architecture, `architecture/multi-module.md` 
- P0, 15, TODO, Activity, Fragment & Lifecycle, `android/activity-fragment-lifecycle.md` 
- P0, 16, TODO, Android Components, `android/components.md` 
- P0, 17, TODO, View System / XML UI, `android/view-system-xml-ui.md` 
- P0, 18, TODO, Background Work & System Behavior, `android/background-work-system-behavior.md` 
- P0, 19, TODO, Gradle & Build System, `android/gradle-build-system.md` 
- P0, 20, TODO, Performance & Memory, `android/performance-memory.md` 
- P0, 21, TODO, DI Basics, `di/basics.md` 
- P0, 22, TODO, Dagger / Hilt, `di/dagger-hilt.md` 
- P0, 23, TODO, Koin, `di/koin.md` 
- P0, 24, TODO, Testing Strategy, `testing/strategy.md` 
- P0, 25, TODO, ViewModel Testing, `testing/viewmodel-testing.md` 
- P0, 26, TODO, Coroutines & Flow Testing, `testing/coroutines-flow-testing.md` 
- P1, 27, TODO, Kotlin Basics, `kotlin/basics.md` 
- P1, 28, TODO, Kotlin vs Java, `kotlin/kotlin-vs-java.md` 
- P1, 29, TODO, Classes & Types, `kotlin/classes-and-types.md` 
- P1, 30, TODO, Collections, `kotlin/collections.md` 
- P1, 31, TODO, Functions, `kotlin/functions.md` 
- P1, 32, TODO, Generics, `kotlin/generics.md` 
- P1, 33, TODO, Java Core, `java/core.md` 
- P1, 34, TODO, Java Concurrency, `java/concurrency.md` 
- P1, 35, TODO, Java Exceptions, `java/exceptions.md` 
- P1, 36, TODO, JVM / Android Runtime, `java/jvm-android-runtime.md` 
- P1, 37, TODO, Storage, `android/storage.md` 
- P1, 38, TODO, Context & Resources, `android/context-resources.md` 
- P1, 39, UPDATED, HTTP / REST, `networking/http-rest.md`, 2026-07-03, Expanded HTTP/REST fundamentals: HTTP methods, safe/idempotent semantics, GET vs POST, status codes table, headers/body, and Android error mapping.
- P1, 40, UPDATED, Retrofit / OkHttp, `networking/retrofit-okhttp.md`, 2026-07-03, Expanded Retrofit/OkHttp: service API examples, Response<T>, OkHttp setup, interceptors, auth interceptor, serialization pitfalls, NetworkResult, request debugging, logging, common mistakes, and production recommendations.
- P1, 41, TODO, GraphQL, `networking/graphql.md` 
- P1, 42, TODO, gRPC / Protobuf, `networking/grpc-protobuf.md` 
- P1, 43, TODO, Android UI Testing, `testing/android-ui-testing.md` 
- P1, 44, TODO, Code Quality, `engineering/code-quality.md` 
- P1, 45, TODO, Code Review, `engineering/code-review.md` 
- P1, 46, TODO, OOP, `engineering/oop.md` 
- P1, 47, TODO, SOLID, `engineering/solid.md` 
- P1, 48, TODO, Design Patterns, `engineering/design-patterns.md` 
- P1, 49, TODO, Algorithms & Complexity, `engineering/algorithms-complexity.md` 
- P1, 50, TODO, Memory & Runtime Basics, `engineering/memory-runtime-basics.md` 
- P1, 51, TODO, Legacy & Refactoring, `architecture/legacy-refactoring.md` 
- P1, 52, TODO, Legacy DI, `di/legacy-di.md` 
- P1, 53, TODO, RxJava, `legacy/rxjava.md` 
- P2, 54, UPDATED, Home, `index.md`, 2026-07-03, Added GitHub repository link to the author/support block.
- P2, 55, TODO, Android Overview, `android/index.md` 
- P2, 56, TODO, Kotlin Overview, `kotlin/index.md` 
- P2, 57, TODO, Compose Overview, `compose/index.md` 
- P2, 58, TODO, Coroutines & Flow Overview, `coroutines-flow/index.md` 
- P2, 59, TODO, Architecture Overview, `architecture/index.md` 
- P2, 60, TODO, Java Overview, `java/index.md` 
- P2, 61, TODO, DI Overview, `di/index.md` 
- P2, 62, TODO, Networking Overview, `networking/index.md` 
- P2, 63, TODO, Testing Overview, `testing/index.md` 
- P2, 64, TODO, Engineering Overview, `engineering/index.md` 
- P2, 65, TODO, Legacy Overview, `legacy/index.md` 
- P2, 66, TODO, Compose Testing, `compose/testing.md` 
- P2, 67, TODO, Android Canvas, `android/canvas.md` 
- P2, 68, TODO, OpenGL ES, `android/opengl-es.md` 
- P2, 69, TODO, Vulkan, `android/vulkan.md` 
- P2, 70, TODO, Google Filament, `android/google-filament.md` 
- P2, 71, TODO, 2D and 3D Rendering, `android/2d-3d-rendering.md` 
