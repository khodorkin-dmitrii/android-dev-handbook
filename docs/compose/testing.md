# Compose Testing

Compose UI tests проверяют пользовательское поведение через Compose testing framework и semantics tree, а не через прямой доступ к composable functions.

## UI tests и Semantics

### Compose UI tests

Обычно тест строится вокруг `createComposeRule()` или `createAndroidComposeRule<Activity>()`, затем задаётся content, ищется node и выполняется assertion/action.

```kotlin
composeTestRule
    .onNodeWithText("Save")
    .assertIsDisplayed()
    .performClick()
```

Для более стабильных тестов часто используют `testTag`:

```kotlin
Modifier.testTag("save_button")
```

```kotlin
composeTestRule
    .onNodeWithTag("save_button")
    .performClick()
```

Compose tests синхронизируются с Compose runtime: тест обычно ждёт idle state, но для анимаций, корутин, clock control и внешних async sources иногда нужно явно управлять `mainClock`, test dispatcher или idling.

**Важно:** не стоит проверять implementation details. Хороший UI test проверяет observable behavior: текст, accessibility role/state, enabled/disabled, navigation result, отображение loading/error/content.

**Коротко:** Compose UI tests interact with the semantics tree; they should verify user-visible behavior, not internal composable implementation.

### Semantics

Semantics - это слой метаданных, который описывает смысл UI node для accessibility, testing и tooling.

Compose testing API ищет элементы не по View id, а по semantics properties: text, `contentDescription`, role, `stateDescription`, `testTag`, enabled/clickable и другим признакам.

Semantics важны не только для тестов, но и для accessibility: screen readers используют эту информацию, чтобы пользователь понимал, что находится на экране и как с этим взаимодействовать.

`Modifier.semantics { ... }` позволяет добавить или переопределить semantics properties. `Modifier.clearAndSetSemantics { ... }` полностью заменяет semantics descendants и полезен, когда сложный визуальный компонент должен восприниматься как один accessibility element.

`Modifier.testTag("...")` удобно использовать для тестов, когда текст нестабилен из-за локализации или UI содержит одинаковые строки. Но `testTag` не должен быть единственным способом описания UI для accessibility.

**Важно:** merged и unmerged semantics trees могут отличаться. Иногда тест не находит node, потому что semantics объединены родителем; тогда нужно понять, искать ли в merged tree или использовать `useUnmergedTree = true`.

**Коротко:** semantics describe UI meaning for accessibility and tests; Compose UI tests query semantics instead of view hierarchy.
