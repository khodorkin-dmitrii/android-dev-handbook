# Navigation in Jetpack Compose

Navigation defines more than which screen is visible. It also defines the current destination, the history a user can return through, state restoration, and which UI layer handles Back.

Compose applications currently have two relevant Jetpack approaches:

* **Navigation Compose**, often called **Navigation 2**, uses `NavController`, `NavHost`, and a navigation graph;
* **Navigation 3** is Compose-first: the application owns the back stack and `NavDisplay` renders it.

Navigation 2 remains a valid production choice, especially in established or mixed View/Compose applications. For new Compose-first projects, Navigation 3 is the recommended direction because navigation state and its ownership are explicit.

> Who owns navigation state and Back at this moment?

This question is the central architectural rule for both approaches.

## Core concepts

### Destinations, keys, and back stacks

A navigation model usually contains:

* **destination** - a screen or another navigable piece of content;
* **route or key** - a small typed value that identifies a destination and its arguments;
* **back stack** - an ordered collection of destinations the user can return to;
* **forward navigation** - adding a destination;
* **Back** - resolving the closest unfinished interaction or returning to the previous destination;
* **deep link** - an external or internal request to open a destination;
* **navigation state** - the active stack, selected top-level destination, and restoration data.

For example:

```text
ProductList -> ProductDetail(productId) -> Checkout(orderId)
```

After Back from checkout:

```text
ProductList -> ProductDetail(productId)
```

Even when a controller hides the list, navigation is still state.

### Pass identifiers, not models

Routes and keys should contain the minimum data required to identify a destination:

```kotlin
ProductDetail(productId = product.id)
```

Do not pass a full `Product`, repository, large collection, or mutable UI state. The destination should load current data using the identifier. Small serializable contracts are easier to restore, test, and keep independent from stale in-memory objects.

## Navigation Compose - Navigation 2

### Type-safe routes and a navigation graph

Navigation Compose lets `NavController` own and mutate the back stack. Since Navigation `2.8.0`, Kotlin routes can be represented by serializable objects and classes instead of manually encoded strings.

```kotlin
@Serializable
data object Products

@Serializable
data class ProductDetails(
    val productId: String,
)
```

`NavHost` maps route types to composable destinations:

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

This model provides a central graph, nested graphs, deep links, saved-state options, multiple-back-stack patterns, and mature testing support.

### Read route arguments in a ViewModel

A Navigation 2 destination can reconstruct a type-safe route from `SavedStateHandle` without giving its `ViewModel` access to `NavController`:

```kotlin
class ProductDetailsViewModel(
    savedStateHandle: SavedStateHandle,
    private val repository: ProductRepository,
) : ViewModel() {

    private val route = savedStateHandle.toRoute<ProductDetails>()

    val product = repository.observeProduct(route.productId)
}
```

This keeps data loading dependent on a stable identifier rather than navigation framework commands.

### Trade-offs of controller ownership

Navigation 2 is mature and capable. Its main trade-off is not type safety, because modern Navigation 2 already has type-safe routes. The difference is ownership: the application sends commands, while `NavController` owns most stack behavior internally.

That model can become less explicit with multiple top-level stacks, custom adaptive layouts, nested flows, or several layers that may consume Back. It is not incorrect - it simply offers a different boundary.

## Navigation 3

### Application-owned navigation state

Navigation 3 reverses the ownership boundary:

```text
UI action -> application-owned back stack -> NavDisplay -> rendered entries
```

The examples below use the current stable Navigation 3 APIs. Preview releases may add conveniences, but application-owned keys and stacks remain the core model.

Keys used with the saveable back stack implement `NavKey` and are serializable:

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

`rememberNavBackStack()` creates a snapshot-aware `NavBackStack` and restores serializable keys after configuration change and process recreation:

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

Forward navigation adds a key; Back removes or otherwise resolves the current key. The application must define stack policies deliberately instead of assuming a controller will infer them.

For per-destination `ViewModel` scope, Navigation 3 provides the `lifecycle-viewmodel-navigation3` integration and entry decorators. Add that integration only when entry-scoped `ViewModel` ownership is required.

### Navigation 2 and Navigation 3 compared

| Navigation 2 | Navigation 3 |
|---|---|
| `NavController` owns and mutates its stack | The application owns and mutates stacks |
| `NavHost` renders a graph | `NavDisplay` renders entries |
| Controller commands drive navigation | State updates drive navigation |
| Supports type-safe routes | Uses typed navigation keys |
| Multiple stacks use controller save/restore patterns | Multiple stacks are explicit application state |
| Primarily models one current destination | Scenes can render multiple entries |
| Mature support for Compose, Fragments, and mixed apps | Compose-first API and ownership model |

Navigation 3 is not Navigation 2 with renamed methods. It gives the application more control and more responsibility for restoration, top-level stacks, and Back policy.

## Navigation ownership in application architecture

### Keep screens independent from the navigation library

Screen composables should usually receive data and callbacks:

```kotlin
@Composable
fun ProductsScreen(
    onProductClick: (String) -> Unit,
) {
    // UI calls onProductClick(productId)
}
```

A useful separation is:

* the `ViewModel` decides the semantic outcome;
* the UI/navigation layer translates it into a navigation operation;
* a navigation state holder centralizes stack policies when flows become complex.

Do not place `NavController`, Android navigation types, or arbitrary stack mutations deep inside screen-level `ViewModel`s. Direct callbacks are preferable for immediate user actions. For asynchronous results, a `ViewModel` can publish a semantic effect that the UI handles with a lifecycle-aware collector. See [Side Effects](side-effects.md), [UI State Architecture](../architecture/ui-state.md), and [Lifecycle-aware Collection](../coroutines-flow/lifecycle-aware-collection.md).

### Back is an ownership contract

Back does not always mean "pop a destination." A screen may first need to close:

* a dialog, bottom sheet, or drawer;
* search, selection, or edit mode;
* an unsaved form confirmation;
* a nested navigation flow.

A practical priority is:

1. The closest visible transient surface dismisses itself.
2. The focused screen resolves temporary UI state.
3. Navigation returns to the previous meaningful destination.
4. The Activity or system handles the final Back action.

Each layer consumes Back only while it owns an unfinished interaction:

```kotlin
BackHandler(enabled = uiState.isSelectionMode) {
    viewModel.exitSelectionMode()
}
```

Scattered always-enabled `BackHandler`s create hidden priority rules. Prefer a small number of handlers with explicit `enabled` conditions and a single owner for destination navigation.

### Unsaved changes

Unsaved work should be explicit UI state:

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

The editor can intercept Back only while it has unsaved changes:

```kotlin
BackHandler(
    enabled = uiState.hasUnsavedChanges &&
        !uiState.showDiscardConfirmation,
) {
    viewModel.requestDiscardConfirmation()
}
```

While visible, the confirmation dialog owns Back. After the work is saved or discarded, navigation resumes its normal path.

## Predictive Back

Predictive Back previews the state or destination behind the current surface during the gesture. `NavDisplay` and current Navigation Compose versions integrate with system Back, but custom handlers and transitions must preserve the same ownership rules.

Review the complete path:

* does the preview match the final destination;
* does only the closest valid layer consume Back;
* do dialogs, sheets, and drawers dismiss before destination navigation;
* are unsaved changes protected;
* do custom transitions follow gesture progress coherently?

Predictive Back does not create navigation inconsistencies. It makes unclear ownership visible.

## Multiple back stacks and adaptive navigation

### Multiple top-level stacks

Bottom navigation often needs one stack per top-level destination:

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

Switching tabs selects another stack without discarding the others. Back normally pops the active stack first; product requirements decide whether Back at its root selects the default tab or exits.

Navigation 2 implements this with `NavController` navigation options such as `popUpTo`, `saveState`, `launchSingleTop`, and `restoreState`. Navigation 3 exposes the stacks directly. In both cases, top-level selection and Back policy need one clear owner.

### Adaptive layouts and scenes

On a compact window, list and detail are usually sequential:

```text
List -> Detail
```

On a larger window, they may be displayed together:

```text
| List | Detail |
```

Navigation 3 scenes and scene strategies can render more than one `NavEntry`. The navigation keys can remain the same while presentation adapts to available space. Keep phone/tablet branching out of business logic: navigation state describes where the user is, and the layout strategy decides how many entries to show.

## Deep links

A deep link should become the same typed navigation state as an internal action:

1. Parse and validate the URI.
2. Convert it to a route or key.
3. Check authentication and other preconditions.
4. Build or update a meaningful back stack.
5. Open the destination with predictable Back behavior.

For a product link, prefer:

```text
ProductList -> ProductDetail(productId)
```

over an isolated details screen with no meaningful parent. Navigation 2 can declare deep links in its graph. With Navigation 3, whether URI matching comes from application code or a library API, the result should still be validated application-owned keys rather than a separate navigation model.

## Testing navigation

Test screen behavior and stack policy separately. A screen test verifies its callback:

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

For Navigation 3, put non-trivial mutations in a small state holder and unit-test its observable stack:

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

Cover the start destination, forward navigation, Back at every layer, restoration, top-level stack switching, deep links, unsaved changes, transient surfaces, predictive Back, and authentication redirects. For UI test principles, see [Compose Testing](testing.md) and [Android UI Testing](../testing/android-ui-testing.md).

## Migration and practical choice

### Migrate deliberately

A Navigation 2 to Navigation 3 migration typically includes:

1. Replace remaining string routes with type-safe routes.
2. Make routes implement `NavKey` or define equivalent Navigation 3 keys.
3. Introduce a navigation state holder and saveable stacks.
4. Move destinations from `NavHost` to an entry provider and `NavDisplay`.
5. Rebuild multiple-stack, dialog, result-returning, and adaptive behavior deliberately.
6. Verify restoration, deep links, and every Back owner.
7. Remove Navigation 2 only after equivalent behavior is covered by tests.

Navigation 3 is Compose-only. A Fragment-heavy or mixed UI application should migrate only when the ownership model provides enough value to justify the change.

### Which approach should you choose?

Choose **Navigation 2** when:

* the application already uses it successfully;
* the project mixes Fragments and Compose;
* mature integrations and existing graph behavior matter most;
* migration would add risk without solving a concrete problem.

Choose **Navigation 3** when:

* the project is new and Compose-first;
* explicit stack ownership is valuable;
* multiple stacks or adaptive layouts are central;
* navigation-as-state fits the architecture;
* the team is ready to own restoration and Back policies.

For a new Compose-first application, start with Navigation 3. Do not migrate a stable Navigation 2 application only because the newer library exists.

## Practical rules

* Use type-safe routes or keys.
* Pass identifiers, not full models.
* Keep navigation framework types out of screen-level `ViewModel`s.
* Save navigation state and model multiple stacks explicitly.
* Let the closest valid owner consume Back.
* Separate transient surface dismissal from destination navigation.
* Make deep links produce valid application navigation state.
* Test stack transitions, restoration, and Back behavior.

**Key idea:** the library matters, but predictable navigation comes from a clear answer to: "Who owns navigation state and Back at this moment?"

## See also

* [State & Recomposition](state-recomposition.md)
* [Side Effects](side-effects.md)
* [UI State Architecture](../architecture/ui-state.md)
* [Activity, Fragment & Lifecycle](../android/activity-fragment-lifecycle.md) - includes `ViewModel` ownership and restoration context
* [Lifecycle-aware Collection](../coroutines-flow/lifecycle-aware-collection.md)
* [Compose Testing](testing.md)

## Further reading

* [Navigation 3 overview](https://developer.android.com/guide/navigation/navigation-3)
* [Navigation 3 basics](https://developer.android.com/guide/navigation/navigation-3/basics)
* [Save and manage Navigation 3 state](https://developer.android.com/guide/navigation/navigation-3/save-state)
* [Migrate from Navigation 2 to Navigation 3](https://developer.android.com/guide/navigation/navigation-3/migration-guide)
* [Type safety in Navigation Compose](https://developer.android.com/guide/navigation/design/type-safety)
* [Predictive Back in Compose](https://developer.android.com/develop/ui/compose/system/predictive-back)