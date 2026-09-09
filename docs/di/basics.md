# DI Basics

Dependency Injection (DI) is a design technique in which an object receives its dependencies from the outside instead of creating or locating them itself. DI can be implemented manually or with a framework such as Hilt, Dagger or Koin.

## Why use DI?

DI makes dependencies explicit, reduces coupling and improves testability. In Android, an object may depend on repositories, API clients, databases, `DataStore`, analytics, dispatchers or feature flags. If every class constructs the next one, creation logic spreads through the codebase and implementations become difficult to replace.

With DI, classes describe what they need while object creation moves to a **composition root** - the place where the application assembles the object graph. This can be a manual container or a DI framework.

DI does not guarantee good architecture. Too many constructor parameters may still indicate too many responsibilities, and an interface is useful only when it represents a meaningful boundary or variation.

## Constructor injection

Constructor injection is the preferred default for classes the application owns:

```kotlin
class UserRepository(
    private val api: ApiService,
    private val dao: UserDao,
    private val ioDispatcher: CoroutineDispatcher
)
```

Dependencies are visible, the object cannot be created in an invalid state, and tests can pass fakes directly:

```kotlin
val repository = UserRepository(
    api = FakeApiService(),
    dao = FakeUserDao(),
    ioDispatcher = StandardTestDispatcher(testScheduler)
)
```

With Hilt or Dagger, `@Inject constructor` tells the framework how to create the class. A provider is needed for cases such as third-party types, builders or custom setup.

Android creates classes such as `Activity` and `Service`, so their injection entry points require framework integration. Runtime values, such as a selected document ID, are data rather than graph dependencies; pass them through navigation state, a method or an assisted factory.

## Manual DI and containers

DI does not require a library. A simple container can create shared infrastructure and expose factories for shorter-lived objects:

```kotlin
class AppContainer {
    private val api = createApiService()
    private val database = createDatabase()

    val userRepository = UserRepository(
        api = api,
        dao = database.userDao(),
        ioDispatcher = Dispatchers.IO
    )
}
```

Manual DI is transparent and suits small graphs. As the graph grows, factories, scopes and Android lifecycle integration create more wiring; frameworks reduce that boilerplate and can validate the graph.

## DI vs Service Locator

With DI, dependencies are supplied to a class and appear in its API. With Service Locator, the class requests them from a registry:

```kotlin
class UserRepository {
    private val api = ServiceLocator.apiService
}
```

The locator hides dependencies, couples business code to global infrastructure and makes isolated tests harder. A registry can be pragmatic at a legacy boundary or inside a composition root, but feature classes should generally not call it directly.

## Scopes and object lifetime

An unscoped binding usually creates a new instance for each request. A scoped binding reuses one instance within a particular container or component. The component's lifetime therefore limits how long that instance can be shared.

Choose a scope according to ownership and required identity:

| Dependency | Typical lifetime |
| --- | --- |
| Database, configured HTTP client | Application |
| Stateful object shared across one user flow | Flow or retained activity |
| Object shared inside one `ViewModel` graph | `ViewModel` |
| Stateless mapper or use case | Often unscoped |

Scope an object when consumers must share state or a resource, synchronization requires one instance, or measured creation cost matters.

## Why not make everything a singleton?

A singleton lives for the application graph and shares one instance across unrelated consumers. This is appropriate for truly application-wide infrastructure, but it is risky for mutable screen state, temporary caches, callbacks and lifecycle-sensitive references.

An application-scoped object must not retain an `Activity`, `Fragment` or `View`. If it needs a `Context`, prefer the application context. Excessive singletons can also couple tests and preserve stale state between users or flows.

The practical default is constructor injection plus unscoped objects. Add the narrowest scope that matches a real sharing requirement.

## Related topics

- [Dagger / Hilt](dagger-hilt.md)
- [Koin](koin.md)
- [Testing Strategy](../testing/strategy.md)
- [Architecture Basics](../architecture/basics.md)
