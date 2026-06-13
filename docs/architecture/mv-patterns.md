# MV* Patterns

MV* patterns помогают разделять UI, presentation logic, state и data/business logic. В Android они часто смешиваются с Jetpack `ViewModel`, lifecycle и Flow/Compose-подходами.

## Patterns

### MVC

MVC (Model-View-Controller) разделяет приложение на Model, View и Controller. Model отвечает за данные и бизнес-логику, View отображает UI, Controller обрабатывает user input и обновляет Model/View.

В классическом Android старые `Activity` / `Fragment` часто становились одновременно View и Controller: они держали UI, lifecycle, navigation, validation, network calls и часть business logic.

Проблема такого подхода - massive `Activity` / `Fragment`: сложнее тестировать, переиспользовать и поддерживать код, потому что слишком много ответственности оказывается в одном классе.

**Коротко:** MVC is a basic separation into Model, View and Controller, but in Android it often led to heavy `Activity` / `Fragment` classes.

### MVP

MVP (Model-View-Presenter) разделяет UI и presentation logic. View обычно реализует interface и показывает данные, Presenter получает user actions, обращается к Model/repositories и командует View, что показать.

Presenter легче unit-тестировать, потому что он может не зависеть напрямую от Android UI classes. View в MVP обычно пассивная: показать loading, показать content, показать error, открыть экран.

MVP был популярен в Android до широкого распространения `ViewModel` / `LiveData` / Flow / Compose, особенно в XML UI и legacy проектах.

**Важно:** Presenter часто держит reference на View, поэтому важно правильно attach/detach по lifecycle, иначе легко получить leaks или callback в уничтоженный экран.

**Коротко:** MVP moves presentation logic from `Activity` / `Fragment` into Presenter, but requires careful View lifecycle management.

### MVVM

MVVM (Model-View-ViewModel) разделяет UI и state/presentation logic через `ViewModel`. View рендерит observable state и отправляет user actions, `ViewModel` готовит UI state и вызывает domain/data layer.

В Android `ViewModel` из Jetpack также переживает configuration changes и хорошо сочетается с `StateFlow` / `LiveData`, Coroutines, Compose и lifecycle-aware collection.

Типичный flow: UI вызывает action -> `ViewModel` запускает use case/repository -> обновляет `UiState` -> UI перерисовывается из нового state.

Плюсы: меньше логики в `Activity` / `Fragment` / composable, проще тестировать `ViewModel`, легче хранить screen state и переживать rotation.

**Важно:** `ViewModel` не должна превращаться в god object. Если логика сложная, её стоит выносить в use cases, repositories, mappers или отдельные state holders.

**Коротко:** MVVM fits modern Android well: View observes state from `ViewModel`, sends actions back, and `ViewModel` coordinates domain/data logic.

### MVI

MVI (Model-View-Intent) делает акцент на unidirectional data flow: View отправляет Intent/Action, logic обрабатывает его, создаётся новый immutable State, View рендерит этот State.

Обычно в MVI есть три ключевых элемента: State, Intent/Action и Reducer/Processor. State описывает экран, Intent описывает действие пользователя или системы, Reducer/Processor превращает old state + action/result в new state.

Плюсы: предсказуемость, один источник truth для UI, удобное логирование state transitions, проще reasoning для сложных экранов с большим количеством состояний.

Минусы: может быть больше boilerplate, сложнее onboarding, а для простых экранов строгий MVI может быть избыточным.

**Коротко:** MVI is unidirectional and state-driven: actions go in, state comes out, and the UI is rendered from a single immutable state.

## Comparison

### MVVM vs MVI

MVVM - более общий pattern: `ViewModel` отдаёт observable state и обрабатывает действия UI. Он не обязательно требует строгого reducer, единого intent pipeline или полностью immutable state transitions.

MVI - более строгий state-management подход с unidirectional flow, explicit intents/actions, immutable state и часто reducer-like обновлением состояния.

В modern Android часто используют гибрид: `ViewModel` как Android state holder + MVI-style `UiState`, `UiAction` и `UiEffect`. Это даёт практичность MVVM и предсказуемость MVI без лишнего framework boilerplate.

Для простых экранов MVVM обычно достаточно. Для сложных экранов с множеством событий, partial loading, optimistic updates и сложными transitions MVI-style state management может быть удобнее.

**Коротко:** MVVM is the architectural container around `ViewModel` and observable state, while MVI is a stricter unidirectional state-management style.

### MVVM with MVI-style state management

MVVM with MVI-style state management - практичный Android-подход, где `ViewModel` остаётся владельцем состояния, но state обновляется в стиле unidirectional data flow.

Обычно есть `UiState`, `UiAction` и `UiEffect`. UI рендерит `UiState`, отправляет `UiAction` во `ViewModel`, `ViewModel` выполняет logic/use cases и обновляет state. Одноразовые команды вроде navigation/snackbar идут как `UiEffect`.

Такой подход хорошо подходит для Compose и `StateFlow`: экран становится функцией от state, а actions идут в одну точку обработки.

Важно не делать архитектуру слишком тяжёлой: reducer, action/result layers и отдельные processors нужны только если они реально упрощают сложность feature.

**Коротко:** MVVM with MVI-style state means `ViewModel` owns immutable `UiState`, UI sends actions, and one-off effects are separated from persistent state.
