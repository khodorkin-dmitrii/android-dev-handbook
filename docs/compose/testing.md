# Compose Testing

Compose UI tests verify user behavior through the Compose testing framework and semantics tree, not through direct access to composable functions.

## UI tests and Semantics

### Compose UI tests

A test is usually built around `createComposeRule()` or `createAndroidComposeRule<Activity>()`, then content is set, a node is found and an assertion/action is performed.

```kotlin
composeTestRule
    .onNodeWithText("Save")
    .assertIsDisplayed()
    .performClick()
```

For more stable tests, `testTag` is often used:

```kotlin
Modifier.testTag("save_button")
```

```kotlin
composeTestRule
    .onNodeWithTag("save_button")
    .performClick()
```

Compose tests synchronize with Compose runtime: a test usually waits for idle state, but animations, coroutines, clock control and external async sources sometimes require explicit control of `mainClock`, test dispatcher or idling.

**Important:** do not test implementation details. A good UI test verifies observable behavior: text, accessibility role/state, enabled/disabled, navigation result, loading/error/content display.

**In short:** Compose UI tests interact with the semantics tree; they should verify user-visible behavior, not internal composable implementation.

### Semantics

Semantics - a metadata layer that describes the meaning of a UI node for accessibility, testing and tooling.

Compose testing API searches elements not by View id, but by semantics properties: text, `contentDescription`, role, `stateDescription`, `testTag`, enabled/clickable and other signals.

Semantics matter not only for tests, but also for accessibility: screen readers use this information so the user understands what is on screen and how to interact with it.

`Modifier.semantics { ... }` allows adding or overriding semantics properties. `Modifier.clearAndSetSemantics { ... }` fully replaces semantics descendants and is useful when a complex visual component should be perceived as one accessibility element.

`Modifier.testTag("...")` is convenient for tests when text is unstable because of localization or UI contains repeated strings. But `testTag` should not be the only way to describe UI for accessibility.

**Important:** merged and unmerged semantics trees can differ. Sometimes a test cannot find a node because semantics are merged by the parent; then you need to decide whether to search in the merged tree or use `useUnmergedTree = true`.

**In short:** semantics describe UI meaning for accessibility and tests; Compose UI tests query semantics instead of view hierarchy.
