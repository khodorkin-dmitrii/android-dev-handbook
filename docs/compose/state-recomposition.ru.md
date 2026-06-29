# State & Recomposition

State и recomposition - основа mental model Compose: UI описывается как функция от состояния, а Compose обновляет затронутые части при изменении state. Моделирование screen-level state подробнее разобрано в [UI State Architecture](../architecture/ui-state.md).

## State

### Что такое state в Compose?

State - это любое значение, которое может изменяться со временем и влияет на то, что должен показывать UI.

Примеры UI state:

* текст, введённый в text field;
* выбранная вкладка;
* раскрытый или закрытый dropdown;
* флаг загрузки;
* загруженный контент;
* сообщение об ошибке;
* UI-флаг, связанный со scroll.

В Compose UI обычно описывается как функция от state:

```kotlin
UI = f(state)
```

Когда state меняется, Compose может снова вызвать затронутые composable-функции с новыми значениями и обновить UI.

Важно различать обычные Kotlin-значения и observable state. Изменение обычной переменной само по себе не сообщает Compose, что UI нужно обновить:

```kotlin
var count = 0 // not observable by Compose
```

Compose нужен state, который он может наблюдать: например `State<T>`, `MutableState<T>`, созданный через `mutableStateOf`, или внешний observable state, собранный в Compose state:

```kotlin
var count by remember { mutableStateOf(0) }
```

Compose отслеживает, где observable state был прочитан. Когда этот state меняется, Compose помечает места чтения как требующие обновления и может рекомпозировать затронутый UI.

**Коротко:** state - это данные, которые влияют на то, что показывает UI; Compose может автоматически обновлять UI только тогда, когда эти данные доступны как observable state.

### Observable state и `mutableStateOf`

`mutableStateOf` создаёт observable Compose `State`. Когда `value` меняется, Compose помечает места, где этот state был прочитан, как требующие обновления и может запустить recomposition.

Обычно `mutableStateOf` используют вместе с `remember`:

```kotlin
var text by remember { mutableStateOf("") }
```

Без `remember` state будет создаваться заново при каждой recomposition.

Для screen-level state чаще лучше использовать `ViewModel` + [`StateFlow`](../coroutines-flow/stateflow-sharedflow.md) и [`collectAsStateWithLifecycle()`](../coroutines-flow/lifecycle-aware-collection.md), а `mutableStateOf` оставлять для локального UI state или state holders, которые осознанно используют Compose runtime.

**Важно:** если хранить mutable collection внутри `mutableStateOf` и менять её содержимое без присваивания нового `value`, Compose может не увидеть изменение.

Предпочитай immutable-обновления UI state:

```kotlin
var items by remember { mutableStateOf<List<String>>(emptyList()) }

items = items + "New item"
```

Если локальная mutable collection state действительно нужна, используй snapshot-aware коллекции Compose, например `mutableStateListOf`. Для screen state из `ViewModel` лучше выбирать immutable models и immutable collections или read-only lists с контролируемым владением.

**Коротко:** `mutableStateOf` - это observable state Compose; при изменении Compose помечает места чтения как требующие обновления, но владелец state всё равно важен.

### Что такое recomposition?

Recomposition - это повторный вызов composable-функций, когда изменился state, прочитанный во время Composition. Compose старается обновлять только затронутую часть UI tree и пропускать неизменившиеся composable.

Recomposition сама по себе нормальна и не является багом. Проблема появляется, когда она слишком частая, затрагивает слишком большую часть UI или внутри composable выполняется дорогая работа. Performance-сценарии подробнее разобраны в [Compose Performance](performance.md).

Важно различать фазы Compose: Composition определяет, что показывать, Layout измеряет и размещает, Drawing рисует. State change может перезапустить одну или несколько фаз в зависимости от того, где state читается: в body composable, layout modifier или draw phase.

Например, state, прочитанный прямо в body composable, может вызвать recomposition. State, прочитанный только внутри draw modifier, может не запускать recomposition и перезапустить только drawing.

**Коротко:** recomposition - это механизм, через который Compose обновляет UI при изменении state; цель не в том, чтобы полностью её избегать, а в том, чтобы держать её узкой и дешёвой.

### `remember` vs `rememberSaveable`

`remember` сохраняет значение между recomposition в пределах текущей composition. Он не переживает удаление composable из composition, configuration change или process death.

`rememberSaveable` тоже сохраняет значение между recomposition, но дополнительно пытается восстановить его после `Activity` / `Fragment` recreation через saved instance state, если тип можно сохранить в `Bundle` или для него задан `Saver`.

`remember` подходит для локального transient UI state и кэширования вычислений внутри composition. `rememberSaveable` подходит для простого UI state, который пользователь ожидает восстановить после rotation: например input text, selected tab или selected item id.

Не храни в `rememberSaveable` большие списки, bitmaps или полные screen data. Он опирается на saved instance state и должен использоваться только для небольшого UI element state.

**Важно:** ни `remember`, ни `rememberSaveable` не заменяют `ViewModel` или persistent storage. Для screen/business state лучше использовать `ViewModel`, `SavedStateHandle`, repository/cache/database в зависимости от данных.

**Коротко:** `remember` переживает recomposition, а `rememberSaveable` дополнительно переживает recreation, если значение можно сохранить.

### Где должен жить state?

State должен жить в самом низком месте, которое владеет им и может корректно его обновлять.

Частые уровни ownership:

* локальный state UI-элемента: `remember`;
* локальный UI state, который должен пережить recreation: `rememberSaveable`;
* screen state или state, связанный с business logic: `ViewModel`;
* state, который должен пережить process death или app restart: `SavedStateHandle`, repository, database, DataStore или backend.

Например, информация о том, раскрыт ли dropdown, обычно может оставаться внутри composable. Загруженный профиль пользователя, payment state или состояние отправки формы обычно принадлежат `ViewModel`.

Полезное правило: если state влияет только на один небольшой UI-элемент и не нужен другим слоям, держи его локально. Если state описывает экран, business logic или загрузку данных, перенеси его в screen-level state holder и моделируй как часть [UI state](../architecture/ui-state.md).

**Коротко:** держи state настолько локально, насколько возможно, но настолько высоко, насколько необходимо.

### State hoisting

State hoisting - это вынос state из child composable к ближайшему common owner, чтобы composable стал более stateless, переиспользуемым и тестируемым.

Обычно child получает `value` и callback вроде `onValueChange`, а state хранится выше: в parent composable, screen state holder или `ViewModel`, если state относится к экрану или business logic. One-off actions вроде navigation или snackbar лучше отделять от durable state и обычно обрабатывать через [Compose side effects](side-effects.md).

Stateless composable отдаёт наружу value и events:

```kotlin
@Composable
fun SearchField(
    query: String,
    onQueryChange: (String) -> Unit
) {
    TextField(
        value = query,
        onValueChange = onQueryChange
    )
}
```

Owner хранит и обновляет state:

```kotlin
@Composable
fun SearchScreen() {
    var query by rememberSaveable { mutableStateOf("") }

    SearchField(
        query = query,
        onQueryChange = { query = it }
    )
}
```

Не всё состояние нужно hoist-ить до `ViewModel`. Локальный UI state, например `expanded` у dropdown или pressed/animation state, может оставаться внутри composable, если он не нужен другим слоям и не должен переживать screen recreation.

**Коротко:** state hoisting отделяет владение state от UI rendering; UI получает state и отправляет events, а owner решает, как state меняется.

## Stability и оптимизация

### Stable parameters / `@Stable` / immutability

Stability в Compose помогает compiler/runtime понять, можно ли безопасно пропустить recomposition, если параметры composable не изменились.

Стабильный тип имеет предсказуемый `equals()` / identity contract и сообщает Compose об изменениях так, чтобы UI мог быть обновлён корректно. Immutable data classes с `val` properties и immutable collections или read-only данными с контролируемым владением обычно проще для Compose, чем mutable objects с неявными изменениями.

`data class` не становится глубоко immutable автоматически, если внутри есть mutable collections или mutable objects:

```kotlin
data class UiState(
    val items: MutableList<String>
)
```

Хотя `items` объявлен как `val`, содержимое списка всё равно может меняться. Compose может не отследить такие внутренние мутации корректно. Лучше использовать state models, которые наружу отдают immutable collections или read-only lists с контролируемым владением:

```kotlin
data class UiState(
    val items: List<String>
)
```

`@Stable` и `@Immutable` - это contracts с Compose compiler, а не магическая оптимизация. Нельзя помечать mutable model как stable, если изменения её полей не отслеживаются Compose: UI может перестать обновляться корректно.

Сначала предпочитай настоящую immutability. Stability annotations используй только тогда, когда понимаешь contract и можешь его гарантировать.

**Коротко:** stable parameters позволяют Compose безопаснее пропускать recomposition, но annotations должны отражать реальное поведение state; неправильная stability - это correctness bug, а не просто проблема performance.

### Как уменьшать лишние recomposition?

Лишние recomposition уменьшают не запретом recomposition как таковой, а правильным размещением state и снижением стоимости affected UI.

Практические приёмы:

* держать state ближе к месту использования;
* hoist-ить только shared state;
* дробить экран на разумные composable;
* использовать stable keys в lazy lists;
* избегать тяжёлой работы в composable body;
* не создавать новые unstable objects без необходимости;
* предпочитать immutable UI models;
* читать часто меняющийся state как можно ниже в UI tree.

`remember` полезен для кэширования вычислений внутри composition, но не должен скрывать business logic.

`derivedStateOf` полезен, когда input state меняется часто, а derived result меняется реже и UI должен инвалидироваться только при изменении результата. Это один из распространённых инструментов для снижения лишней работы, описанных в [Compose Performance](performance.md).

Например, scroll position списка может меняться очень часто, но UI может интересовать только то, виден ли первый item:

```kotlin
val showScrollToTop by remember {
    derivedStateOf {
        listState.firstVisibleItemIndex > 0
    }
}
```

Не используй `derivedStateOf` для каждого computed value. Он добавляет сложность и наиболее полезен тогда, когда предотвращает лишнюю invalidation из-за часто меняющегося input state.

**Коротко:** оптимизируй recomposition через понимание, какой state где читается, затем уменьшай лишнюю invalidation и дорогую работу вместо того, чтобы вслепую добавлять `remember` везде.
