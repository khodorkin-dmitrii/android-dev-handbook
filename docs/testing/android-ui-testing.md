# Android UI Testing

Раздел про Android UI testing: Espresso, Compose UI tests, JUnit и проверку observable behavior пользовательских сценариев.

## UI testing tools

### Espresso

Espresso - Android UI testing framework для View System. Он позволяет находить `View`, выполнять user actions и проверять состояние UI.

Базовый стиль Espresso:

```kotlin
onView(withId(R.id.emailInput))
    .perform(typeText("ada@example.com"))

onView(withId(R.id.loginButton))
    .perform(click())

onView(withText("Welcome"))
    .check(matches(isDisplayed()))
```

Espresso синхронизируется с main thread и стандартными Android UI operations, поэтому часто не нужно вручную ждать отрисовку. Но для внешней async-работы, custom executors, network или background jobs может понадобиться `IdlingResource` или controlled fake dependency.

Хороший Espresso test проверяет user-visible behavior: текст, enabled/disabled state, navigation result, error message, item in list. Он не должен проверять private implementation details.

Типичные pitfalls:

- реальные network calls в UI tests;
- `Thread.sleep`;
- слишком точные проверки layout details;
- нестабильные matchers для RecyclerView;
- tests, которые зависят от порядка запуска или общего state приложения.

**Коротко:** Espresso подходит для XML/View UI tests и проверяет поведение через View hierarchy, actions и matchers.

### Compose UI tests

Compose UI tests работают через semantics tree, а не через View hierarchy. Тест ищет nodes по text, content description, role, state, testTag и другим semantics properties.

Базовый пример:

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

Для элементов, где текст нестабилен из-за локализации или есть несколько одинаковых строк, используют `testTag`:

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

Compose tests автоматически ждут idle state Compose runtime. Для анимаций можно управлять clock:

```kotlin
composeRule.mainClock.autoAdvance = false
composeRule.mainClock.advanceTimeBy(300)
```

**Важно:** `testTag` удобен для тестов, но accessibility всё равно должна описываться смысловыми semantics: text, role, content description, state description.

**Коротко:** Compose UI tests проверяют UI через semantics tree; лучше тестировать user-visible behavior, а не внутреннюю структуру composable.

### JUnit

JUnit - базовый test framework, на котором обычно строятся unit tests и многие Android tests. Он даёт `@Test`, assertions, rules, lifecycle hooks и интеграцию с Gradle/IDE.

В Android обычно встречаются два уровня:

- local unit tests в `src/test`, которые запускаются на JVM без устройства;
- instrumented tests в `src/androidTest`, которые запускаются на emulator/device и имеют доступ к Android framework.

Пример простого JUnit test:

```kotlin
class EmailValidatorTest {

    @Test
    fun `valid email returns true`() {
        val validator = EmailValidator()

        assertTrue(validator.isValid("ada@example.com"))
    }
}
```

JUnit rules полезны для повторяющейся настройки, например подменить `Dispatchers.Main`, создать temporary folder или настроить Compose/Espresso rule.

JUnit сам по себе не делает Android UI testing. Для UI нужны Espresso, Compose testing APIs, Robolectric или instrumented test runner, в зависимости от сценария.

**Коротко:** JUnit - foundation для tests; Android-specific поведение добавляют rules, runners и testing libraries поверх него.
