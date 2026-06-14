# Multi-module Architecture

Multi-module architecture помогает разделять большой Android-проект на Gradle-модули с понятными границами, зависимостями и ответственностью.

## Modules

### Что такое multi-module project?

Multi-module project - Android/Gradle проект, разделённый на несколько модулей вместо одного большого app module.

Модули могут быть feature, core/library, data, domain, design system, testing utilities или platform-specific wrappers. Каждый module имеет свой `build.gradle`, dependencies и public API.

Зачем это нужно: ускорить incremental builds, уменьшить связанность, разделить ownership между командами, переиспользовать код, упростить тестирование и скрыть внутренние детали реализации.

Trade-off: multi-module architecture добавляет сложность в Gradle configuration, dependency graph, navigation, DI setup и version management. Маленькому проекту она может быть не нужна.

**Коротко:** multi-module architecture splits a large app into Gradle modules to improve boundaries, build performance, ownership and testability, but it should be introduced pragmatically.

### Feature modules

Feature module содержит код конкретной функциональности или user flow: login, profile, payments, product details, settings, onboarding.

Обычно feature module включает UI, `ViewModel` / state holder, feature-specific models, navigation entry point и иногда feature-specific domain logic. Общие вещи не должны копироваться в каждую feature, а должны жить в core modules.

Feature modules помогают изолировать ответственность: команда может менять feature, не затрагивая весь app module. Также они могут ускорить сборку и улучшить архитектурные границы.

**Важно:** feature modules не должны напрямую зависеть друг от друга хаотично. Для связи между features часто используют navigation contracts, interfaces, shared domain models или app-level coordinator.

**Коротко:** feature modules isolate user-facing features and should depend on shared core/domain contracts rather than directly knowing about every other feature.

### Core modules

Core modules содержат переиспользуемую инфраструктуру и shared code, который нужен нескольким features.

Типичные core modules: `core:network`, `core:database`, `core:ui` / `designsystem`, `core:common`, `core:model`, `core:analytics`, `core:testing`, `core:datastore`.

Хороший core module имеет понятную ответственность и стабильный public API. Он не должен превращаться в dumping ground для всего подряд.

Core modules обычно не должны зависеть от feature modules. Направление зависимостей чаще идёт от features к core, а app module связывает всё вместе.

**Важно:** слишком общий `core:utils` быстро превращается в мусорный модуль. Лучше создавать маленькие модули по ответственности: formatting, date/time, dispatchers, logging, permissions, design system.

**Коротко:** core modules hold reusable infrastructure and shared contracts, but they must stay focused and not become a global utils dump.

## Dependencies

### Dependency graph

Dependency graph показывает, какие modules зависят друг от друга. В хорошей архитектуре он направленный и понятный: app module собирает features, features зависят от domain/core contracts, data modules реализуют repositories и зависят от network/database.

Главная цель - не допустить хаотичных зависимостей, когда любой module может импортировать любой другой. Это ломает boundaries и делает изменения дорогими.

Типичный принцип: низкоуровневые shared modules не зависят от высокоуровневых feature modules. Domain/contracts должны быть стабильнее, чем конкретные data/UI implementations.

DI помогает соединять реализации с абстракциями: feature или domain может зависеть от `Repository` interface, а app/data layer предоставляет реализацию через Hilt/Dagger module.

**Коротко:** module dependency graph should be acyclic and layered; app wiring and DI connect modules without breaking boundaries.

### Cyclic dependencies

Cyclic dependency возникает, когда module A зависит от module B, а B прямо или косвенно зависит от A.

Gradle обычно не позволяет прямые cycles, но архитектурные cycles могут появляться через shared modules, callbacks, navigation и неверное размещение interfaces.

Проблема cycles в том, что модули нельзя независимо собирать, тестировать и переиспользовать. Любое изменение тянет цепочку зависимостей назад и ломает смысл modularization.

Решение: вынести общий contract в отдельный module, инвертировать зависимость через interface, использовать DI, event/navigation contract или app-level coordinator.

Пример: если feature A должна открыть feature B, A не должна зависеть от implementation B напрямую. Можно вынести Route/Navigation contract в shared module, а app module выполнит actual navigation.

**Коротко:** cyclic dependencies mean module boundaries are wrong; usually the cycle is broken by extracting a contract module or inverting the dependency.
