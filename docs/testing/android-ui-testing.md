# Android UI Testing

Android UI tests verify observable user behavior: the user performs an action and sees the expected state, navigation result or error. Keep most business logic in faster local tests and reserve device tests for behavior that depends on Android UI, lifecycle, resources or integration between screens.

## Test scope and environment

JUnit provides the test lifecycle, assertions and rules, but does not drive Android UI by itself.

- Tests in `src/test` run on the local JVM. They suit pure Kotlin code and can use Robolectric when a simulated Android environment is appropriate.
- Tests in `src/androidTest` run on an emulator or device through an instrumented runner. Espresso and Compose device tests normally live here.

A focused screen test supplies controlled state and fake dependencies. A broader journey test launches the app and verifies several integrated components. Keep the latter set small: it is slower and has more failure points.

## Espresso for Views

Espresso finds `View` objects, performs actions and checks assertions:

```kotlin
onView(withId(R.id.emailInput))
    .perform(typeText("ada@example.com"), closeSoftKeyboard())

onView(withId(R.id.loginButton)).perform(click())
onView(withText("Welcome")).check(matches(isDisplayed()))
```

Espresso waits for the main message queue, `AsyncTask` work and registered `IdlingResource` instances to become idle. It does not automatically know about arbitrary executors, callbacks or external asynchronous work. Prefer controlled fake dependencies; when real asynchronous work must participate, register an idling resource before it starts and unregister it after the test. Avoid `Thread.sleep()` because it is both slow and timing-dependent.

Use stable matchers such as resource IDs and meaningful text or content descriptions. For lists, match a stable item property and perform a RecyclerView action rather than relying on screen coordinates or child positions.

## Compose UI tests

Compose tests interact with the semantics tree rather than the View hierarchy:

```kotlin
@get:Rule
val composeRule = createComposeRule()

@Test
fun savingProfileShowsSuccess() {
    composeRule.setContent {
        ProfileScreen(
            state = ProfileUiState(userName = "Ada"),
            onSave = { }
        )
    }

    composeRule.onNodeWithText("Save").performClick()
    composeRule.onNodeWithText("Saved").assertIsDisplayed()
}
```

Use `createComposeRule()` when the test owns the content. Use `createAndroidComposeRule<Activity>()` when an Activity and Android integration are part of the scenario.

Prefer semantics that also describe the UI to users, such as text, role, content description, selected state and state description. Use `Modifier.testTag()` when no stable user-facing selector exists, but do not treat a tag as an accessibility replacement. If a node cannot be found, inspect the semantics tree and consider whether merged descendants require `useUnmergedTree = true`; do not make unmerged-tree queries the default.

Compose waits for known Compose work and its test clock, but it cannot observe every external asynchronous source. Inject completed or controllable fakes when possible. Use `waitUntil` for observable conditions that genuinely complete outside Compose synchronization, with a bounded timeout.

For deterministic animation tests, control virtual time:

```kotlin
composeRule.mainClock.autoAdvance = false
composeRule.mainClock.advanceTimeBy(300)
```

## Reliable UI tests

- Verify outcomes visible to the user, not private fields, composable structure or exact pixel positions.
- Replace real network, clock and random data with deterministic dependencies.
- Start each test from known app state; do not depend on test order or data left by another test.
- Cover important configuration boundaries deliberately, such as locale, dark theme, font scale and representative window sizes, rather than duplicating every test for every device.
- Use screenshots for diagnostics or dedicated visual regression tooling, not as a substitute for behavioral assertions.
- A flaky test is a defect: identify missing synchronization or shared state instead of adding retries blindly.

Related: [Testing Strategy](strategy.md), [ViewModel Testing](viewmodel-testing.md), [Compose Testing](../compose/testing.md).

Sources: [Android testing fundamentals](https://developer.android.com/training/testing/fundamentals), [Espresso](https://developer.android.com/training/testing/espresso), [Espresso idling resources](https://developer.android.com/training/testing/espresso/idling-resource), [Compose UI testing](https://developer.android.com/develop/ui/compose/testing), [Compose test synchronization](https://developer.android.com/develop/ui/compose/testing/synchronization).
