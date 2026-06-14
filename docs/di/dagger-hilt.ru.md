# Dagger / Hilt

Hilt - Android-focused DI layer поверх Dagger. Он уменьшает boilerplate, задаёт стандартную иерархию components и связывает DI graph с Android lifecycle.

## Hilt и Dagger

### Что такое Hilt?

Hilt - DI framework для Android, построенный поверх Dagger. Он упрощает интеграцию dependency injection в Android-приложение и даёт готовые entry points, components и scopes для Android lifecycle.

Обычно Hilt подключают через `@HiltAndroidApp` на `Application`, `@AndroidEntryPoint` на `Activity` / `Fragment` / `Service` / `Receiver`, `@HiltViewModel` для `ViewModel` и constructor injection через `@Inject`.

Главная польза Hilt - меньше manual Dagger boilerplate: не нужно вручную описывать `AppComponent`, subcomponents, component factories и Android-specific wiring для большинства стандартных случаев.

Но Hilt не отменяет понимание Dagger: всё равно важно понимать object graph, bindings, modules, scopes, qualifiers и compile-time errors.

**Коротко:** Hilt is the recommended Android DI layer on top of Dagger; it reduces Android boilerplate while keeping Dagger's compile-time graph validation.

### Hilt vs Dagger

Dagger - general-purpose compile-time DI framework. Он генерирует код для dependency graph и проверяет bindings на этапе компиляции.

Hilt - opinionated Android integration поверх Dagger. Он заранее задаёт стандартную иерархию components, связывает её с Android lifecycle и даёт удобные аннотации для Android entry points.

На чистом Dagger у команды больше гибкости: можно полностью контролировать components, scopes, factories и multi-module setup. Но за это приходится платить boilerplate и более сложной настройкой.

Hilt обычно лучше для modern Android приложений, где нужны стандартные Application/Activity/Fragment/ViewModel scopes и меньше ручного wiring. Чистый Dagger может быть полезен в legacy, non-Android modules или сложной custom graph architecture.

**Коротко:** Dagger is the underlying DI engine, Hilt is the Android-focused layer that standardizes components and removes much of the setup boilerplate.

## Bindings

### `@Inject`

`@Inject` используется в двух основных местах: на constructor, чтобы Dagger/Hilt мог создать объект, и на fields/methods, чтобы выполнить injection в объект, который создаёт не DI container.

Constructor injection - preferred вариант для классов, которыми мы владеем: repositories, use cases, mappers, managers, validators.

```kotlin
class UserRepository @Inject constructor(
    private val api: ApiService,
    private val dao: UserDao
)
```

Если у класса есть `@Inject constructor` и все его dependencies известны graph-у, отдельный `@Provides` method обычно не нужен.

Field injection в Android чаще нужен для framework-created classes вроде `Activity`, `Fragment`, `Service` или `BroadcastReceiver` после `@AndroidEntryPoint`. Для обычных классов лучше constructor injection, потому что зависимости видны и объект проще тестировать.

**Коротко:** use `@Inject constructor` for classes you own; field injection is mostly for Android classes created by the framework.

### `@Provides` vs `@Binds`

`@Provides` - method в `@Module`, который вручную создаёт dependency. Он нужен, когда объект нельзя создать через `@Inject constructor`: external SDK, Retrofit, OkHttp, Room database, `DataStore`, builder/factory API, runtime configuration.

`@Binds` - abstract method в `@Module`, который говорит graph-у: когда нужен interface/base type, используй эту implementation. Он подходит, когда implementation уже создаётся через `@Inject constructor`.

`@Binds` обычно предпочтительнее для связывания interface -> implementation: меньше кода, меньше ручного создания объектов и лучше видно, что это просто alias binding.

`@Provides` может содержать logic создания, но не стоит прятать туда business logic. Module должен заниматься wiring, а не правилами приложения.

**Коротко:** `@Provides` creates an object manually, `@Binds` maps an abstraction to an existing injectable implementation.

### `@Module` / `@InstallIn`

`@Module` группирует binding methods, которые объясняют Dagger/Hilt, как предоставлять зависимости, если constructor injection недостаточно.

В Hilt `@InstallIn` указывает, в какой Hilt component устанавливается module: например `SingletonComponent`, `ActivityRetainedComponent`, `ViewModelComponent` или `ActivityComponent`. От этого зависит, где binding доступен и какой scope можно использовать.

Если binding нужен всему приложению, module часто ставят в `SingletonComponent`. Если dependency нужна только `ViewModel`, лучше рассмотреть `ViewModelComponent`, чтобы не расширять lifetime без необходимости.

Частые pitfalls: установить module слишком высоко в graph и случайно сделать screen-specific зависимость application-wide; пытаться инжектить `Activity Context` в Singleton-scoped object.

**Коротко:** `@Module` defines bindings, `@InstallIn` chooses the Hilt component where those bindings live.

## Components и ViewModel

### Hilt components and scopes

Hilt components - сгенерированные Dagger components, привязанные к Android lifecycle. Основные уровни: `SingletonComponent` для application, `ActivityRetainedComponent` для состояния между configuration changes, `ViewModelComponent` для `ViewModel`, `ActivityComponent`, `FragmentComponent`, `ViewComponent` и `ServiceComponent`.

Scope ограничивает lifetime instance внутри соответствующего component. Например, `@Singleton` живёт в `SingletonComponent`, `@ActivityRetainedScoped` - пока живёт retained activity graph, `@ViewModelScoped` - пока живёт конкретная `ViewModel`, `@ActivityScoped` - пока живёт `Activity` instance.

Важно различать `ActivityRetainedComponent` и `ActivityComponent`: retained переживает configuration change, а `ActivityComponent` относится к конкретному instance `Activity` после recreation.

Хороший scope выбирают по owner lifecycle. API client или database обычно application-wide, use case без state может быть unscoped, а screen-specific state лучше держать в ViewModel scope или вообще во `ViewModel` state.

**Коротко:** Hilt scopes should match the Android lifecycle owner; scope is about correctness of lifetime, not just caching instances.

### ViewModel injection

В Hilt `ViewModel` обычно помечают `@HiltViewModel`, а dependencies передают через `@Inject constructor`. `Activity` или `Fragment` должны быть `@AndroidEntryPoint`, чтобы получить `ViewModel` через стандартные APIs.

```kotlin
@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel()
```

Hilt создаёт `ViewModel` через интеграцию с `ViewModelProvider` и может предоставить dependencies из подходящих components. Для dependencies, которые должны жить столько же, сколько `ViewModel`, можно использовать `ViewModelComponent` и `@ViewModelScoped`.

Если `ViewModel` нужен runtime argument, обычно используют `SavedStateHandle` для navigation args/state или assisted injection/factory, если параметр не является частью стандартного saved state подхода.

**Важно:** `ViewModel` не должна хранить `Activity`, `Fragment`, `View` или обычный UI `Context`. Если нужен `Context` для resources/application-level API, инжектят `@ApplicationContext`, но часто лучше вынести это в mapper/provider.

**Коротко:** Hilt injects `ViewModel` dependencies through `@HiltViewModel` and constructor injection; runtime screen arguments usually come from `SavedStateHandle`.
