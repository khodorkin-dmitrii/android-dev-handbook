# Compose Testing

UI-тесты Compose проверяют наблюдаемое поведение через дерево semantics, а не внутреннее устройство composable-функций. Общая стратегия и тестирование View UI рассмотрены в [Android UI Testing](../testing/android-ui-testing.ru.md).

## UI-тесты Compose

Используйте `createComposeRule()`, если тест сам задаёт содержимое, или `createAndroidComposeRule<Activity>()`, если нужен Activity. После `setContent` найдите semantics node, выполните действие и проверьте результат:

```kotlin
var saved = false
composeTestRule.setContent { EditorScreen(onSave = { saved = true }) }
composeTestRule.onNodeWithText("Save").performClick()
assertThat(saved).isTrue()
```

Предпочитайте свойства, полезные и пользователю: текст, роль, состояние выбора, `contentDescription`. Если они неоднозначны или зависят от локализации, добавьте стабильный `testTag`:

```kotlin
Modifier.testTag("save_button")
```

```kotlin
composeTestRule
    .onNodeWithTag("save_button")
    .performClick()
```

Действия и проверки обычно ждут, пока Compose станет idle. `mainClock` управляет recomposition и анимациями Compose, но не всеми Android draw passes и внешними асинхронными операциями. Для внешней работы используйте управляемые fakes; при необходимости ждите наблюдаемое условие через `waitUntil` с ограничением времени или зарегистрируйте idling resource. Для проверки хода анимации управляйте clock явно.

Проверяйте поведение, видимое пользователю: доступность действия, выбор, состояния загрузки/ошибки/контента, callback или результат навигации. Не привязывайте тест к приватному состоянию или точной форме дерева composables.

## Semantics

Semantics описывают смысл UI-элементов для accessibility, тестирования и инструментов. Тесты Compose ищут свойства semantics, а не View ID. Многие стандартные компоненты предоставляют нужные свойства автоматически.

`Modifier.semantics { ... }` добавляет свойства. `Modifier.clearAndSetSemantics { ... }` заменяет semantics дочерних элементов: используйте его, только если объединённый компонент сохранил нужные пользователю подпись, роль, состояние и действия. Один `testTag` не заменяет accessibility-подпись.

По умолчанию тесты используют **merged tree**. Если дочерний элемент не находится, изучите дерево через `onRoot().printToLog("ComposeTest")`; включайте `useUnmergedTree = true`, только если нужно проверить именно ребёнка. Если весь компонент представляет одно действие, лучше взаимодействовать с родительским элементом.

См. также: [Android UI Testing](../testing/android-ui-testing.ru.md), [Стратегия тестирования](../testing/strategy.ru.md).

Источники: [тестирование Compose](https://developer.android.com/develop/ui/compose/testing), [Testing APIs](https://developer.android.com/develop/ui/compose/testing/apis), [синхронизация тестов](https://developer.android.com/develop/ui/compose/testing/synchronization).
