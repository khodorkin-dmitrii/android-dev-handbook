# Навигация в Jetpack Compose

Навигация определяет не только то, какой экран виден сейчас. Она также задает текущий destination, историю переходов, восстановление состояния и слой UI, который обрабатывает Back.

Для Compose-приложений актуальны два подхода Jetpack:

* **Navigation Compose**, который часто называют **Navigation 2**, использует `NavController`, `NavHost` и граф навигации;
* **Navigation 3** спроектирован специально для Compose: приложение владеет back stack, а `NavDisplay` отображает его состояние.

Navigation 2 остается полноценным production-решением, особенно для существующих приложений и проектов со смешанным View/Compose UI. Для новых Compose-first проектов рекомендуемым направлением является Navigation 3, потому что состояние навигации и его владелец выражены явно.

> Кто в данный момент владеет состоянием навигации и Back?

Это главный архитектурный вопрос для обоих подходов.

## Основные понятия

### Destinations, keys и back stack

Модель навигации обычно включает:

* **destination** - экран или другой навигационный фрагмент контента;
* **route или key** - небольшое типизированное значение, которое идентифицирует destination и содержит его минимальные аргументы;
* **back stack** - упорядоченная последовательность destinations, к которым пользователь может вернуться;
* **переход вперед** - добавление destination;
* **Back** - завершение ближайшего незаконченного взаимодействия или возврат к предыдущему destination;
* **deep link** - внешний или внутренний запрос на открытие destination;
* **navigation state** - активный back stack, выбранный top-level destination и данные, необходимые для восстановления.

Например:

```text
ProductList -> ProductDetail(productId) -> Checkout(orderId)
```

После Back с экрана checkout:

```text
ProductList -> ProductDetail(productId)
```

Навигация остается состоянием, даже если `NavController` скрывает сам back stack.

### Передавайте идентификаторы, а не модели

Routes и keys должны содержать только данные, необходимые для идентификации destination:

```kotlin
ProductDetail(productId = product.id)
```

Не следует передавать целый `Product`, repository, большую коллекцию или изменяемый UI state. Destination должен загрузить актуальные данные по идентификатору. Небольшие сериализуемые контракты проще восстанавливать и тестировать, и они не зависят от устаревших объектов в памяти.

## Navigation Compose - Navigation 2

### Type-safe routes и граф навигации

В Navigation Compose объект `NavController` владеет back stack и изменяет его. Начиная с Navigation `2.8.0`, маршруты в Kotlin можно описывать сериализуемыми объектами и классами вместо строк, сформированных вручную.

```kotlin
@Serializable
data object Products

@Serializable
data class ProductDetails(
    val productId: String,
)
```

`NavHost` связывает типы routes с composable destinations:

```kotlin
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(
        navController = navController,
        startDestination = Products,
    ) {
        composable<Products> {
            ProductsScreen(
                onProductClick = { productId ->
                    navController.navigate(ProductDetails(productId))
                },
            )
        }

        composable<ProductDetails> { backStackEntry ->
            val route = backStackEntry.toRoute<ProductDetails>()

            ProductDetailsScreen(
                productId = route.productId,
                onBack = navController::popBackStack,
            )
        }
    }
}
```

Эта модель предоставляет центральный граф, nested graphs, deep links, сохранение состояния, шаблоны для нескольких back stacks и зрелые средства тестирования.

### Чтение аргументов route во ViewModel

Destination в Navigation 2 может восстановить type-safe route из `SavedStateHandle`, не передавая `NavController` во `ViewModel`:

```kotlin
class ProductDetailsViewModel(
    savedStateHandle: SavedStateHandle,
    private val repository: ProductRepository,
) : ViewModel() {

    private val route = savedStateHandle.toRoute<ProductDetails>()

    val product = repository.observeProduct(route.productId)
}
```

Так загрузка данных зависит от стабильного идентификатора, а не от команд конкретного navigation framework.

### Компромиссы модели с NavController

Navigation 2 - зрелая и функциональная библиотека. Ее главный компромисс связан не с type safety, потому что современный Navigation 2 уже поддерживает type-safe routes. Разница заключается во владении состоянием: приложение отправляет команды, а внутренним состоянием и основным поведением back stack управляет `NavController`.

Такая модель может быть менее прозрачной при нескольких top-level stacks, нестандартных adaptive layouts, вложенных сценариях или нескольких слоях, способных обработать Back. Это не делает подход неправильным - он просто проводит границу ответственности иначе.

## Navigation 3

### Состояние навигации принадлежит приложению

Navigation 3 меняет границу владения состоянием:

```text
UI action -> application-owned back stack -> NavDisplay -> rendered entries
```

Примеры ниже используют актуальные стабильные API Navigation 3. Preview-версии могут добавлять новые удобные API, но модель с keys и back stacks, которыми владеет приложение, остается основной.

Keys, используемые в сохраняемом back stack, реализуют `NavKey` и должны быть сериализуемыми:

```kotlin
@Serializable
sealed interface AppKey : NavKey

@Serializable
data object ProductList : AppKey

@Serializable
data class ProductDetail(
    val productId: String,
) : AppKey

@Serializable
data class Checkout(
    val orderId: String,
) : AppKey
```

`rememberNavBackStack()` создает `NavBackStack`, интегрированный со snapshot state, и восстанавливает сериализуемые keys после configuration change и process recreation:

```kotlin
@Composable
fun AppNavigation() {
    val backStack = rememberNavBackStack(ProductList)

    NavDisplay(
        backStack = backStack,
        onBack = {
            if (backStack.size > 1) {
                backStack.removeLastOrNull()
            }
        },
        entryProvider = entryProvider {
            entry<ProductList> {
                ProductsScreen(
                    onProductClick = { productId ->
                        backStack.add(ProductDetail(productId))
                    },
                )
            }

            entry<ProductDetail> { key ->
                ProductDetailsScreen(
                    productId = key.productId,
                    onCheckout = { orderId ->
                        backStack.add(Checkout(orderId))
                    },
                    onBack = {
                        if (backStack.size > 1) {
                            backStack.removeLastOrNull()
                        }
                    },
                )
            }

            entry<Checkout> { key ->
                CheckoutScreen(
                    orderId = key.orderId,
                    onFinished = {
                        backStack.clear()
                        backStack.add(ProductList)
                    },
                )
            }
        },
    )
}
```

Переход вперед добавляет key; Back удаляет текущий key или завершает связанное с ним состояние другим способом. Приложение должно явно определить правила работы back stack, а не рассчитывать, что controller выведет их автоматически.

Для `ViewModel`, привязанной к отдельному destination, Navigation 3 предоставляет интеграцию `lifecycle-viewmodel-navigation3` и entry decorators. Эту интеграцию стоит добавлять только тогда, когда действительно нужен scope `ViewModel`, связанный с конкретной entry.

### Сравнение Navigation 2 и Navigation 3

| Navigation 2 | Navigation 3 |
|---|---|
| `NavController` владеет своим stack и изменяет его | Приложение владеет stacks и изменяет их |
| `NavHost` отображает граф | `NavDisplay` отображает entries |
| Навигацией управляют команды controller | Навигацией управляют обновления state |
| Поддерживает type-safe routes | Использует typed navigation keys |
| Несколько stacks реализуются через save/restore controller | Несколько stacks являются явным состоянием приложения |
| В основном моделирует один текущий destination | Scenes могут отображать несколько entries |
| Зрелая поддержка Compose, Fragments и mixed UI | Compose-first API и явная модель владения состоянием |

Navigation 3 - это не Navigation 2 с переименованными методами. Он дает приложению больше контроля и больше ответственности за восстановление, top-level stacks и правила Back.

## Владение навигацией в архитектуре приложения

### Не связывайте экраны с navigation library

Экранные composable-функции обычно должны получать данные и callbacks:

```kotlin
@Composable
fun ProductsScreen(
    onProductClick: (String) -> Unit,
) {
    // UI calls onProductClick(productId)
}
```

Практичное разделение ответственности:

* `ViewModel` определяет требуемый смысловой результат;
* слой UI/навигации преобразует его в конкретный переход;
* владелец navigation state централизует правила изменения back stack для сложных сценариев.

Не следует помещать `NavController`, Android navigation types или произвольные изменения back stack глубоко в экранную `ViewModel`. Для непосредственного действия пользователя проще использовать callback. Для асинхронного результата `ViewModel` может публиковать смысловой effect, который UI обрабатывает с учетом lifecycle. См. [Side Effects](side-effects.md), [UI State Architecture](../architecture/ui-state.md) и [Lifecycle-aware Collection](../coroutines-flow/lifecycle-aware-collection.md).

### Back - это контракт владения

Back не всегда означает «удалить destination из back stack». Сначала экрану может потребоваться закрыть:

* dialog, bottom sheet или drawer;
* режим поиска, выбора или редактирования;
* диалог подтверждения для несохраненной формы;
* nested navigation flow.

Практический порядок:

1. Ближайший видимый временный UI-слой закрывает себя.
2. Активный экран завершает временный UI state.
3. Навигация возвращается к предыдущему значимому destination.
4. Финальное действие Back обрабатывает Activity или система.

Каждый слой перехватывает Back только пока владеет незавершенным взаимодействием:

```kotlin
BackHandler(enabled = uiState.isSelectionMode) {
    viewModel.exitSelectionMode()
}
```

Разрозненные всегда активные `BackHandler` создают скрытые правила приоритета. Лучше иметь небольшое количество обработчиков с явными условиями `enabled` и одного владельца переходов между destinations.

### Несохраненные изменения

Несохраненную работу нужно моделировать как явный UI state:

```kotlin
data class EditorUiState(
    val text: String = "",
    val originalText: String = "",
    val showDiscardConfirmation: Boolean = false,
) {
    val hasUnsavedChanges: Boolean
        get() = text != originalText
}
```

Редактор может перехватывать Back только при наличии несохраненных изменений:

```kotlin
BackHandler(
    enabled = uiState.hasUnsavedChanges &&
        !uiState.showDiscardConfirmation,
) {
    viewModel.requestDiscardConfirmation()
}
```

Пока диалог видим, Back принадлежит ему. После сохранения или отказа от изменений навигация возвращается к обычному поведению.

## Predictive Back

Predictive Back во время жеста показывает состояние или destination за текущим UI-слоем. `NavDisplay` и актуальные версии Navigation Compose интегрируются с системным Back, но пользовательские обработчики и transitions должны сохранять те же правила владения.

При проверке важно рассматривать весь сценарий:

* совпадает ли preview с конечным destination;
* обрабатывает ли Back только ближайший подходящий слой;
* закрываются ли dialogs, sheets и drawers до перехода между destinations;
* защищены ли несохраненные изменения;
* согласованы ли пользовательские transitions с прогрессом жеста?

Predictive Back не создает противоречия в навигации. Он лишь делает неясное владение заметным.

## Несколько back stacks и adaptive navigation

### Несколько top-level stacks

Для bottom navigation часто требуется отдельный stack для каждого top-level destination:

```kotlin
@Serializable
data object Home : NavKey

@Serializable
data object Search : NavKey

@Serializable
data object Profile : NavKey

enum class TopLevelTab { Home, Search, Profile }

val homeStack = rememberNavBackStack(Home)
val searchStack = rememberNavBackStack(Search)
val profileStack = rememberNavBackStack(Profile)

var selectedTab by rememberSaveable {
    mutableStateOf(TopLevelTab.Home)
}

val activeStack = when (selectedTab) {
    TopLevelTab.Home -> homeStack
    TopLevelTab.Search -> searchStack
    TopLevelTab.Profile -> profileStack
}
```

Переключение вкладки выбирает другой stack, не удаляя остальные. Back обычно сначала удаляет entry из активного stack; требования продукта определяют, должен ли Back в корне этого stack выбрать вкладку по умолчанию или закрыть приложение.

В Navigation 2 это реализуется через navigation options объекта `NavController`: `popUpTo`, `saveState`, `launchSingleTop` и `restoreState`. Navigation 3 предоставляет прямой доступ к stacks. В обоих случаях у выбора top-level destination и правил Back должен быть один понятный владелец.

### Adaptive layouts и scenes

В компактном окне список и детали обычно отображаются последовательно:

```text
List -> Detail
```

В большом окне они могут отображаться одновременно:

```text
| List | Detail |
```

Scenes и scene strategies в Navigation 3 могут отображать несколько `NavEntry`. Navigation keys при этом остаются прежними, а представление адаптируется к доступному пространству. Не следует переносить ветвление phone/tablet в business logic: navigation state описывает, где находится пользователь, а layout strategy определяет количество видимых entries.

## Deep links

Deep link должен преобразовываться в ту же type-safe модель навигации, что и внутреннее действие:

1. Распарсить и проверить URI.
2. Преобразовать его в route или key.
3. Проверить authentication и другие предварительные условия.
4. Построить или обновить осмысленный back stack.
5. Открыть destination с предсказуемым поведением Back.

Для ссылки на товар лучше построить:

```text
ProductList -> ProductDetail(productId)
```

чем открыть изолированный экран деталей без понятного родительского destination. Navigation 2 позволяет объявлять deep links в графе. В Navigation 3 независимо от того, выполняет URI matching код приложения или API библиотеки, результатом должны быть проверенные keys, которыми владеет приложение, а не отдельная модель навигации.

## Тестирование навигации

Поведение экрана следует проверять отдельно от правил работы stack. Тест экрана проверяет callback:

```kotlin
@Test
fun clickingProductRequestsNavigation() {
    var selectedId: String? = null

    composeTestRule.setContent {
        ProductsScreen(onProductClick = { selectedId = it })
    }

    composeTestRule.onNodeWithText("Coffee").performClick()

    assertThat(selectedId).isEqualTo("coffee")
}
```

В Navigation 3 нетривиальные операции лучше вынести в небольшой state holder и проверять его наблюдаемый stack с помощью unit tests:

```kotlin
class AppNavigator(
    val backStack: MutableList<AppKey>,
) {
    fun openProduct(productId: String) {
        backStack.add(ProductDetail(productId))
    }

    fun goBack(): Boolean {
        if (backStack.size <= 1) return false
        backStack.removeLast()
        return true
    }
}
```

Следует покрыть тестами start destination, переходы вперед, Back на каждом слое, восстановление, переключение top-level stacks, deep links, несохраненные изменения, transient surfaces, Predictive Back и authentication redirects. Принципы UI testing разобраны в [Compose Testing](testing.md) и [Android UI Testing](../testing/android-ui-testing.md).

## Миграция и практический выбор

### Мигрируйте осознанно

Переход с Navigation 2 на Navigation 3 обычно включает:

1. Заменить оставшиеся string routes на type-safe routes.
2. Сделать существующие routes реализациями `NavKey` или определить эквивалентные Navigation 3 keys.
3. Ввести navigation state holder и сохраняемые stacks.
4. Перенести destinations из `NavHost` в entry provider и `NavDisplay`.
5. Явно воспроизвести несколько stacks, dialogs, возврат результатов и adaptive behavior.
6. Проверить восстановление состояния, deep links и поведение каждого потенциального владельца Back.
7. Удалить Navigation 2 только после покрытия эквивалентного поведения тестами.

Navigation 3 работает только с Compose. Проекту с большим количеством Fragments или mixed UI стоит мигрировать, только если новая модель владения приносит достаточно пользы.

### Какой подход выбрать?

Выбирайте **Navigation 2**, если:

* приложение уже успешно его использует;
* проект объединяет Fragments и Compose;
* важнее зрелые интеграции и существующее поведение графа;
* миграция добавит риск, не решая конкретную проблему.

Выбирайте **Navigation 3**, если:

* проект новый и Compose-first;
* важно явное владение back stack;
* ключевую роль играют несколько stacks или adaptive layouts;
* navigation-as-state соответствует архитектуре;
* команда готова явно управлять восстановлением и правилами Back.

Для нового Compose-first приложения стоит начинать с Navigation 3. Не следует мигрировать стабильное приложение с Navigation 2 только потому, что существует более новая библиотека.

## Практические правила

* Используйте type-safe routes или keys.
* Передавайте идентификаторы, а не полные модели.
* Не помещайте типы navigation framework в экранную `ViewModel`.
* Сохраняйте navigation state и явно моделируйте несколько stacks.
* Back должен обрабатывать ближайший подходящий владелец.
* Отделяйте закрытие временных UI-слоев от переходов между destinations.
* Deep links должны создавать валидный navigation state приложения.
* Тестируйте переходы stack, восстановление и поведение Back.

**Главная мысль:** библиотека важна, но предсказуемая навигация начинается с ясного ответа на вопрос: "Кто в данный момент владеет состоянием навигации и Back?"

## См. также

* [State & Recomposition](state-recomposition.md)
* [Side Effects](side-effects.md)
* [UI State Architecture](../architecture/ui-state.md)
* [Activity, Fragment & Lifecycle](../android/activity-fragment-lifecycle.md) - содержит контекст по владению `ViewModel` и восстановлению состояния
* [Lifecycle-aware Collection](../coroutines-flow/lifecycle-aware-collection.md)
* [Compose Testing](testing.md)

## Дополнительные материалы

* [Navigation 3 overview](https://developer.android.com/guide/navigation/navigation-3)
* [Navigation 3 basics](https://developer.android.com/guide/navigation/navigation-3/basics)
* [Save and manage Navigation 3 state](https://developer.android.com/guide/navigation/navigation-3/save-state)
* [Migrate from Navigation 2 to Navigation 3](https://developer.android.com/guide/navigation/navigation-3/migration-guide)
* [Type safety in Navigation Compose](https://developer.android.com/guide/navigation/design/type-safety)
* [Predictive Back in Compose](https://developer.android.com/develop/ui/compose/system/predictive-back)