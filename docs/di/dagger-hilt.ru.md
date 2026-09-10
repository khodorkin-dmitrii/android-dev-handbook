# Dagger / Hilt

Hilt - слой внедрения зависимостей для Android, построенный поверх Dagger. Он сохраняет генерацию кода и проверку графа на этапе компиляции, но предоставляет стандартную иерархию компонентов, связанную с жизненным циклом Android.

## Hilt и Dagger

### Что такое Hilt?

Hilt стандартизирует подключение графа Dagger к Android-приложению:

- `@HiltAndroidApp` создаёт контейнер уровня приложения.
- `@AndroidEntryPoint` включает внедрение зависимостей в создаваемые системой классы Android, например activity, fragment, service и receiver.
- `@HiltViewModel` интегрирует `ViewModel` с `ViewModelProvider`.
- `@Inject` отмечает конструкторы или поля для внедрения зависимостей.

В типичном Android-приложении больше не нужно вручную описывать компонент приложения, Android-подкомпоненты и их фабрики. При этом базовые понятия Dagger остаются важными: bindings, modules, qualifiers, scopes и ошибки графа зависимостей.

### Hilt и Dagger

Dagger - универсальный DI-фреймворк, работающий на этапе компиляции. Он генерирует код создания объектов и проверяет, что для каждой запрошенной зависимости существует ровно один подходящий binding, а в графе нет циклов.

Hilt - специализированная Android-интеграция поверх Dagger. Он предоставляет готовые компоненты и связывает их с владельцами жизненного цикла Android. Для современного Android-приложения Hilt обычно является практичным выбором по умолчанию. Чистый Dagger остаётся полезен для legacy-графов, не-Android кода и архитектур, которым нужен нестандартный контроль над компонентами.

## Bindings

### `@Inject`

Для собственных классов предпочтительно внедрение через конструктор: зависимости видны явно, а объект легко создать в тесте.

```kotlin
class UserRepository @Inject constructor(
    private val api: ApiService,
    private val dao: UserDao,
)
```

Если для каждого параметра конструктора есть binding, отдельный provider не требуется. В конструктор стоит передавать зависимости создания, а изменяющиеся данные конкретной операции - в методы, не добавляя каждое runtime-значение в DI-граф.

Внедрение через поля в основном нужно для объектов, которые создаёт Android framework. Такое поле не может быть `private` и недоступно до момента, когда Hilt выполнит injection в соответствующем lifecycle callback. Обычным классам приложения лучше использовать конструктор.

### `@Provides` и `@Binds`

Используйте `@Binds`, чтобы связать injectable-реализацию с абстракцией:

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

Используйте `@Provides`, когда для создания нужен код или у класса не может быть `@Inject`-конструктора, например для Retrofit, OkHttp, Room, DataStore или внешнего SDK:

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

Provider-методы должны содержать создание и связывание объектов, а не бизнес-правила. Ни `@Binds`, ни `@Provides` сами по себе не делают объект singleton: временем жизни управляет отдельная scope-аннотация.

### Qualifiers

Если в графе есть несколько bindings одного типа, различайте их с помощью qualifier. Обычно собственная аннотация с предметным названием безопаснее, чем строковый `@Named`, в котором легко допустить опечатку.

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

Одинаковый qualifier должен стоять и на binding, и в месте injection. Лучше последовательно отмечать им все bindings данного типа, чтобы выбор был явным.

### `@Module` / `@InstallIn`

`@Module` объединяет bindings, которые нельзя выразить через constructor injection. `@InstallIn` выбирает сгенерированный компонент Hilt, которому они принадлежат, и определяет область их видимости.

Binding родительского компонента доступен дочерним компонентам, но binding дочернего компонента недоступен родителю и соседним компонентам. Устанавливайте binding в самый нижний компонент, охватывающий всех потребителей. Так screen-specific зависимость не станет доступна всему приложению, а объект со scope приложения не получит недопустимый activity context.

Для известных Hilt типов используйте готовые bindings и qualifiers, например `@ApplicationContext` и `@ActivityContext`, вместо дублирующих context providers.

## Компоненты и ViewModel

### Компоненты и scopes Hilt

Основные пары компонентов и scopes:

| Компонент | Типичное время жизни | Соответствующий scope |
|---|---|---|
| `SingletonComponent` | Граф процесса приложения | `@Singleton` |
| `ActivityRetainedComponent` | Логическая activity между изменениями конфигурации | `@ActivityRetainedScoped` |
| `ViewModelComponent` | Одна `ViewModel` | `@ViewModelScoped` |
| `ActivityComponent` | Один экземпляр activity | `@ActivityScoped` |
| `FragmentComponent` | Один экземпляр fragment | `@FragmentScoped` |
| `ServiceComponent` | Один экземпляр service | `@ServiceScoped` |

Scope означает один экземпляр на один экземпляр компонента, а не обязательно один объект на всё приложение. Для unscoped binding новый объект может создаваться при каждом запросе. Scope нужен объектам с общей идентичностью, собственными ресурсами или дорогим созданием. Stateless use cases и mappers часто можно оставить без scope.

`ActivityRetainedComponent` переживает изменение конфигурации, а `ActivityComponent` - нет. Ни один из них не следует использовать для UI state, который должен храниться во `ViewModel` или saved state.

### Внедрение в ViewModel

Отметьте ViewModel аннотацией `@HiltViewModel`, а зависимости передайте через конструктор:

```kotlin
@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val repository: UserRepository,
    savedStateHandle: SavedStateHandle,
) : ViewModel()
```

Activity или fragment, которым принадлежит ViewModel, должны быть отмечены `@AndroidEntryPoint`. В Compose аннотация на composable не ставится: ViewModel получают через Hilt-aware API с подходящим владельцем из activity или navigation.

Используйте `SavedStateHandle` для navigation arguments и восстанавливаемого состояния экрана. Если обязательный runtime-аргумент не относится к saved state, применяйте assisted injection Hilt. ViewModel не должна получать или хранить `Activity`, `Fragment`, `View` либо UI context. Если доступ уровня приложения действительно необходим, используйте абстракцию или `@ApplicationContext`, оставляя UI-работу за пределами ViewModel.

## Диагностика ошибок графа

Большинство ошибок Hilt обнаруживается на этапе компиляции. Начните с первого сообщения об отсутствующем или дублирующемся binding, затем проследите показанную Dagger цепочку зависимостей.

Частые причины:

- отсутствует constructor или module binding;
- для одного типа есть два bindings без qualifier;
- qualifier у provider и consumer не совпадает;
- binding установлен в компонент, который не является предком consumer;
- scoped binding зависит от объекта из более короткоживущего компонента;
- Gradle-модуль с bindings не входит в транзитивные зависимости приложения.

## Связанные темы

- [Основы DI](basics.md)
- [Koin](koin.md)
- [Многомодульная архитектура](../architecture/multi-module.md)
- [Тестирование ViewModel](../testing/viewmodel-testing.md)
