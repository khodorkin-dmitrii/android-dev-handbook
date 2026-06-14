# Legacy & Refactoring

Legacy и refactoring в Android требуют аккуратности: важно сохранять существующее поведение, постепенно улучшать boundaries и не превращать migration в большой рискованный rewrite.

## Legacy

### Legacy-код в Android-проекте

Legacy-код - это не обязательно плохой код. Обычно это код, который долго живёт в проекте, написан под старые требования, старые архитектурные решения, устаревшие библиотеки или до появления текущих team conventions.

В Android legacy часто выглядит как massive `Activity` / `Fragment`, XML + callbacks, RxJava chains, ручной DI/service locator, static singletons, сложные inheritance hierarchies, старые navigation approaches или смешение UI, business logic и data access в одном классе.

Работа с legacy требует осторожности: сначала нужно понять текущий behavior, покрыть критичные сценарии тестами или хотя бы characterization tests, и только потом менять структуру.

Главный принцип - не переписывать всё ради "красивой архитектуры", а снижать риск и постепенно улучшать boundaries: выносить data access в repository, бизнес-логику в use case/domain, UI state во `ViewModel`, а side effects делать явными.

**Коротко:** legacy code is code with existing behavior and constraints; refactor it incrementally, first protecting behavior with tests or checks, then improving boundaries and reducing coupling.

### Incremental refactoring

Incremental refactoring - постепенное улучшение кода маленькими безопасными шагами без большого big bang rewrite.

В Android это особенно важно, потому что feature может быть связана с lifecycle, navigation, analytics, caching, push/deep links, permissions и разными версиями OS. Большой rewrite легко ломает скрытые сценарии.

Практичный процесс: найти pain point, зафиксировать текущее поведение, добавить тесты или ручной checklist, выделить small seams, затем переносить логику по частям.

Примеры small steps: вынести network call из `Activity` в repository, заменить callback на suspend function/Flow, ввести `UiState`, отделить mapper, добавить interface для legacy dependency, покрыть `ViewModel` тестами, постепенно удалить дублирование.

Важно сохранять public contracts и мигрировать call sites постепенно. Если нужно менять API, лучше сначала добавить новый путь, перевести клиентов, потом удалить старый.

**Коротко:** incremental refactoring reduces risk by changing one boundary at a time, keeping behavior stable and continuously verifying the result.

## Migration

### Migration from XML/RxJava to Compose/Flow

Миграция с XML/RxJava на Compose/Flow обычно должна быть постепенной, потому что в реальном Android-проекте UI, navigation, lifecycle, DI, analytics и data layer часто сильно связаны.

Для UI можно использовать interoperability: добавлять Compose через `ComposeView` внутри XML/Fragment или, наоборот, встраивать `AndroidView` / `ViewBinding` в Compose, если нужно временно переиспользовать старый `View`.

Для state management полезно сначала привести экран к `ViewModel` + `UiState`, а уже потом менять rendering layer. Если `ViewModel` отдаёт стабильный `StateFlow<UiState>`, UI можно заменить с XML на Compose с меньшим риском.

Для RxJava миграции важно не делать механическую замену операторов. Нужно понять semantics: cold/hot streams, backpressure, schedulers, error handling, cancellation/disposal и lifecycle. Rx `Observable` / `Single` / `Completable` можно постепенно адаптировать в suspend functions или `Flow` на границах слоя.

Практичный путь: сначала изолировать Rx внутри repository/data layer, наружу отдавать suspend/Flow для нового кода, затем постепенно переписывать внутреннюю реализацию. Для UI collection использовать lifecycle-aware APIs: `collectAsStateWithLifecycle()` в Compose и `repeatOnLifecycle()` во View System.

**Важно:** нельзя одновременно менять UI framework, reactive stack и бизнес-логику без чёткой проверки поведения. Лучше разделять migration steps и делать rollback-friendly изменения.

**Коротко:** prefer migration in layers: first stabilize state contracts, then bridge old and new UI/reactive APIs, and only then replace implementations gradually.
