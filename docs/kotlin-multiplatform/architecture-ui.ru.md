# Архитектура и стратегии UI

KMP не требует конкретной архитектуры. Он сочетается с MVVM, unidirectional data flow (UDF), MVI-like immutable state, feature-based modules и выборочным применением Clean Architecture. Архитектура должна отражать сложность продукта, а не технологию компиляции общего кода.

```text
Platform or shared UI
        ↓ UserAction
Shared state holder / ViewModel
        ↓
Use cases or repositories
        ↓
Local and remote data sources
        ↓
StateFlow<UiState>
```

UDF с immutable `UiState`, actions и `StateFlow` может использоваться внутри MVVM. Эти решения сами по себе не превращают архитектуру в MVI.

## Варианты presentation

1. **Platform ViewModels и UI.** Data и domain общие, а Android и iOS используют нативные соглашения для state, lifecycle и navigation.
2. **Общий plain Kotlin state holder с нативным UI.** Поведение и state общие, но каждая платформа явно управляет созданием, отменой работы и collection.
3. **Общий AndroidX ViewModel с платформенной интеграцией.** AndroidX ViewModel поддерживает KMP и доступен в `commonMain`, но lifecycle integration различается. Android components предоставляют стандартных owners, а SwiftUI требует bridge наподобие `ViewModelStoreOwner` и явной очистки.
4. **Общие ViewModel и Compose Multiplatform UI.** Presentation и rendering можно переиспользовать вместе, если поддерживаемые targets и UX продукта совпадают.
5. **Гибрид по features.** Каждая feature разделяет только то, что приносит пользу.

Plain state holder может быть проще экспортируемого AndroidX ViewModel, если семантика Android lifecycle не нужна. Hilt недоступен в `commonMain`, поэтому `@HiltViewModel` не может собирать shared ViewModel. Подходят constructor injection, platform composition roots или совместимое multiplatform DI-решение.

## Navigation как граница

При нативном UI каждая платформа может владеть navigation stack, а shared logic - выдавать navigation results, destinations или effects. Shared Compose UI позволяет переиспользовать больше navigation implementation. Ни один вариант не обязателен: lifecycle, deep links, system back behavior и платформенные presentation conventions требуют осознанной интеграции.

## Нативный, общий и гибридный UI

| Подход | Сильные стороны | Основные издержки |
| --- | --- | --- |
| Native UI | Платформенный UX, accessibility conventions, прямые интеграции | Дублирование rendering и части presentation |
| Shared Compose UI | Product parity, одна UI-реализация, согласованные releases | Cross-platform skills, интеграция и ограничения targets |
| Hybrid UI | Переиспользование там, где оно полезно, и native exceptions | Более явные границы и два способа интеграции |

При выборе учитывайте product parity, платформенный UX, ownership, release cadence, навыки команды, стоимость сопровождения, accessibility и system integrations. Максимальное переиспользование UI не является универсальной целью.

См. [Общий и платформенный код](shared-platform-code.md), [MV Patterns](../architecture/mv-patterns.md), [UI State](../architecture/ui-state.md), [StateFlow и SharedFlow](../coroutines-flow/stateflow-sharedflow.md) и [Dependency Injection](../di/index.md).

## Источники

- [AndroidX ViewModel для KMP](https://developer.android.com/kotlin/multiplatform/viewmodel)
- [Рекомендации Android по KMP](https://developer.android.com/kotlin/multiplatform)
