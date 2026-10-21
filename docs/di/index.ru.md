# DI

Раздел охватывает dependency injection в Android: владение зависимостями, composition root, constructor injection, scopes, проверку графа, тестирование и компромиссы DI-фреймворков.

Практический порядок изучения: начните с принципов DI и ручной сборки зависимостей. Затем разберите Dagger и Hilt, чтобы понять compile-time графы и время жизни Android-компонентов, после чего сравните их с runtime DSL в Koin. Статья про legacy DI пригодится при поддержке старого проекта или планировании постепенной миграции.

## Основы

- [DI Basics](basics.md) - зависимости, composition root, constructor injection, runtime values, scopes, компромиссы Service Locator и риски времени жизни singleton.

## DI-фреймворки для Android

- [Dagger / Hilt](dagger-hilt.md) - compile-time графы, constructor- и module-bindings, qualifiers, видимость компонентов, scopes и интеграция с ViewModel.
- [Koin](koin.md) - runtime definitions, constructor DSL, qualifiers, параметры, lifecycle-aware scopes, валидация и изоляция тестов.

## Legacy-проекты и миграция

- [Legacy DI](legacy-di.md) - старые версии Dagger, Toothpick, lifecycle-риски Moxy, владение scopes, проверки перед миграцией и безопасная замена компонентов.
