# Koin

Koin - Kotlin-first DI framework, который часто используют в Android-проектах. Он описывает modules и dependencies через Kotlin DSL, без такого annotation-heavy setup, как в Dagger/Hilt.

Koin хорошо подходит для небольших и средних Android-приложений, prototypes, pet projects и команд, которым важна простая конфигурация. Он также актуален для Kotlin Multiplatform-oriented architecture, хотя здесь основной фокус остаётся на Android.

## Основы Koin

```kotlin
val appModule = module {
    single { ApiService(get()) }
    single { UserRepository(get()) }
    viewModel { UserViewModel(get()) }
}
```

`module {}` группирует dependency definitions. `single {}` создаёт application-level singleton. `factory {}` создаёт новый instance при каждом запросе. `viewModel {}` интегрируется с созданием Android `ViewModel`. `get()` резолвит другую dependency из Koin container.

Обычно Koin запускают из `Application`:

```kotlin
startKoin {
    modules(appModule)
}
```

## Koin vs Hilt

| Тема | Hilt | Koin |
| --- | --- | --- |
| Стиль конфигурации | Аннотации и сгенерированный Dagger code | Kotlin DSL modules |
| Compile-time vs runtime behavior | Compile-time graph generation и validation | Runtime dependency resolution |
| Boilerplate | Больше setup-концепций, меньше manual Dagger wiring | Обычно меньше настройки и очень читаемые modules |
| Android integration | Сильная стандартная интеграция с Android lifecycle components | Android integrations для `ViewModel`, scopes и типичного app setup |
| Error detection | Многие проблемы graph-а падают на этапе build | Ошибки в modules чаще проявляются в runtime |
| Refactoring safety | Выше, потому что generated code и compile-time checks ловят много ошибок | Хорошая читаемость, но нужны дисциплина и тесты |
| Learning curve | Больше понятий: components, scopes, modules, qualifiers | Проще начать, если команда знает Kotlin |
| Best fit | Большие, сложные, long-lived production Android apps | Небольшие и средние apps, prototypes и KMP-friendly codebases |

Hilt построен поверх Dagger и обычно остаётся default recommendation для больших production Android-приложений, потому что даёт более сильные compile-time guarantees. Koin - валидная modern alternative, когда важны простота, быстрый setup, Kotlin DSL или Kotlin Multiplatform-friendly architecture.

В modern Koin есть tools и features, которые улучшают module validation, но базовый trade-off остаётся тем же: Koin проще и динамичнее, а Hilt строже и безопаснее для больших dependency graphs.

## Практическая рекомендация

### Когда использовать Koin

Используйте Koin, когда проект небольшой или средний, команда хочет DI без тяжёлого annotation processing или code generation setup, либо codebase ориентирован на Kotlin Multiplatform.

Koin также хорошо подходит для pet projects, prototypes и приложений, где runtime DI trade-offs приемлемы, а читаемая Kotlin-конфигурация важнее строгой compile-time graph validation.

### Когда Hilt обычно лучше

Hilt обычно лучше для больших production Android-приложений со сложным dependency graph, множеством modules и большим количеством developers.

Выбирайте Hilt, когда важна сильная compile-time validation или команда уже использует Google-recommended Android architecture stack.
