# Dagger / Hilt

Hilt is an Android-focused DI layer on top of Dagger. It reduces boilerplate, defines a standard component hierarchy and connects the DI graph to the Android lifecycle.

## Hilt and Dagger

### What is Hilt?

Hilt is a DI framework for Android built on top of Dagger. It simplifies dependency injection integration in an Android app and provides ready-made entry points, components and scopes for the Android lifecycle.

Hilt is usually connected through `@HiltAndroidApp` on `Application`, `@AndroidEntryPoint` on `Activity` / `Fragment` / `Service` / `Receiver`, `@HiltViewModel` for `ViewModel` and constructor injection with `@Inject`.

The main benefit of Hilt is less manual Dagger boilerplate: for most standard cases, there is no need to manually define `AppComponent`, subcomponents, component factories and Android-specific wiring.

But Hilt does not remove the need to understand Dagger: object graph, bindings, modules, scopes, qualifiers and compile-time errors still matter.

**In short:** Hilt is the recommended Android DI layer on top of Dagger; it reduces Android boilerplate while keeping Dagger's compile-time graph validation.

### Hilt vs Dagger

Dagger is a general-purpose compile-time DI framework. It generates code for the dependency graph and validates bindings at compile time.

Hilt is an opinionated Android integration on top of Dagger. It provides a standard component hierarchy, connects it to the Android lifecycle and gives convenient annotations for Android entry points.

With pure Dagger, a team has more flexibility: components, scopes, factories and multi-module setup can be fully controlled. The cost is more boilerplate and more complex setup.

Hilt is usually better for modern Android apps that need standard Application/Activity/Fragment/ViewModel scopes and less manual wiring. Pure Dagger can be useful in legacy code, non-Android modules or complex custom graph architecture.

**In short:** Dagger is the underlying DI engine, Hilt is the Android-focused layer that standardizes components and removes much of the setup boilerplate.

## Bindings

### `@Inject`

`@Inject` is used in two main places: on a constructor so Dagger/Hilt can create the object, and on fields/methods to inject into an object that is not created by the DI container.

Constructor injection is the preferred option for classes we own: repositories, use cases, mappers, managers, validators.

```kotlin
class UserRepository @Inject constructor(
    private val api: ApiService,
    private val dao: UserDao
)
```

If a class has an `@Inject constructor` and all its dependencies are known to the graph, a separate `@Provides` method is usually not needed.

Field injection in Android is mostly needed for framework-created classes such as `Activity`, `Fragment`, `Service` or `BroadcastReceiver` after `@AndroidEntryPoint`. For regular classes, constructor injection is better because dependencies are visible and the object is easier to test.

**In short:** use `@Inject constructor` for classes you own; field injection is mostly for Android classes created by the framework.

### `@Provides` vs `@Binds`

`@Provides` is a method in `@Module` that manually creates a dependency. It is needed when an object cannot be created through an `@Inject constructor`: external SDK, Retrofit, OkHttp, Room database, `DataStore`, builder/factory API, runtime configuration.

`@Binds` is an abstract method in `@Module` that tells the graph: when an interface/base type is requested, use this implementation. It fits cases where the implementation is already created through an `@Inject constructor`.

`@Binds` is usually preferable for interface -> implementation bindings: less code, less manual object creation, and it is clearer that this is just an alias binding.

`@Provides` can contain creation logic, but business logic should not be hidden there. A module should handle wiring, not application rules.

**In short:** `@Provides` creates an object manually, `@Binds` maps an abstraction to an existing injectable implementation.

### `@Module` / `@InstallIn`

`@Module` groups binding methods that explain to Dagger/Hilt how to provide dependencies when constructor injection is not enough.

In Hilt, `@InstallIn` specifies which Hilt component the module is installed into: for example `SingletonComponent`, `ActivityRetainedComponent`, `ViewModelComponent` or `ActivityComponent`. This determines where the binding is available and which scope can be used.

If a binding is needed by the whole app, the module is often installed into `SingletonComponent`. If a dependency is needed only by `ViewModel`, consider `ViewModelComponent` to avoid extending lifetime unnecessarily.

Common pitfalls: installing a module too high in the graph and accidentally making a screen-specific dependency application-wide; trying to inject `Activity Context` into a Singleton-scoped object.

**In short:** `@Module` defines bindings, `@InstallIn` chooses the Hilt component where those bindings live.

## Components and ViewModel

### Hilt components and scopes

Hilt components are generated Dagger components tied to the Android lifecycle. Main levels: `SingletonComponent` for application, `ActivityRetainedComponent` for state between configuration changes, `ViewModelComponent` for `ViewModel`, `ActivityComponent`, `FragmentComponent`, `ViewComponent` and `ServiceComponent`.

Scope limits an instance lifetime inside the corresponding component. For example, `@Singleton` lives in `SingletonComponent`, `@ActivityRetainedScoped` lives while the retained activity graph lives, `@ViewModelScoped` lives while a specific `ViewModel` lives, and `@ActivityScoped` lives while the `Activity` instance lives.

It is important to distinguish `ActivityRetainedComponent` and `ActivityComponent`: retained survives configuration change, while `ActivityComponent` belongs to a specific `Activity` instance after recreation.

Choose scope by owner lifecycle. An API client or database is usually application-wide, a stateless use case can be unscoped, and screen-specific state is better kept in ViewModel scope or directly in `ViewModel` state.

**In short:** Hilt scopes should match the Android lifecycle owner; scope is about correctness of lifetime, not just caching instances.

### ViewModel injection

In Hilt, `ViewModel` is usually annotated with `@HiltViewModel`, and dependencies are passed through an `@Inject constructor`. `Activity` or `Fragment` must be `@AndroidEntryPoint` to obtain the `ViewModel` through standard APIs.

```kotlin
@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel()
```

Hilt creates `ViewModel` through integration with `ViewModelProvider` and can provide dependencies from suitable components. For dependencies that should live as long as `ViewModel`, use `ViewModelComponent` and `@ViewModelScoped`.

If `ViewModel` needs a runtime argument, `SavedStateHandle` is usually used for navigation args/state, or assisted injection/factory if the parameter is not part of the standard saved state approach.

**Important:** `ViewModel` must not store `Activity`, `Fragment`, `View` or a regular UI `Context`. If `Context` is needed for resources/application-level API, inject `@ApplicationContext`, though often it is better to move this into a mapper/provider.

**In short:** Hilt injects `ViewModel` dependencies through `@HiltViewModel` and constructor injection; runtime screen arguments usually come from `SavedStateHandle`.
