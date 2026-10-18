# Architecture

Этот раздел посвящён архитектуре Android-приложений: границам ответственности, владению state, unidirectional data flow, MV* patterns, modularization и постепенному изменению legacy-систем.

Практичный порядок изучения: начните с основ архитектуры и UI state. Затем сравните MV* patterns как разные способы организации presentation logic. Переходите к multi-module architecture, когда проекту и команде нужны более чёткие границы, а раздел про legacy используйте для безопасного изменения существующей системы.

## Проектирование и state

- [Architecture Basics](basics.md) - слои, направление зависимостей, repositories, опциональная domain logic, unidirectional data flow и sources of truth.
- [UI State Architecture](ui-state.md) - владение state, immutable UI models, events, effects, lifecycle boundaries и восстановление состояния.
- [MV* Patterns](mv-patterns.md) - зоны ответственности MVC, MVP, MVVM и MVI, reducers, effects и прагматичный выбор паттерна.

## Масштабирование и изменения

- [Multi-module Architecture](multi-module.md) - границы модулей, public APIs, правила зависимостей, Gradle configurations и modularization на основе измерений.
- [Legacy & Refactoring](legacy-refactoring.md) - сохранение поведения, safety checks, incremental migration, lifecycle-риски и замена legacy UI или reactive-кода.
