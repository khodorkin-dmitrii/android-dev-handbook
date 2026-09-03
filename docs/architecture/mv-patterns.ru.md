# MV* Patterns

MV* patterns отделяют UI от presentation logic, состояния и бизнес-логики. Определения различаются между командами, поэтому полезнее спрашивать: кто владеет состоянием, как действия попадают в систему, как данные доходят до UI и где выполняются side effects.

## Паттерны

### MVC

MVC (Model-View-Controller) разделяет приложение на:

- **Model** - данные и бизнес-правила;
- **View** - отображение UI;
- **Controller** - обработка ввода и координация Model и View.

В ранних Android-приложениях `Activity` или `Fragment` часто одновременно выполняли роли View и Controller. UI-код, lifecycle callbacks, navigation, validation и доступ к данным накапливались в одном классе, создавая "massive Activity" или "massive Fragment".

Проблема не в самом MVC. В Android к ней обычно приводили размытые границы и слишком большое количество обязанностей у framework-классов.

### MVP

MVP (Model-View-Presenter) переносит presentation logic в Presenter. View обычно пассивна: передаёт действия пользователя и реализует команды вроде `showLoading()` или `showContent(items)`. Presenter обращается к Model или repository API и сообщает View, что нужно показать.

Presenter можно unit-тестировать без Android UI classes. Однако он часто хранит ссылку на View, поэтому attach/detach должны учитывать lifecycle. Иначе callbacks могут обратиться к уничтоженному экрану или удерживать его в памяти.

MVP остаётся актуальным в legacy-проектах с XML/Views, но требует больше императивных UI-команд и lifecycle-кода, чем state-driven подходы.

### MVVM

В MVVM (Model-View-ViewModel) View отображает observable state из ViewModel и отправляет ей действия пользователя. ViewModel готовит presentation state и координирует работу с domain или data layer.

В Android Jetpack `ViewModel` - это владелец состояния экрана, который переживает configuration changes и хорошо сочетается со `StateFlow`, Coroutines, Compose и lifecycle-aware collection. При этом `ViewModel` не является persistent storage и не должна хранить ссылки на `Activity`, `Fragment` или View.

Одного использования Jetpack `ViewModel` недостаточно, чтобы архитектура стала MVVM. Важны также распределение обязанностей и поток данных:

```text
UI action -> ViewModel -> domain/data layer
UI state  <- ViewModel <- domain/data layer
```

`ViewModel` должна заниматься состоянием экрана и координацией. Сложные или переиспользуемые бизнес-правила лучше размещать в use cases или repositories, а логику переиспользуемого UI-элемента - в обычном state holder.

### MVI

MVI (Model-View-Intent) делает акцент на явном однонаправленном потоке данных:

```text
Intent/Action -> processing -> new State -> View
```

Здесь `Intent` означает намерение пользователя или системное действие, например `RetryClicked`, и не обязательно связан с Android `android.content.Intent`.

Типичные элементы MVI:

- **State** - неизменяемое описание отображаемого UI;
- **Intent/Action** - входное действие пользователя или системы;
- **Reducer** - функция, создающая новое состояние из предыдущего state и результата;
- **Processor/Actor** - необязательный компонент для asynchronous work и side effects.

Reducer должен оставаться детерминированным: одинаковые old state и result дают одинаковый new state. Сетевые запросы, storage и timers выполняются за его пределами, а их результаты возвращаются в state pipeline.

MVI делает transitions предсказуемыми и удобными для логирования и тестирования, особенно на сложных экранах. Строгая реализация может породить множество actions, results и processors, поэтому её сложность должна соответствовать фиче.

## Сравнение

### MVVM и MVI

| | MVVM | MVI-style state management |
|---|---|---|
| Главный акцент | Разделение View и presentation state | Явные однонаправленные state transitions |
| Входные действия | Методы ViewModel или actions | Обычно типизированные actions/intents |
| Обновление state | Любая контролируемая логика ViewModel | Часто immutable и reducer-like |
| Лучше подходит | Большинству обычных экранов | Сложным экранам с множеством событий и состояний |
| Главный риск | Большая и несфокусированная ViewModel | Избыточные boilerplate и abstraction |

Граница между подходами нестрогая. В современном Android часто используют Jetpack `ViewModel`, immutable `UiState` и UDF. Такой вариант вполне можно назвать MVVM с MVI-style управлением состоянием.

### MVVM с MVI-style управлением состоянием

Практичный гибрид сохраняет `ViewModel` владельцем состояния, но заимствует у MVI явные `UiState` и `UiAction`:

```text
UI renders UiState
UI sends UiAction
ViewModel handles the action and updates UiState
```

Не каждой фиче нужны единая функция `dispatch(action)` и формальный reducer. Методы вроде `onRetry()` тоже соответствуют UDF, если actions движутся вверх, а state - вниз.

Долговечные результаты следует представлять как state. Для действительно одноразовых UI effects нужно осознанно выбрать delivery semantics, потому что неактивный UI может пропустить событие в памяти. Обработка navigation, snackbar и похожих эффектов должна соответствовать общей политике проекта по UI state.

## Связанные темы

- [Architecture Basics](basics.ru.md)
- [UI State Architecture](ui-state.ru.md)
- [Lifecycle-aware Collection](../coroutines-flow/lifecycle-aware-collection.ru.md)
