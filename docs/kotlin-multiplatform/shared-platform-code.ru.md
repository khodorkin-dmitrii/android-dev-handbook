# Общий и платформенный код

KMP допускает несколько полезных границ переиспользования. Это варианты, а не ступени зрелости. Гибридный продукт не является неудачной попыткой переиспользовать всё.

| Стратегия | Общее | Платформенное | Типичный сценарий |
| --- | --- | --- | --- |
| Shared core | Модели, форматирование, алгоритмы | Большая часть приложения | Библиотеки, эксперименты, первое внедрение KMP |
| Shared data | API, сериализация, database logic, repositories | Presentation и UI | Постепенное внедрение |
| Shared data + domain | Data, repositories, бизнес-правила, use cases | ViewModels и UI | Независимые native presentation-команды |
| Shared presentation | Data, domain, state holders, UI state | Нативный UI и навигация | Одинаковое поведение при нативном UI |
| Shared UI | Большая часть приложения и Compose UI | Entry points и интеграции | Небольшие cross-platform команды и близкие продукты |
| Hybrid | Отдельные features, слои или UI-компоненты | Всё остальное | Зрелые продукты с разными требованиями платформ |

## Граница по ответственности

### Data sources и repositories

Поведение HTTP client, сериализация, DTO, SQL-запросы, cache policy, pagination, retry и синхронизация часто хорошо переносятся в общий код. Database drivers или factories, пути файловой системы, secure storage, наблюдение за сетью, background work и push notifications обычно требуют платформенных adapters. Точная граница зависит от поддержки targets библиотеками и требований продукта.

Repositories особенно полезно переиспользовать, когда они задают single source of truth, координируют remote и local data, реализуют offline-first и freshness policies, а также преобразуют DTO, database- и domain-модели. Так платформы разделяют бизнес-поведение, а не только transport code.

### Domain и presentation

Domain models, валидация, фильтрация, сортировка и реальные бизнес-правила обычно переносимы. Use cases должны представлять значимые операции или orchestration. Не нужно оборачивать каждый метод repository только ради формальной схемы слоёв.

В presentation можно переиспользовать immutable `UiState`, actions, state holders или ViewModels, а также поведение loading, error, offline, retry и recovery через `StateFlow`. Сложными границами остаются lifecycle ownership, saved state, navigation, permissions, соглашения SwiftUI и Compose и Kotlin/Swift interoperability.

UI может оставаться Jetpack Compose плюс SwiftUI, использовать общие экраны Compose Multiplatform, переиспользовать отдельные компоненты или разделять Compose UI только между Android и Desktop при нативном SwiftUI на iOS.

## Interfaces и `expect`/`actual`

Для поведения и заменяемых зависимостей - storage, connectivity, clock, analytics, external links и platform services - удобны interfaces с внедряемыми реализациями:

```kotlin
interface ExternalLinks {
    fun open(url: String)
}

class HelpPresenter(private val links: ExternalLinks) {
    fun openHelp() = links.open("https://example.com/help")
}
```

`expect`/`actual` подходит для узкого bridge, когда API имеет одинаковый смысл, но разную реализацию:

```kotlin
// commonMain
expect fun platformName(): String

// androidMain
actual fun platformName(): String = "Android"
```

Expected и actual classes сейчас имеют статус Beta. Functions и properties всё равно могут быть полезным узким bridge, но interfaces проще заменять, подделывать в тестах и реализовывать несколько раз на одной платформе.

**Практическое правило:** предпочитайте interfaces для поведения и зависимостей. Используйте `expect`/`actual` как узкий bridge к platform API, а не как замену архитектурным абстракциям.

См. [Структура проекта и Source Sets](project-structure.md) и [Архитектура и стратегии UI](architecture-ui.md).

## Источники

- [Expected и actual declarations](https://kotlinlang.org/docs/multiplatform/multiplatform-expect-actual.html)
