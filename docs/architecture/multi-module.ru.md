# Multi-module Architecture

Multi-module architecture разделяет Android-проект на Gradle-модули с явными границами, зависимостями и ownership. Она полезна, когда проект достаточно большой и один application module становится сложно собирать, тестировать, поддерживать и развивать.

Цель не в том, чтобы создать как можно больше модулей. Цель - сделать границы модулей похожими на реальные продуктовые и технические ответственности.

## Какие проблемы решает multi-module architecture

Multi-module architecture помогает с build scalability, понятным code ownership, переиспользуемой shared logic и более строгими dependency boundaries. Feature часто можно собирать, тестировать, переписывать или мигрировать с меньшим влиянием на остальное приложение.

Она также помогает большим командам работать параллельно. Если у модулей стабильные public API, команды могут владеть features или shared capabilities без постоянных изменений в одних и тех же файлах.

Trade-off реальный: больше модулей означает больше Gradle configuration, больше coordination по dependencies, больше DI wiring, больше navigation contracts и больше решений о том, где должен жить код. Маленькому приложению может быть достаточно простой package structure внутри одного или нескольких модулей.

**Коротко:** multi-module architecture полезна, когда isolation, ownership и build scalability оправдывают Gradle-сложность и coordination cost.

## Layer-based modularization

Layer-based modularization отражает Clean Architecture layers на уровне Gradle-модулей:

```text
:app
:presentation
:domain
:data
```

Такая структура может выглядеть чисто, потому что направление зависимостей очевидно: UI зависит от domain contracts, data реализует repositories, а app module связывает всё вместе. Это может быть полезно для изучения Clean Architecture, разделения ответственности и независимого тестирования domain logic.

Ограничение в том, что продуктовые features часто размазываются по техническим buckets. Изменение в payments может требовать правок в `:presentation`, `:domain` и `:data` одновременно:

```text
:presentation  -> payments screen, ViewModel, UI state
:domain        -> payments use cases, entities, repository interface
:data          -> payments repository implementation, API, local cache
```

Для маленьких и средних проектов это может быть приемлемо. В больших product apps такие модули могут превратиться в крупные технические монолиты: каждая feature живёт в каждом слое, ownership неочевиден, а добавление feature затрагивает несколько широких modules.

Layer-based modules не бесполезны. Они помогают с dependency direction, testability и явными architecture boundaries. Проблема начинается, когда их механически применяют как главную стратегию modularization для всего приложения.

**Плюсы:**

- понятное направление зависимостей;
- легко объяснять Clean Architecture boundaries;
- полезно для маленьких и средних приложений;
- domain logic можно тестировать отдельно;
- технические ответственности хорошо видны.

**Минусы:**

- feature code размазан по модулям;
- ownership часто неочевиден;
- modules могут стать большими technical buckets;
- добавление feature может требовать правок во многих modules;
- reuse не появляется автоматически;
- это может стать тем же монолитом, разбитым на несколько технических частей.

## Feature-based modularization

Feature-based modularization группирует код по продуктовой функциональности:

```text
:app
:feature:profile
:feature:payments
:feature:offers
:feature:settings
:core:network
:core:database
:core:ui
```

Feature module владеет пользовательской capability или flow: profile, payments, checkout, offers, settings, onboarding. Это часто лучше совпадает с тем, как работают команды и как доставляются изменения.

Feature modules держат рядом связанные UI, state, feature-specific business logic и navigation entry points. Команда может менять или переписывать feature без размазывания работы по глобальным техническим modules.

Feature-based modularization не магия. Без внутренних правил feature module может стать mini-monolith. Shared logic может дублироваться, слишком рано переезжать в `core` или связываться через нестабильные contracts. Navigation и DI boundaries тоже становятся важнее.

**Плюсы:**

- feature code находится ближе друг к другу;
- ownership проще определить;
- features проще изолировать, удалить, переписать или мигрировать;
- большие приложения и несколько команд обычно масштабируются лучше;
- module boundaries ближе к product boundaries.

**Минусы:**

- feature modules могут стать mini-monoliths;
- shared logic может дублироваться или извлекаться слишком рано;
- нужны понятные dependency rules;
- navigation contracts и DI setup требуют больше внимания;
- cross-feature flows требуют явной координации.

## Pragmatic hybrid approach

Для многих реальных Android-проектов лучший default - hybrid structure: feature modules для продуктовых областей, core modules для технической инфраструктуры и shared modules только там, где reuse действительно есть.

```text
:app

:core:network
:core:database
:core:datetime
:core:ui
:core:analytics

:shared:user
:shared:payments
:shared:offers

:feature:profile
:feature:payments
:feature:checkout
:feature:settings
```

### `:app`

`:app` module - application entry point. Он отвечает за startup logic, root navigation, app-level DI wiring, global configuration и сборку features.

Он должен координировать приложение, а не содержать всю product logic.

### `:core`

`core` modules содержат переиспользуемую техническую инфраструктуру: network clients, database setup, logging, analytics, dispatchers, date/time, design system, common UI components и testing utilities.

Хорошие `core` modules маленькие и сфокусированные. Не стоит заводить расплывчатый `core:utils`, который превращается в dumping ground для несвязанных helpers.

### `:shared`

`shared` modules содержат reusable business или domain capabilities, которые используются несколькими features: user, payments, offers, permissions, subscriptions.

Их стоит создавать только при реальном reuse или стабильной boundary. Если код нужен только одной feature, обычно он должен оставаться внутри этой feature.

### `:feature`

Feature modules инкапсулируют продуктовую функциональность. Feature может содержать внутренние packages вроде `presentation`, `domain` и `data`:

```text
:feature:payments
  presentation/
  domain/
  data/
```

Так Clean Architecture separation остаётся там, где она полезна, но каждый слой не обязательно становится отдельным Gradle module.

Разделять внутренности feature на отдельные Gradle modules стоит только тогда, когда feature достаточно большая, переиспользуется независимо, имеет отдельный ownership или есть причина по build performance.

## Как принять решение

Используй отдельный Gradle module, когда:

- код переиспользуется несколькими features;
- boundary стабильна;
- команда может владеть этим модулем независимо;
- это улучшает build performance или isolation;
- это предотвращает нежелательные dependencies;
- код можно тестировать независимо;
- у модуля есть понятный public API.

Не стоит создавать отдельный Gradle module, когда:

- он только повторяет folder или package;
- он используется одной feature;
- он добавляет Gradle boilerplate без isolation;
- простые изменения начинают требовать правок во многих modules;
- boundary ещё нестабильна;
- module станет generic dumping ground.

**Практический подход:** multi-module architecture полезна, когда проект достаточно большой, чтобы получить выгоду от isolation, ownership и build scalability. Не стоит делить всё приложение только по Clean Architecture layers вроде `data`, `domain` и `presentation`, потому что это может размазать features по техническим modules. Для больших Android-приложений лучше начинать с feature-based structure, сфокусированных `core` technical modules и `shared` domain modules там, где reuse реальный. Внутри feature можно сохранить разделение `presentation`, `domain` и `data` как packages, а выносить их в Gradle modules только при практической необходимости.

## Dependency rules

Хороший module graph направленный и скучный. Низкоуровневые shared modules не должны зависеть от высокоуровневых feature modules. Feature modules не должны хаотично зависеть друг от друга. `:app` module часто связывает features через navigation, DI и app-level coordination.

Если появляется cycle, обычно boundary выбрана неверно. Нужно вынести общий contract в меньший module, инвертировать зависимость через interface или дать `:app` скоординировать взаимодействие.

Пример: если `:feature:profile` должна открыть `:feature:payments`, profile не должна зависеть от implementation payments напрямую. Route или navigation contract может жить в shared contract module, а `:app` выполнит actual navigation.

**Главная мысль:** feature-based modularization обычно лучше подходит как default direction для больших product apps, но layer separation всё равно важна. Часто ей место внутри features как packages, а отдельными Gradle modules она становится только тогда, когда reuse, ownership или build isolation оправдывают стоимость.
