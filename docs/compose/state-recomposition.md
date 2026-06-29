# State & Recomposition

State and recomposition are the foundation of the Compose mental model: UI is described as a function of state, and Compose updates affected parts when state changes. For screen-level state modeling, see [UI State Architecture](../architecture/ui-state.md).

## State

### What is state in Compose?

State is any value that can change over time and affect what the UI should show.

Examples of UI state:

* text entered into a text field;
* selected tab;
* expanded/collapsed dropdown;
* loading flag;
* loaded content;
* error message;
* scroll-related UI flag.

In Compose, UI is usually described as a function of state:

```kotlin
UI = f(state)
```

When state changes, Compose can call affected composable functions again with the new values and update the UI.

It is important to distinguish ordinary Kotlin values from observable state. Changing a regular variable does not automatically tell Compose that UI should be updated:

```kotlin
var count = 0 // not observable by Compose
```

Compose needs state that it can observe, such as `State<T>`, `MutableState<T>` created with `mutableStateOf`, or external observable state collected into Compose state:

```kotlin
var count by remember { mutableStateOf(0) }
```

Compose tracks where observable state is read. When that state changes, Compose invalidates the places that read it and can recompose the affected UI.

**In short:** state is data that affects what the UI shows; Compose can update UI automatically only when that data is exposed through observable state.

### Observable state and `mutableStateOf`

`mutableStateOf` creates observable Compose `State`. When `value` changes, Compose invalidates places where this state was read and can start recomposition.

It is usually used together with `remember`:

```kotlin
var text by remember { mutableStateOf("") }
```

Without `remember`, state will be created again on every recomposition.

For screen-level state, it is usually better to use `ViewModel` + [`StateFlow`](../coroutines-flow/stateflow-sharedflow.md) and [`collectAsStateWithLifecycle()`](../coroutines-flow/lifecycle-aware-collection.md), leaving `mutableStateOf` for local UI state or state holders that intentionally use Compose runtime.

**Important:** if a mutable collection is stored inside `mutableStateOf` and its contents are changed without assigning a new `value`, Compose may not see the change.

Prefer immutable UI state updates:

```kotlin
var items by remember { mutableStateOf<List<String>>(emptyList()) }

items = items + "New item"
```

If local mutable collection state is intentional, use Compose snapshot-aware collections such as `mutableStateListOf`. For screen state from `ViewModel`, prefer immutable models and immutable lists.

**In short:** `mutableStateOf` is Compose-observable state; changing it triggers invalidation where it was read, but state ownership still matters.

### What is recomposition?

Recomposition is a repeated call of composable functions when state read during Composition has changed. Compose tries to update only the affected part of the UI tree and skip unchanged composables.

Recomposition itself is normal and is not a bug. It becomes a problem when it is too frequent, affects too large a part of UI or expensive work is performed inside a composable. Performance-focused cases are covered separately in [Compose Performance](performance.md).

It is important to distinguish Compose phases: Composition determines what to show, Layout measures and places, Drawing renders. A state change can restart one or more phases depending on where the state is read: in the composable body, layout modifier or draw phase.

For example, state read directly in a composable body can trigger recomposition. State read only inside a draw modifier may avoid recomposition and restart only drawing.

**In short:** recomposition is how Compose updates UI from state changes; the goal is not to avoid it completely, but to keep it scoped and cheap.

### `remember` vs `rememberSaveable`

`remember` keeps a value between recompositions within the current composition. It does not survive removing the composable from composition, configuration change or process death.

`rememberSaveable` also keeps a value between recompositions, but additionally tries to restore it after `Activity` / `Fragment` recreation through saved instance state if the type can be stored in a `Bundle` or has a `Saver`.

`remember` fits local transient UI state and caching calculations inside composition. `rememberSaveable` fits simple UI state that the user expects to be restored after rotation, such as input text, selected tab or selected item id.

Do not store large lists, bitmaps or full screen data in `rememberSaveable`. It is backed by saved instance state and should be used only for small UI element state.

**Important:** neither `remember` nor `rememberSaveable` replaces `ViewModel` or persistent storage. For screen/business state, prefer `ViewModel`, `SavedStateHandle`, repository/cache/database depending on the data.

**In short:** `remember` survives recomposition, `rememberSaveable` also survives recreation when the value can be saved.

### Where should state live?

State should live in the lowest place that owns it and can correctly update it.

Common ownership levels:

* local UI element state: `remember`;
* local UI state that should survive recreation: `rememberSaveable`;
* screen state or business-related state: `ViewModel`;
* state that must survive process death or app restart: `SavedStateHandle`, repository, database, DataStore or backend.

For example, whether a dropdown is expanded can usually stay inside the composable. A loaded user profile, payment state or form submission state usually belongs in a `ViewModel`.

A useful rule: if state affects only one small UI element and no other layer needs it, keep it local. If state represents the screen, business logic or data loading, move it to a screen-level state holder and model it as part of [UI state](../architecture/ui-state.md).

**In short:** keep state as local as possible, but as high as necessary.

### State hoisting

State hoisting is moving state from a child composable to the nearest common owner so the composable becomes more stateless, reusable and testable.

Usually the child receives `value` and a callback like `onValueChange`, while state is stored higher: in a parent composable, screen state holder or `ViewModel` if the state belongs to screen/business logic. One-off actions such as navigation or snackbar should stay separate from durable state and are usually handled with [Compose side effects](side-effects.md).

A stateless composable exposes value and events:

```kotlin
@Composable
fun SearchField(
    query: String,
    onQueryChange: (String) -> Unit
) {
    TextField(
        value = query,
        onValueChange = onQueryChange
    )
}
```

The owner stores and updates the state:

```kotlin
@Composable
fun SearchScreen() {
    var query by rememberSaveable { mutableStateOf("") }

    SearchField(
        query = query,
        onQueryChange = { query = it }
    )
}
```

Not all state needs to be hoisted to `ViewModel`. Local UI state, such as `expanded` for a dropdown or pressed/animation state, can stay inside a composable if other layers do not need it and it does not need to survive screen recreation.

**In short:** state hoisting separates state ownership from UI rendering; UI receives state and emits events, while the owner decides how state changes.

## Stability and optimization

### Stable parameters / `@Stable` / immutability

Stability in Compose helps the compiler/runtime understand whether recomposition can be safely skipped when composable parameters have not changed.

A stable type has a predictable `equals()` / identity contract and reports changes to Compose so UI can be updated correctly. Immutable data classes with `val` properties and immutable/read-only data are usually easier for Compose than mutable objects with implicit changes.

A `data class` is not automatically deeply immutable if it contains mutable collections or mutable objects:

```kotlin
data class UiState(
    val items: MutableList<String>
)
```

Even though `items` is a `val`, the list contents can still change. Compose may not observe such internal mutations correctly. Prefer immutable state models:

```kotlin
data class UiState(
    val items: List<String>
)
```

`@Stable` and `@Immutable` are contracts with the Compose compiler, not magic optimizations. Do not mark a mutable model as stable if changes to its fields are not tracked by Compose: UI may stop updating correctly.

Prefer real immutability first. Use stability annotations only when you understand and can guarantee the contract.

**In short:** stable parameters allow Compose to skip more safely, but annotations must reflect real state behavior; wrong stability is a correctness bug, not just a performance issue.

### How to reduce unnecessary recompositions?

Unnecessary recompositions are reduced not by banning recomposition itself, but by placing state correctly and lowering the cost of affected UI.

Practical techniques:

* keep state close to where it is used;
* hoist only shared state;
* split the screen into reasonable composables;
* use stable keys in lazy lists;
* avoid heavy work in composable body;
* avoid creating new unstable objects unnecessarily;
* prefer immutable UI models;
* read frequently changing state as low as possible in the UI tree.

`remember` is useful for caching calculations inside composition, but should not hide business logic.

`derivedStateOf` is useful when input state changes often, but the derived result changes less often and UI should be invalidated only when that result changes. This is one of the common tools for reducing unnecessary work described in [Compose Performance](performance.md).

For example, a list scroll position can change very frequently, but the UI may only care whether the first item is visible:

```kotlin
val showScrollToTop by remember {
    derivedStateOf {
        listState.firstVisibleItemIndex > 0
    }
}
```

Do not use `derivedStateOf` for every computed value. It adds complexity and is most useful when it prevents unnecessary invalidation from frequently changing input state.

**In short:** optimize recomposition by understanding which state is read where, then reduce unnecessary invalidation and expensive work instead of blindly adding `remember` everywhere.
