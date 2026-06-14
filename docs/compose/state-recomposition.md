# State & Recomposition

State and recomposition are the foundation of the Compose mental model: UI is described as a function of state, and Compose updates affected parts when state changes.

## State

### What is recomposition?

Recomposition is a repeated call of composable functions when state read during Composition has changed. Compose tries to update only the affected part of the UI tree and skip unchanged composables.

Recomposition itself is normal and is not a bug. It becomes a problem when it is too frequent, affects too large a part of UI or expensive work is performed inside a composable.

It is important to distinguish Compose phases: Composition determines what to show, Layout measures and places, Drawing renders. A state change can restart one or more phases depending on where the state is read: in the composable body, layout modifier or draw phase.

**In short:** recomposition is how Compose updates UI from state changes; the goal is not to avoid it completely, but to keep it scoped and cheap.

### `remember` vs `rememberSaveable`

`remember` keeps a value between recompositions within the current composition. It does not survive removing the composable from composition, configuration change or process death.

`rememberSaveable` also keeps a value between recompositions, but additionally tries to restore it after `Activity` / `Fragment` recreation through saved instance state if the type can be stored in a `Bundle` or has a `Saver`.

`remember` fits local transient UI state and caching calculations inside composition. `rememberSaveable` fits simple UI state that the user expects to be restored after rotation, such as input text or selected tab.

**Important:** neither `remember` nor `rememberSaveable` replaces `ViewModel` or persistent storage. For screen/business state, prefer `ViewModel`, `SavedStateHandle`, repository/cache/database depending on the data.

**In short:** `remember` survives recomposition, `rememberSaveable` also survives recreation when the value can be saved.

### `mutableStateOf`

`mutableStateOf` creates observable Compose `State`. When `value` changes, Compose invalidates places where this state was read and can start recomposition.

It is usually used together with `remember`:

```kotlin
var text by remember { mutableStateOf("") }
```

Without `remember`, state will be created again on every recomposition.

For screen-level state, it is usually better to use `ViewModel` + `StateFlow` and `collectAsStateWithLifecycle()`, leaving `mutableStateOf` for local UI state or state holders that intentionally use Compose runtime.

**Important:** if a mutable collection is stored inside `mutableStateOf` and its contents are changed without assigning a new `value`, Compose may not see the change. For UI state, prefer immutable copy.

**In short:** `mutableStateOf` is Compose-observable state; changing it triggers invalidation where it was read, but state ownership still matters.

### State hoisting

State hoisting - moving state from a child composable to the nearest common owner so the composable becomes more stateless, reusable and testable.

Usually the child receives `value` and a callback like `onValueChange`, while state is stored higher: in a parent composable, screen state holder or `ViewModel` if the state belongs to screen/business logic.

Not all state needs to be hoisted to `ViewModel`. Local UI state, such as `expanded` for a dropdown or pressed/animation state, can stay inside a composable if other layers do not need it and it does not need to survive screen recreation.

**In short:** state hoisting separates state ownership from UI rendering; UI receives state and emits events, while the owner decides how state changes.

## Stability and optimization

### Stable parameters / `@Stable` / immutability

Stability in Compose helps the compiler/runtime understand whether recomposition can be safely skipped when composable parameters have not changed.

A stable type has a predictable `equals()` / identity contract and reports changes to Compose so UI can be updated correctly. Immutable data classes with `val` properties and immutable/read-only data are usually easier for Compose than mutable objects with implicit changes.

`@Stable` and `@Immutable` are contracts with the Compose compiler, not magic optimizations. Do not mark a mutable model as stable if changes to its fields are not tracked by Compose: UI may stop updating correctly.

**In short:** stable parameters allow Compose to skip more safely, but annotations must reflect real state behavior; wrong stability is a correctness bug, not just a performance issue.

### How to reduce unnecessary recompositions?

Unnecessary recompositions are reduced not by banning recomposition itself, but by placing state correctly and lowering the cost of affected UI.

Practical techniques: keep state closer to where it is used, hoist only shared state, split the screen into reasonable composables, use stable keys in lazy lists, avoid heavy work in composable body and do not create new unstable objects unnecessarily.

`derivedStateOf` is useful when a derived value is often recalculated from frequently changing state, but UI should actually be invalidated only when the result changes. `remember` is useful for caching calculations, but should not hide business logic.

**In short:** optimize recomposition by understanding which state is read where, then reduce unnecessary invalidation and expensive work instead of blindly adding `remember` everywhere.
