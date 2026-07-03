# Compose Basics

Jetpack Compose is a modern declarative UI toolkit for Android. Instead of manually changing the View tree, we describe UI as a function of state, and Compose updates the necessary parts of the interface when data changes.

## Compose basics

### What is Jetpack Compose?

Compose is used to build screens in Kotlin without XML and integrates well with `ViewModel`, `Flow` / `StateFlow`, Material Design, Navigation and testing APIs.

The main mental model: a composable should be fast, idempotent and side-effect free. Do not think that Compose fully redraws the whole screen every time: it tries to skip unchanged parts.

Compose is not only a replacement for XML layouts. It changes how we model UI: instead of manually pushing changes into views, we provide state and let Compose update the affected UI.

**In short:** Jetpack Compose lets us build Android UI declaratively: UI is a function of state, and Compose recomposes affected parts when state changes.

### Declarative UI

Declarative UI is an approach where code describes how UI should look for the current state, not which step-by-step commands should be executed to manually change the screen.

In the imperative View System, we often call `setText()`, `setVisibility()` or `notifyDataSetChanged()`. In Compose, we pass new state into a composable, Compose re-executes affected composable functions and updates the UI tree where needed.

The practical benefit is simpler reasoning about loading/content/error, forms, lists and state-driven screens.

```kotlin
data class UserUiState(
    val isLoading: Boolean = false,
    val userName: String? = null,
    val error: String? = null
)

@Composable
fun UserScreen(
    state: UserUiState,
    onRetryClick: () -> Unit
) {
    when {
        state.isLoading -> CircularProgressIndicator()
        state.error != null -> ErrorMessage(
            message = state.error,
            onRetryClick = onRetryClick
        )
        state.userName != null -> Text("Hello, ${state.userName}")
    }
}
```

Here the composable does not decide how to load data. It only renders the current state and exposes callbacks for user actions.

**Important:** do not execute business logic and side effects directly in the composable body, because recomposition can happen often, be skipped or be canceled.

**In short:** in declarative UI, the screen is rendered from state; when state changes, we provide new inputs and the framework updates the UI.

### Compose vs View System

The traditional Android View System is imperative: XML describes the initial layout, and code later mutates views by calling methods such as `setText()`, `setVisibility()` or adapter update APIs.

Compose is declarative: UI is described directly in Kotlin as composable functions. When state changes, Compose decides what needs to be recomposed, laid out or redrawn.

This does not mean that the View System is obsolete everywhere. Many production apps use both approaches during migration:

- Compose can be embedded into existing XML / Fragment screens with `ComposeView`.
- Android Views can be embedded into Compose with `AndroidView`.
- New screens can be written in Compose while legacy screens remain on Views.

**In short:** the View System updates existing views imperatively; Compose renders UI from state declaratively and supports gradual migration.

### Composable function

A composable function is a Kotlin function marked with `@Composable` that describes part of UI and can call other composable functions.

A composable does not return a `View`. It participates in Composition: Compose calls composable functions, builds a UI tree and updates it when state changes.

```kotlin
@Composable
fun Greeting(name: String) {
    Text("Hello, $name")
}
```

Important rules: a composable can be called many times, in a different order, or be skipped, so it must be fast and must not perform unexpected side effects. Events use callbacks, and controlled side effects use special APIs such as `LaunchedEffect`.

Avoid doing this directly in a composable body:

- network or database calls;
- starting coroutines without an effect API;
- mutating external state during composition;
- heavy calculations on every recomposition;
- logging or analytics that must happen exactly once.

Instead, keep screen logic in `ViewModel`, expose state to UI, send user actions back through callbacks, and use Compose side-effect APIs only when the effect is truly tied to composition.

**In short:** a composable function describes UI for given inputs; it should be fast, idempotent and free of uncontrolled side effects.

### Compose rendering phases

In Compose, UI is updated through several phases: Composition, Layout and Drawing.

Composition is the phase where Compose calls composable functions and builds or updates the UI tree. This is where Compose determines what should be on screen: which composables are needed, which parameters they receive and what UI structure comes from the current state.

Layout is the phase of measuring and placing elements. Here Compose determines the sizes of UI nodes and their positions on screen. This phase includes measure and placement: first elements are measured with constraints, then placed inside the parent.

Drawing is the rendering phase. Here Compose draws already measured and placed elements: text, background, icons, canvas drawing, draw modifiers and other visual details.

Important point: a state change does not always mean all phases run again. Compose tries to restart only the phases that actually depend on the changed state.

If state is read in the composable body, a change can trigger recomposition, and then layout and drawing if needed. If state is read only in a layout modifier, Compose can skip Composition and go straight to Layout. If state is read only in the draw phase, Compose can limit work to redraw without recomposition and relayout.

For example, if color is read inside `Modifier.drawBehind { drawCircle(color) }`, then when only `color` changes, Compose can run only the Drawing phase because UI structure and layout did not change.

**In short:** Jetpack Compose rendering pipeline has three main phases: Composition, Layout, and Drawing. A state change may restart one or more phases depending on where that state is read.

## Related topics

- [State & Recomposition](state-recomposition.md)
- [Side Effects](side-effects.md)
- [Compose Performance](performance.md)
- [UI State Architecture](../architecture/ui-state.md)
