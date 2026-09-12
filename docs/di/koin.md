# Koin

Koin is a dependency injection framework designed for Kotlin. Its classic API describes modules and object creation with a Kotlin DSL, without requiring annotations or generated components. Koin supports Android, Kotlin Multiplatform and other Kotlin targets.

Koin is easy to introduce, but it is still a container whose ownership, lifetimes and startup configuration must be designed deliberately.

## Koin basics

A module groups definitions. Prefer constructor references when they keep the graph readable:

```kotlin
val appModule = module {
    singleOf(::DefaultUserRepository) bind UserRepository::class
    factoryOf(::LoadUserUseCase)
    viewModelOf(::UserViewModel)
}
```

The main definition types are:

| Definition | Behavior | Typical use |
|---|---|---|
| `single` | One instance per Koin container | Database, API client, repository |
| `factory` | New instance for every resolution | Lightweight, independent objects |
| `scoped` | One instance inside an explicit scope | Session- or screen-owned objects |
| `viewModel` | Created through Android `ViewModelProvider` | Android ViewModels |

`single` does not mean a JVM-global singleton. Its instance belongs to the Koin application that contains the definition and is created lazily by default.

Start Koin once, normally from `Application`:

```kotlin
class App : Application() {
    override fun onCreate() {
        super.onCreate()

        startKoin {
            androidContext(this@App)
            modules(appModule)
        }
    }
}
```

Keep ordinary classes independent of Koin and use constructor injection. Resolve dependencies at composition roots such as Android entry points, rather than calling `get()` throughout business code. This keeps dependencies visible and makes unit tests simple.

## Qualifiers

Use a qualifier when several definitions have the same type:

```kotlin
val networkModule = module {
    single(named("authenticated")) { authenticatedClient(get()) }
    single(named("public")) { publicClient() }
}
```

String qualifiers are concise but can be mistyped, so centralize them or prefer typed qualifiers in larger graphs. Values known only at the call site can be supplied with `parametersOf(...)`; reserve this mechanism for real runtime input rather than hiding long-lived configuration.

## Validation and testing

With the classic DSL, missing definitions, wrong qualifiers and some cycles may appear only when the affected dependency is resolved. Validate modules in tests and exercise important entry points, not just application startup.

Modern Koin also offers annotations and compiler-plugin-based DSL options that can generate wiring and catch more errors during the build. These improve safety, but they are separate from the behavior of the classic runtime DSL and should not be assumed unless the project enables them.

Tests can use test modules, but direct constructor injection is often simpler for unit tests. Isolate the Koin application between tests to avoid shared state and order-dependent failures.

## Koin vs Hilt

| Topic | Hilt | Koin classic DSL |
|---|---|---|
| Graph construction | Generated Dagger components | Runtime container |
| Error detection | Strong compile-time validation | Primarily resolution-time; module checks help |
| Configuration | Annotations, modules and predefined components | Kotlin DSL definitions |
| Android lifetimes | Standard generated component hierarchy | ViewModel integration and explicit scopes |
| Multiplatform | Dagger/Hilt graph is Android/JVM-oriented | Koin Core supports Kotlin Multiplatform |

Hilt is a strong default when a large Android graph benefits from strict compile-time validation and standardized lifecycle components. Koin is attractive when a team values concise Kotlin configuration, fast adoption or shared Kotlin Multiplatform infrastructure.

Do not choose only by project size. Consider team experience, build tooling, failure detection, lifecycle ownership, test strategy and whether the dependency graph crosses platform boundaries.

## Related topics

- [DI Basics](basics.md)
- [Dagger / Hilt](dagger-hilt.md)
- [Multi-module Architecture](../architecture/multi-module.md)
- [ViewModel Testing](../testing/viewmodel-testing.md)
