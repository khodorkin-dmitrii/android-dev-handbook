# MV* Patterns

MV* patterns separate UI from presentation, state and business logic. Their definitions vary between teams, so the useful questions are who owns state, how actions enter the system, how data reaches UI and where side effects happen.

## Patterns

### MVC

MVC (Model-View-Controller) separates an application into:

- **Model** - data and business rules;
- **View** - UI rendering;
- **Controller** - input handling and coordination between Model and View.

In early Android applications, an `Activity` or `Fragment` often acted as both View and Controller. UI code, lifecycle callbacks, navigation, validation and data access accumulated in one class, producing a "massive Activity" or "massive Fragment".

MVC is not inherently broken. The Android problem was usually unclear boundaries and framework classes owning too many responsibilities.

### MVP

MVP (Model-View-Presenter) moves presentation logic into a Presenter. The View is normally passive: it forwards user actions and implements operations such as `showLoading()` or `showContent(items)`. The Presenter calls Model or repository APIs and tells the View what to display.

A Presenter can be unit-tested without Android UI classes. However, it commonly holds a View reference, so attach/detach must follow the lifecycle. Otherwise callbacks can target a destroyed screen or keep it in memory.

MVP remains relevant in legacy XML/View projects, but it requires more imperative UI commands and lifecycle plumbing than state-driven approaches.

### MVVM

MVVM (Model-View-ViewModel) makes the View render observable state exposed by a ViewModel and send user actions back to it. The ViewModel prepares presentation state and coordinates the domain or data layer.

On Android, Jetpack `ViewModel` is a screen-level state holder that survives configuration changes and works well with `StateFlow`, Coroutines, Compose and lifecycle-aware collection. It is not persistent storage and must not hold references to `Activity`, `Fragment` or View instances.

Using Jetpack `ViewModel` does not automatically make an application MVVM. The pattern also depends on responsibilities and data flow:

```text
UI action -> ViewModel -> domain/data layer
UI state  <- ViewModel <- domain/data layer
```

Keep `ViewModel` focused on screen state and coordination. Reusable or complex business rules belong in use cases or repositories; reusable UI-element logic can use a plain state holder.

### MVI

MVI (Model-View-Intent) emphasizes explicit unidirectional data flow:

```text
Intent/Action -> processing -> new State -> View
```

Here, `Intent` means a user or system intention such as `RetryClicked`; it does not necessarily mean Android's `android.content.Intent`.

Typical elements are:

- **State** - an immutable description of what the UI renders;
- **Intent/Action** - an input from the user or system;
- **Reducer** - a function that produces new state from previous state and a result;
- **Processor/Actor** - optional asynchronous work and side effects.

A reducer should remain deterministic: the same old state and result should produce the same new state. Network calls, storage and timers run outside it, and their results return to the state pipeline.

MVI makes transitions predictable and easy to log or test, especially on complex screens. Strict implementations can add many actions, results and processors, so the ceremony should match the feature.

## Comparison

### MVVM vs MVI

| | MVVM | MVI-style state management |
|---|---|---|
| Main focus | Separation of View and presentation state | Explicit unidirectional state transitions |
| Inputs | ViewModel method calls or actions | Usually typed actions/intents |
| State updates | Any controlled ViewModel logic | Often reducer-like and immutable |
| Best fit | Most ordinary screens | Complex, event-heavy or state-heavy screens |
| Main risk | A large, unfocused ViewModel | Excessive boilerplate and abstraction |

The boundary is not strict. Modern Android commonly uses a Jetpack `ViewModel` with immutable `UiState` and UDF, which can reasonably be described as MVVM with MVI-style state management.

### MVVM with MVI-style state management

A practical hybrid keeps `ViewModel` as the state owner while borrowing explicit `UiState` and `UiAction` from MVI:

```text
UI renders UiState
UI sends UiAction
ViewModel handles the action and updates UiState
```

Not every feature needs a single `dispatch(action)` function or a formal reducer. Named methods such as `onRetry()` still follow UDF when actions move upward and state moves downward.

Durable outcomes should be represented in state. Truly transient UI effects require deliberately chosen delivery semantics because an inactive UI can miss an in-memory event. Keep navigation, snackbar and similar handling consistent with the project's UI-state policy.

## Related topics

- [Architecture Basics](basics.md)
- [UI State Architecture](ui-state.md)
- [Lifecycle-aware Collection](../coroutines-flow/lifecycle-aware-collection.md)
