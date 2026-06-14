# Architecture Basics

Modern Android architecture - прагматичный подход к разделению ответственности между UI, state holder, domain logic и data sources.

## Layers

### Modern Android architecture

Modern Android architecture - это layered architecture, где приложение разделено на UI layer, data layer и optional domain layer.

Главная идея - separation of concerns: `Activity`, `Fragment` и composable не должны содержать всю логику приложения, а каждый слой должен иметь понятную ответственность и границы.

В modern Android обычно используют `ViewModel` как state holder, immutable UI state, unidirectional data flow, repositories, coroutines/Flow и dependency injection.

**Коротко:** modern Android architecture is usually a pragmatic layered architecture with clear responsibilities: UI renders state, `ViewModel` produces UI state, repositories hide data sources, and domain/use cases are added when they reduce complexity.

### UI layer / domain layer / data layer

UI layer отвечает за отображение application data и обработку user interaction. В Android это обычно composable, `Fragment`, `Activity`, `ViewModel`, UI state, UI events и UI-specific formatting.

Data layer отвечает за application data и business logic, связанный с созданием, хранением и изменением данных. Обычно включает repositories, remote/local data sources, API services, Room/DataStore/cache, DTO/entity models и mappers.

Domain layer - optional слой между UI и data. Он содержит use cases/interactors, business rules, validation и orchestration сценариев, когда логика сложная или переиспользуется несколькими `ViewModel`.

Хорошее разделение слоёв означает, что UI не знает деталей API/database, data layer не зависит от Android UI, а бизнес-правила не размазаны по composable или `Activity`.

**Коротко:** UI layer shows state and sends user actions, data layer owns data and repositories, domain layer is optional and contains reusable business logic.

### Clean Architecture

Clean Architecture - подход к разделению ответственности, где UI, бизнес-логика и работа с данными отделены друг от друга, а зависимости направлены к более стабильным абстракциям.

В Android это часто выглядит как UI layer -> `ViewModel` -> use case/domain -> repository -> data sources. Но Clean Architecture не обязана означать одинаковый набор папок и use case на каждое действие.

Польза: код проще тестировать, бизнес-логику легче переиспользовать, data sources можно заменить без переписывания UI, а большие классы проще разделять.

Trade-off: слишком строгая Clean Architecture в простом CRUD/API-to-UI экране может добавить boilerplate и замедлить разработку без реальной пользы.

**Коротко:** use Clean Architecture pragmatically: keep clear boundaries and testable business logic, but avoid adding layers that do not solve a real problem.

### Когда нужен domain layer?

Domain layer нужен не всегда. Он полезен, когда есть сложная бизнес-логика, сценарии переиспользуются между несколькими `ViewModel`, нужно объединять несколько repositories или важно тестировать business rules отдельно от UI и data details.

Типичные примеры: payment flow, authorization rules, permissions, validation, combining user + subscription + feature flags, complex error mapping, orchestration нескольких remote/local sources.

Если экран просто загружает список и показывает его, отдельный use case на каждую маленькую операцию может быть лишним. В таком случае `ViewModel` может обращаться к repository напрямую, если это принято в проекте и границы слоёв остаются понятными.

**Коротко:** domain layer is optional; add it when it reduces duplication, hides complex business logic, or makes behavior easier to test.

## Data ownership

### Repository pattern

Repository - фасад над источниками данных, который даёт остальным слоям единый API для работы с данными.

Repository скрывает, откуда пришли данные: network, database, cache, DataStore, file или websocket. Он может centralize data changes, resolve conflicts between sources, делать mapping и инкапсулировать caching/offline-first логику.

`ViewModel` или use case не должны напрямую зависеть от Retrofit service, DAO или DataSource, если repository уже является entry point в data layer.

**Важно:** repository не должен быть просто тонкой прокладкой без смысла. Он полезен, когда реально скрывает источники данных, правила кэширования, mapping, error handling или orchestration.

**Коротко:** repository abstracts data sources and exposes a clean API to the rest of the app, so UI/domain code does not know whether data comes from API, database or cache.

### Single source of truth

Single source of truth - принцип, при котором у конкретного состояния есть один главный владелец, а остальные части системы читают данные от него, а не хранят конкурирующие копии.

Для UI это значит, что экран должен рендериться из одного актуального UI state, а не собирать противоречивые значения из разных mutable полей. Для данных это часто repository/database/cache как главный источник, из которого строится observable stream.

Single source of truth снижает риск рассинхронизации, race conditions и багов после recreation/configuration change.

**Важно:** не меняй UI state напрямую в UI, если владельцем данных является `ViewModel` или data layer.

**Коротко:** single source of truth means one clear owner of state; UI observes it and sends events back instead of maintaining competing copies.
