# DI Basics

Dependency Injection (DI) - подход, при котором класс не создаёт свои dependencies сам, а получает их извне: через constructor, factory, framework или composition root.

## Основы DI

### Зачем нужен DI?

DI нужен для слабой связности, тестируемости и явного управления зависимостями. В Android это особенно полезно из-за слоёв, lifecycle, `ViewModel`, repositories, API clients, database, `DataStore`, analytics, dispatchers и feature flags.

Без DI `ViewModel` может сама создавать repository, repository - Retrofit service, а service - OkHttp client. Это приводит к tight coupling: зависимости сложно заменить, мокнуть в тестах и контролировать по lifecycle.

Хороший DI делает dependencies видимыми через constructor/API, позволяет подставить fake implementation в тестах, централизует wiring и помогает соблюдать Dependency Inversion Principle.

**Коротко:** DI is not just about avoiding `new`; it reduces coupling, improves testability and gives controlled lifecycle for dependencies.

### Dependency Injection vs Service Locator

Dependency Injection означает, что dependency передаётся объекту извне. Класс явно объявляет, что ему нужно, обычно через constructor parameters, а composition root или DI container создаёт object graph.

Service Locator - объект-реестр, из которого класс сам запрашивает dependency: например, `ServiceLocator.getRepository()`. Это проще для маленького проекта, но dependency становится менее явной.

Главная разница: при DI зависимости видны в API класса, а при Service Locator класс скрыто знает о глобальном registry. Это усложняет тестирование, reasoning и поиск реальных зависимостей.

Service Locator не всегда зло: он может быть временным решением в legacy-коде или manual DI. Но в больших Android-проектах обычно лучше явный DI через constructor injection и Hilt/Dagger.

**Коротко:** DI pushes dependencies into a class, Service Locator lets the class pull them from a registry; DI is usually more explicit and testable.

### Constructor injection

Constructor injection - способ DI, при котором все обязательные dependencies передаются через constructor.

Это предпочтительный вариант по умолчанию: объект нельзя создать без нужных dependencies, зависимости явно видны, их легко заменить в unit tests, а класс не зависит от конкретного DI framework внутри своей logic.

В Android через Hilt/Dagger constructor injection часто выглядит так:

```kotlin
class UserRepository @Inject constructor(
    private val api: ApiService,
    private val dao: UserDao
)
```

Если класс принадлежит нам и его можно создать через constructor, обычно не нужен отдельный `@Provides` method.

Constructor injection хуже подходит, когда объект создаётся Android framework-ом напрямую, нужен runtime parameter, builder/factory или external SDK. Тогда используют assisted injection, factory, provider method или module.

**Коротко:** constructor injection is the default choice because it makes required dependencies explicit and keeps classes easy to test.

### Scope в DI

Scope в DI определяет lifetime зависимости и границы переиспользования одного instance внутри object graph.

Без scope dependency обычно создаётся каждый раз, когда она нужна. Scoped dependency переиспользуется внутри своего компонента/lifecycle: например, application-level singleton, `ViewModel`-scoped object или `Activity`-scoped object.

Scope нужно выбирать по реальному владельцу состояния. Stateless API client или database обычно может быть application-scoped, а объект с screen-specific state лучше держать ближе к `ViewModel` или feature scope.

Неправильный scope может привести к memory leak, stale state или неожиданному shared mutable state. Например, нельзя хранить `Activity Context` в Singleton-scoped объекте.

**Коротко:** scope is about object lifetime; good DI is not "make everything singleton", but matching dependency lifetime to the owner lifecycle.

### Почему не стоит делать всё singleton?

Делать всё singleton не стоит, потому что singleton расширяет lifetime объекта до всего приложения и может случайно удерживать state, `Context`, callbacks или heavy resources дольше, чем нужно.

Singleton удобен для stateless/shared infrastructure: Retrofit/OkHttp clients, database, `DataStore`, analytics, configuration providers. Но screen-specific state, user flow state, temporary caches и objects with lifecycle-sensitive references не должны жить application-wide без причины.

Избыточные singleton-ы увеличивают связанность, усложняют тесты, создают hidden global state и могут приводить к bugs между сессиями, пользователями или features.

Хороший подход - scoped dependencies по необходимости: singleton только для truly application-wide объектов, shorter scopes для lifecycle-specific logic, а transient objects оставлять unscoped.

**Коротко:** singleton is a lifecycle decision, not a default optimization; use it only when one application-wide instance is actually correct.
