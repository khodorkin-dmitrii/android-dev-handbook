# State & Recomposition

State и recomposition - основа mental model Compose: UI описывается как функция от состояния, а Compose обновляет затронутые части при изменении state.

## State

### Что такое recomposition?

Recomposition - это повторный вызов composable-функций, когда изменился state, прочитанный во время Composition. Compose старается обновлять только затронутую часть UI tree и пропускать неизменившиеся composable.

Recomposition сама по себе нормальна и не является багом. Проблема появляется, когда она слишком частая, затрагивает слишком большую часть UI или внутри composable выполняется дорогая работа.

Важно различать фазы Compose: Composition определяет, что показывать, Layout измеряет и размещает, Drawing рисует. State change может перезапустить одну или несколько фаз в зависимости от того, где state читается: в body composable, layout modifier или draw phase.

**Коротко:** recomposition is how Compose updates UI from state changes; the goal is not to avoid it completely, but to keep it scoped and cheap.

### `remember` vs `rememberSaveable`

`remember` сохраняет значение между recomposition в пределах текущего composition. Он не переживает удаление composable из composition, configuration change или process death.

`rememberSaveable` тоже сохраняет значение между recomposition, но дополнительно пытается восстановить его после `Activity` / `Fragment` recreation через saved instance state, если тип можно сохранить в `Bundle` или для него задан `Saver`.

`remember` подходит для локального transient UI state и кэширования вычислений внутри composition. `rememberSaveable` подходит для простого UI state, который пользователь ожидает восстановить после rotation, например input text или selected tab.

**Важно:** ни `remember`, ни `rememberSaveable` не заменяют `ViewModel` или persistent storage. Для screen/business state лучше использовать `ViewModel`, `SavedStateHandle`, repository/cache/database в зависимости от данных.

**Коротко:** `remember` survives recomposition, `rememberSaveable` also survives recreation when the value can be saved.

### `mutableStateOf`

`mutableStateOf` создаёт observable Compose `State`. Когда `value` меняется, Compose invalidates места, где этот state был прочитан, и может запустить recomposition.

Обычно используется вместе с `remember`:

```kotlin
var text by remember { mutableStateOf("") }
```

Без `remember` state будет создаваться заново при каждой recomposition.

Для screen-level state чаще лучше использовать `ViewModel` + `StateFlow` и `collectAsStateWithLifecycle()`, а `mutableStateOf` оставлять для локального UI state или state holders, которые осознанно используют Compose runtime.

**Важно:** если хранить mutable collection внутри `mutableStateOf` и менять её содержимое без присваивания нового `value`, Compose может не увидеть изменение. Для UI state лучше предпочитать immutable copy.

**Коротко:** `mutableStateOf` is Compose-observable state; changing it triggers invalidation where it was read, but state ownership still matters.

### State hoisting

State hoisting - это вынос state из child composable к ближайшему common owner, чтобы composable стал более stateless, переиспользуемым и тестируемым.

Обычно child получает `value` и callback вроде `onValueChange`, а state хранится выше: в parent composable, screen state holder или `ViewModel`, если состояние относится к экрану/бизнес-логике.

Не всё состояние нужно hoist-ить до `ViewModel`. Локальный UI state, например `expanded` у dropdown или pressed/animation state, может оставаться внутри composable, если он не нужен другим слоям и не должен переживать screen recreation.

**Коротко:** state hoisting separates state ownership from UI rendering; UI receives state and emits events, while the owner decides how state changes.

## Stability и оптимизация

### Stable parameters / `@Stable` / immutability

Stability в Compose помогает compiler/runtime понять, можно ли безопасно пропустить recomposition, если параметры composable не изменились.

Стабильный тип имеет предсказуемый `equals()` / identity contract и сообщает Compose об изменениях так, чтобы UI мог быть обновлён корректно. Immutable data classes с `val` properties и immutable/read-only данными обычно проще для Compose, чем mutable objects с неявными изменениями.

`@Stable` и `@Immutable` - это contract с Compose compiler, а не магическая оптимизация. Нельзя помечать mutable модель как stable, если изменения её полей не отслеживаются Compose: UI может перестать обновляться корректно.

**Коротко:** stable parameters allow Compose to skip more safely, but annotations must reflect real state behavior; wrong stability is a correctness bug, not just a performance issue.

### Как уменьшать лишние recomposition?

Лишние recomposition уменьшают не запретом recomposition как таковой, а правильным размещением state и снижением стоимости affected UI.

Практические приёмы: держать state ближе к месту использования, hoist-ить только shared state, дробить экран на разумные composable, использовать stable keys в lazy lists, избегать тяжёлой работы в composable body и не создавать новые нестабильные объекты без необходимости.

`derivedStateOf` полезен, когда derived value часто пересчитывается из часто меняющегося state, но реально должен инвалидировать UI только при изменении результата. `remember` полезен для кэширования вычислений, но не должен скрывать business logic.

**Коротко:** optimize recomposition by understanding which state is read where, then reduce unnecessary invalidation and expensive work instead of blindly adding `remember` everywhere.
