# Compose Basics

Jetpack Compose - a modern declarative UI toolkit for Android. Instead of manually changing the View tree, we describe UI as a function of state, and Compose updates the necessary parts of the interface when data changes.

## Compose basics

### What is Jetpack Compose?

Compose is used to build screens in Kotlin without XML and integrates well with `ViewModel`, `Flow` / `StateFlow`, Material Design, Navigation and testing APIs.

The main mental model: a composable should be fast, idempotent and side-effect free. Do not think that Compose fully redraws the whole screen every time: it tries to skip unchanged parts.

**In short:** Jetpack Compose lets us build Android UI declaratively: UI is a function of state, and Compose recomposes affected parts when state changes.

### Declarative UI

Declarative UI - an approach where code describes how UI should look for the current state, not which step-by-step commands should be executed to manually change the screen.

In the imperative View System, we often call `setText()`, `setVisibility()`, `notifyDataSetChanged()`. In Compose, we pass new state into a composable, and UI is rebuilt as a result of that state.

The practical benefit is simpler reasoning about loading/content/error, forms, lists and state-driven screens.

**Important:** do not execute business logic and side effects directly in the composable body, because recomposition can happen often, be skipped or be canceled.

**In short:** in declarative UI, the screen is rendered from state; when state changes, we provide new inputs and the framework updates the UI.

### Composable function

Composable function - a Kotlin function marked with `@Composable` that describes part of UI and can call other composable functions.

A composable does not return a `View`. It participates in Composition: Compose calls composable functions, builds a UI tree and updates it when state changes.

```kotlin
@Composable
fun Greeting(name: String) {
    Text("Hello, $name")
}
```

Important rules: a composable can be called many times, in a different order, or be skipped, so it must be fast and must not perform unexpected side effects. Events use callbacks, and controlled side effects use special APIs such as `LaunchedEffect`.

**In short:** a composable function describes UI for given inputs; it should be fast, idempotent and free of uncontrolled side effects.

### Compose rendering phases

In Compose, UI is updated through several phases: Composition, Layout and Drawing.

Composition - the phase where Compose calls composable functions and builds or updates the UI tree. This is where Compose determines what should be on screen: which composables are needed, which parameters they receive and what UI structure comes from the current state.

Layout - the phase of measuring and placing elements. Here Compose determines the sizes of UI nodes and their positions on screen. This phase includes measure and placement: first elements are measured with constraints, then placed inside the parent.

Drawing - the rendering phase. Here Compose draws already measured and placed elements: text, background, icons, canvas drawing, draw modifiers and other visual details.

Important point: a state change does not always mean all phases run again. Compose tries to restart only the phases that actually depend on the changed state.

If state is read in the composable body, a change can trigger recomposition, and then layout and drawing if needed. If state is read only in a layout modifier, Compose can skip Composition and go straight to Layout. If state is read only in the draw phase, Compose can limit work to redraw without recomposition and relayout.

For example, if color is read inside `Modifier.drawBehind { drawCircle(color) }`, then when only `color` changes, Compose can run only the Drawing phase because UI structure and layout did not change.

**In short:** Jetpack Compose rendering pipeline has three main phases: Composition, Layout, and Drawing. A state change may restart one or more phases depending on where that state is read.
