# MV* Patterns

MV* patterns help separate UI, presentation logic, state and data/business logic. In Android they are often combined with Jetpack `ViewModel`, lifecycle and Flow/Compose approaches.

## Patterns

### MVC

MVC (Model-View-Controller) separates an application into Model, View and Controller. Model owns data and business logic, View displays UI, and Controller handles user input and updates Model/View.

In classic Android, old `Activity` / `Fragment` classes often became both View and Controller: they contained UI, lifecycle, navigation, validation, network calls and part of business logic.

The problem with this approach is massive `Activity` / `Fragment`: code becomes harder to test, reuse and maintain because too many responsibilities end up in one class.

**In short:** MVC is a basic separation into Model, View and Controller, but in Android it often led to heavy `Activity` / `Fragment` classes.

### MVP

MVP (Model-View-Presenter) separates UI and presentation logic. View usually implements an interface and displays data, while Presenter receives user actions, talks to Model/repositories and tells View what to show.

Presenter is easier to unit test because it can avoid direct dependency on Android UI classes. View in MVP is usually passive: show loading, show content, show error, open a screen.

MVP was popular in Android before `ViewModel` / `LiveData` / Flow / Compose became common, especially in XML UI and legacy projects.

**Important:** Presenter often holds a reference to View, so attach/detach must follow the lifecycle correctly. Otherwise it is easy to get leaks or callbacks into a destroyed screen.

**In short:** MVP moves presentation logic from `Activity` / `Fragment` into Presenter, but requires careful View lifecycle management.

### MVVM

MVVM (Model-View-ViewModel) separates UI and state/presentation logic through `ViewModel`. View renders observable state and sends user actions, while `ViewModel` prepares UI state and calls the domain/data layer.

In Android, Jetpack `ViewModel` also survives configuration changes and works well with `StateFlow` / `LiveData`, Coroutines, Compose and lifecycle-aware collection.

A typical flow: UI calls an action -> `ViewModel` runs a use case/repository -> updates `UiState` -> UI redraws from the new state.

Benefits: less logic in `Activity` / `Fragment` / composable functions, easier `ViewModel` testing, easier screen state storage and better handling of rotation.

**Important:** `ViewModel` should not turn into a god object. If logic is complex, move it into use cases, repositories, mappers or separate state holders.

**In short:** MVVM fits modern Android well: View observes state from `ViewModel`, sends actions back, and `ViewModel` coordinates domain/data logic.

### MVI

MVI (Model-View-Intent) focuses on unidirectional data flow: View sends an Intent/Action, logic handles it, a new immutable State is created, and View renders that State.

MVI usually has three key elements: State, Intent/Action and Reducer/Processor. State describes the screen, Intent describes a user or system action, and Reducer/Processor turns old state + action/result into new state.

Benefits: predictability, one source of truth for UI, convenient logging of state transitions, and simpler reasoning for complex screens with many states.

Drawbacks: more boilerplate, harder onboarding, and strict MVI can be excessive for simple screens.

**In short:** MVI is unidirectional and state-driven: actions go in, state comes out, and the UI is rendered from a single immutable state.

## Comparison

### MVVM vs MVI

MVVM is a more general pattern: `ViewModel` exposes observable state and handles UI actions. It does not necessarily require a strict reducer, a single intent pipeline or fully immutable state transitions.

MVI is a stricter state-management approach with unidirectional flow, explicit intents/actions, immutable state and often reducer-like state updates.

Modern Android often uses a hybrid: `ViewModel` as the Android state holder plus MVI-style `UiState`, `UiAction` and `UiEffect`. This gives the practicality of MVVM and the predictability of MVI without unnecessary framework boilerplate.

For simple screens, MVVM is usually enough. For complex screens with many events, partial loading, optimistic updates and complex transitions, MVI-style state management can be more convenient.

**In short:** MVVM is the architectural container around `ViewModel` and observable state, while MVI is a stricter unidirectional state-management style.

### MVVM with MVI-style state management

MVVM with MVI-style state management is a practical Android approach where `ViewModel` remains the state owner, but state is updated in a unidirectional data flow style.

Usually there are `UiState`, `UiAction` and `UiEffect`. UI renders `UiState`, sends `UiAction` to `ViewModel`, and `ViewModel` runs logic/use cases and updates state. One-off commands such as navigation/snackbar are emitted as `UiEffect`.

This approach works well with Compose and `StateFlow`: the screen becomes a function of state, and actions go into one handling point.

Avoid making the architecture too heavy: reducer, action/result layers and separate processors are useful only if they actually reduce feature complexity.

**In short:** MVVM with MVI-style state means `ViewModel` owns immutable `UiState`, UI sends actions, and one-off effects are separated from persistent state.
