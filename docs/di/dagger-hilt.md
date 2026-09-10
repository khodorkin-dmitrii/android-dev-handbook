# Dagger / Hilt

Hilt is an Android-focused dependency injection layer built on top of Dagger. It keeps Dagger's generated code and compile-time graph validation, while providing a standard component hierarchy tied to Android lifecycles.

## Hilt and Dagger

### What is Hilt?

Hilt standardizes how a Dagger graph is connected to an Android app:

- `@HiltAndroidApp` creates the application-level container.
- `@AndroidEntryPoint` enables injection into framework-created Android classes such as activities, fragments, services and receivers.
- `@HiltViewModel` integrates a `ViewModel` with `ViewModelProvider`.
- `@Inject` marks injectable constructors or fields.

For common Android applications, this removes the need to define an application component, Android subcomponents and their factories manually. It does not remove the underlying Dagger concepts: bindings, modules, qualifiers, scopes and dependency graph errors still matter.

### Hilt vs Dagger

Dagger is a general-purpose compile-time DI framework. It generates the code that creates objects and validates that every requested dependency has exactly one valid binding and that the graph has no dependency cycles.

Hilt is an opinionated Android integration built on Dagger. It supplies predefined components and connects them to Android lifecycle owners. Hilt is usually the practical default for a modern Android application. Pure Dagger remains useful in legacy graphs, non-Android code or architectures that require custom component ownership beyond Hilt's hierarchy.

## Bindings

### `@Inject`

Constructor injection is preferred for classes we own because dependencies are explicit and the object is easy to instantiate in tests:

```kotlin
class UserRepository @Inject constructor(
    private val api: ApiService,
    private val dao: UserDao,
)
```

If every constructor parameter has a binding, no separate provider is required. Keep creation dependencies in the constructor and pass changing operation data to methods instead of putting every runtime value into the DI graph.

Field injection is mainly for objects created by the Android framework. An injected field cannot be `private`, and it is unavailable before Hilt performs injection in the corresponding lifecycle callback. Regular application classes should normally use constructor injection.

### `@Provides` vs `@Binds`

Use `@Binds` to map an injectable implementation to an abstraction:

```kotlin
@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {
    @Binds
    abstract fun bindUserRepository(
        implementation: DefaultUserRepository,
    ): UserRepository
}
```

Use `@Provides` when construction requires code or the class cannot have an `@Inject` constructor, for example Retrofit, OkHttp, Room, DataStore or an external SDK:

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    @Provides
    @Singleton
    fun provideApi(client: OkHttpClient): ApiService =
        Retrofit.Builder()
            .baseUrl("https://example.com/")
            .client(client)
            .build()
            .create(ApiService::class.java)
}
```

Provider methods should contain object construction and wiring, not business rules. `@Binds` does not automatically make an instance singleton, and `@Provides` does not either: lifetime is controlled separately by a scope annotation.

### Qualifiers

When the graph contains several bindings of the same type, distinguish them with a qualifier. Prefer a domain-specific custom qualifier over relying on `@Named` strings, which are easier to mistype.

```kotlin
@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class AuthenticatedClient

@Provides
@AuthenticatedClient
fun provideAuthenticatedClient(
    authInterceptor: AuthInterceptor,
): OkHttpClient = OkHttpClient.Builder()
    .addInterceptor(authInterceptor)
    .build()
```

The same qualifier must be present at both the binding and injection site. Qualify all bindings of that type consistently to make selection explicit.

### `@Module` / `@InstallIn`

`@Module` groups bindings that cannot be expressed with constructor injection. `@InstallIn` selects the generated Hilt component that owns the bindings and determines where they are visible.

A binding installed in a parent component is available to its child components, but a child binding is not visible to its parent or siblings. Install a binding in the lowest component that covers all consumers. This avoids exposing a screen-specific dependency application-wide and prevents invalid dependencies such as an activity context inside a singleton object.

For types that Hilt already knows, use its predefined bindings and qualifiers, such as `@ApplicationContext` and `@ActivityContext`, instead of creating duplicate context providers.

## Components and ViewModel

### Hilt components and scopes

The most common component and scope pairs are:

| Component | Typical lifetime | Matching scope |
|---|---|---|
| `SingletonComponent` | Application process graph | `@Singleton` |
| `ActivityRetainedComponent` | Logical activity across configuration changes | `@ActivityRetainedScoped` |
| `ViewModelComponent` | One `ViewModel` | `@ViewModelScoped` |
| `ActivityComponent` | One activity instance | `@ActivityScoped` |
| `FragmentComponent` | One fragment instance | `@FragmentScoped` |
| `ServiceComponent` | One service instance | `@ServiceScoped` |

A scope means one instance per component instance, not one instance globally. Unscoped bindings may create a new object for each injection request. Scope only objects that require shared identity, own resources or are expensive to create. Stateless use cases and mappers often do not need a scope.

`ActivityRetainedComponent` survives configuration changes; `ActivityComponent` does not. Neither should be used to store UI state that belongs in a `ViewModel` or saved state.

### ViewModel injection

Annotate a ViewModel with `@HiltViewModel` and inject dependencies through its constructor:

```kotlin
@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val repository: UserRepository,
    savedStateHandle: SavedStateHandle,
) : ViewModel()
```

The hosting activity or fragment must be an `@AndroidEntryPoint`. In Compose, the composable itself is not annotated; obtain the ViewModel through the Hilt-aware ViewModel API under an appropriate navigation or activity owner.

Use `SavedStateHandle` for navigation arguments and restorable screen state. Use Hilt-assisted injection when a required runtime argument does not belong in saved state. Do not inject or store an `Activity`, `Fragment`, `View` or UI context in a ViewModel. If application-level access is unavoidable, use an abstraction or `@ApplicationContext` and keep UI work outside the ViewModel.

## Diagnosing graph errors

Hilt failures are usually compile-time graph errors. Read from the first missing or duplicate binding, then trace the dependency path shown by Dagger.

Common causes include:

- a constructor or module binding is missing;
- two bindings have the same type and no qualifier;
- the qualifier differs between provider and consumer;
- a binding is installed in a component that is not an ancestor of the consumer;
- a scoped binding depends on an object from a shorter-lived component;
- a Gradle module containing bindings is not in the application's transitive dependency graph.

## Related topics

- [DI Basics](basics.md)
- [Koin](koin.md)
- [Multi-module Architecture](../architecture/multi-module.md)
- [ViewModel Testing](../testing/viewmodel-testing.md)
