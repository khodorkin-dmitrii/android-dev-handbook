# Android UI Testing

This section covers Android UI testing: Espresso, Compose UI tests, JUnit and observable behavior checks for user scenarios.

## UI testing tools

### Espresso

Espresso is an Android UI testing framework for the View System. It lets tests find `View`, perform user actions and verify UI state.

Basic Espresso style:

```kotlin
onView(withId(R.id.emailInput))
    .perform(typeText("ada@example.com"))

onView(withId(R.id.loginButton))
    .perform(click())

onView(withText("Welcome"))
    .check(matches(isDisplayed()))
```

Espresso synchronizes with the main thread and standard Android UI operations, so manual waiting for rendering is often unnecessary. But external async work, custom executors, network or background jobs may require `IdlingResource` or a controlled fake dependency.

A good Espresso test checks user-visible behavior: text, enabled/disabled state, navigation result, error message, item in list. It should not check private implementation details.

Typical pitfalls:

- real network calls in UI tests;
- `Thread.sleep`;
- overly precise layout detail checks;
- unstable matchers for RecyclerView;
- tests that depend on run order or shared app state.

**In short:** Espresso fits XML/View UI tests and verifies behavior through View hierarchy, actions and matchers.

### Compose UI tests

Compose UI tests work through the semantics tree, not the View hierarchy. A test finds nodes by text, content description, role, state, testTag and other semantics properties.

Basic example:

```kotlin
@get:Rule
val composeRule = createComposeRule()

@Test
fun saveButtonIsDisplayed() {
    composeRule.setContent {
        ProfileScreen(
            state = ProfileUiState(userName = "Ada"),
            onAction = {}
        )
    }

    composeRule
        .onNodeWithText("Save")
        .assertIsDisplayed()
}
```

For elements where text is unstable because of localization or several identical strings exist, use `testTag`:

```kotlin
Button(
    modifier = Modifier.testTag("save_button"),
    onClick = onSave
) {
    Text("Save")
}
```

```kotlin
composeRule
    .onNodeWithTag("save_button")
    .performClick()
```

Compose tests automatically wait for the idle state of the Compose runtime. For animations, the clock can be controlled:

```kotlin
composeRule.mainClock.autoAdvance = false
composeRule.mainClock.advanceTimeBy(300)
```

**Important:** `testTag` is convenient for tests, but accessibility should still be described through meaningful semantics: text, role, content description, state description.

**In short:** Compose UI tests verify UI through the semantics tree; test user-visible behavior rather than internal composable structure.

### JUnit

JUnit is the base test framework on which unit tests and many Android tests are usually built. It provides `@Test`, assertions, rules, lifecycle hooks and Gradle/IDE integration.

In Android there are usually two levels:

- local unit tests in `src/test`, which run on the JVM without a device;
- instrumented tests in `src/androidTest`, which run on an emulator/device and have access to the Android framework.

Example of a simple JUnit test:

```kotlin
class EmailValidatorTest {

    @Test
    fun `valid email returns true`() {
        val validator = EmailValidator()

        assertTrue(validator.isValid("ada@example.com"))
    }
}
```

JUnit rules are useful for repeated setup, for example replacing `Dispatchers.Main`, creating a temporary folder or configuring a Compose/Espresso rule.

JUnit itself does not perform Android UI testing. UI needs Espresso, Compose testing APIs, Robolectric or an instrumented test runner, depending on the scenario.

**In short:** JUnit is the foundation for tests; Android-specific behavior is added by rules, runners and testing libraries on top of it.
