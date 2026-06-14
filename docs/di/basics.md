# DI Basics

Dependency Injection (DI) is an approach where a class does not create its dependencies itself, but receives them from the outside: through a constructor, factory, framework or composition root.

## DI Basics

### Why is DI needed?

DI is needed for loose coupling, testability and explicit dependency management. In Android this is especially useful because of layers, lifecycle, `ViewModel`, repositories, API clients, database, `DataStore`, analytics, dispatchers and feature flags.

Without DI, `ViewModel` may create repository itself, repository may create a Retrofit service, and the service may create an OkHttp client. This leads to tight coupling: dependencies are hard to replace, mock in tests and control by lifecycle.

Good DI makes dependencies visible through constructors/API, allows fake implementations in tests, centralizes wiring and helps follow the Dependency Inversion Principle.

**In short:** DI is not just about avoiding `new`; it reduces coupling, improves testability and gives controlled lifecycle for dependencies.

### Dependency Injection vs Service Locator

Dependency Injection means a dependency is passed into an object from the outside. The class explicitly declares what it needs, usually through constructor parameters, while the composition root or DI container creates the object graph.

Service Locator is a registry object from which a class requests a dependency itself, for example `ServiceLocator.getRepository()`. This is simpler for a small project, but the dependency becomes less explicit.

The main difference: with DI, dependencies are visible in the class API; with Service Locator, the class secretly knows about a global registry. This complicates testing, reasoning and finding real dependencies.

Service Locator is not always bad: it can be a temporary solution in legacy code or manual DI. But in large Android projects, explicit DI through constructor injection and Hilt/Dagger is usually better.

**In short:** DI pushes dependencies into a class, Service Locator lets the class pull them from a registry; DI is usually more explicit and testable.

### Constructor injection

Constructor injection is a DI style where all required dependencies are passed through the constructor.

This is the preferred default: the object cannot be created without required dependencies, dependencies are explicit, they are easy to replace in unit tests, and the class does not depend on a specific DI framework inside its logic.

In Android with Hilt/Dagger, constructor injection often looks like this:

```kotlin
class UserRepository @Inject constructor(
    private val api: ApiService,
    private val dao: UserDao
)
```

If the class belongs to us and can be created through the constructor, a separate `@Provides` method is usually not needed.

Constructor injection is less suitable when the object is created directly by the Android framework, needs a runtime parameter, uses a builder/factory or comes from an external SDK. In those cases use assisted injection, factory, provider method or module.

**In short:** constructor injection is the default choice because it makes required dependencies explicit and keeps classes easy to test.

### Scope in DI

Scope in DI defines a dependency lifetime and the boundaries for reusing one instance inside the object graph.

Without a scope, a dependency is usually created each time it is needed. A scoped dependency is reused inside its component/lifecycle: for example, an application-level singleton, a `ViewModel`-scoped object or an `Activity`-scoped object.

Choose scope based on the real owner of state. A stateless API client or database can usually be application-scoped, while an object with screen-specific state should live closer to `ViewModel` or feature scope.

An incorrect scope can lead to memory leak, stale state or unexpected shared mutable state. For example, an `Activity Context` must not be stored in a Singleton-scoped object.

**In short:** scope is about object lifetime; good DI is not "make everything singleton", but matching dependency lifetime to the owner lifecycle.

### Why not make everything singleton?

Making everything singleton is a bad default because singleton extends an object's lifetime to the whole application and can accidentally retain state, `Context`, callbacks or heavy resources longer than needed.

Singleton is convenient for stateless/shared infrastructure: Retrofit/OkHttp clients, database, `DataStore`, analytics, configuration providers. But screen-specific state, user flow state, temporary caches and objects with lifecycle-sensitive references should not live application-wide without a reason.

Excessive singletons increase coupling, complicate tests, create hidden global state and can cause bugs across sessions, users or features.

A good approach is scoped dependencies as needed: singleton only for truly application-wide objects, shorter scopes for lifecycle-specific logic, and transient objects left unscoped.

**In short:** singleton is a lifecycle decision, not a default optimization; use it only when one application-wide instance is actually correct.
