# Compose Testing

Compose UI tests verify observable behavior through the semantics tree. They do not inspect composable functions directly. For the broader test strategy and View-based UI tests, see [Android UI Testing](../testing/android-ui-testing.md).

## Compose UI tests

A test uses `createComposeRule()` when it supplies its own content, or `createAndroidComposeRule<Activity>()` when the scenario needs an Activity. After `setContent`, find a semantics node, act on it, and assert the resulting UI state:

```kotlin
var saved = false
composeTestRule.setContent { EditorScreen(onSave = { saved = true }) }
composeTestRule.onNodeWithText("Save").performClick()
assertThat(saved).isTrue()
```

Prefer user-facing semantics such as text, role, selected state, or content description. Use a `testTag` for a stable selector when those properties are ambiguous or localized:

```kotlin
Modifier.testTag("save_button")
```

```kotlin
composeTestRule
    .onNodeWithTag("save_button")
    .performClick()
```

Actions and assertions normally wait for Compose to become idle. `mainClock` controls Compose recomposition and animations, but not every Android draw pass or external asynchronous operation. Use controllable fakes for external work; if necessary, wait for an observable condition with a bounded `waitUntil` or register an idling resource. Control the clock explicitly when testing animation progress.

Test the behavior a user can observe: enabled state, selection, loading/error/content, and callbacks or navigation outcomes. Avoid assertions about private state or a particular composable tree shape.

## Semantics

Semantics describe the meaning of UI nodes for accessibility, testing, and tooling. Compose tests query semantics properties, not View IDs. Many built-in components provide useful properties automatically.

`Modifier.semantics { ... }` adds properties. `Modifier.clearAndSetSemantics { ... }` replaces the semantics exposed by a subtree: use it only when the combined control still has the label, role, state, and actions users need. A `testTag` alone is not an accessibility label.

Tests use the **merged tree** by default. If a child cannot be found, inspect the tree with `onRoot().printToLog("ComposeTest")`; use `useUnmergedTree = true` only when the child is intentionally tested separately. Prefer to interact with the parent control when it represents one user action.

Related: [Android UI Testing](../testing/android-ui-testing.md), [Testing Strategy](../testing/strategy.md).

Sources: [Compose testing](https://developer.android.com/develop/ui/compose/testing), [Testing APIs](https://developer.android.com/develop/ui/compose/testing/apis), [Test synchronization](https://developer.android.com/develop/ui/compose/testing/synchronization).
