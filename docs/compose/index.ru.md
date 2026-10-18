# Jetpack Compose

Этот раздел посвящён Jetpack Compose для Android: declarative UI, layout, state, recomposition, side effects, navigation, performance и UI testing.

Практичный порядок изучения: начните с основ Compose и layouts, затем вместе изучите state и side effects. После этого переходите к navigation, а статьи о performance и testing используйте при разработке production-экранов.

## Основы UI

- [Compose Basics](basics.md) - composable-функции, declarative UI, modifiers, previews и interoperability с View system.
- [Layouts и контейнеры Compose](layouts.md) - `Row`, `Column`, `Box`, lazy-контейнеры, adaptive layouts, `ConstraintLayout` и custom `Layout`.

## State и поведение

- [State & Recomposition](state-recomposition.md) - владение state, state hoisting, stability, derived state и управление recomposition.
- [Side Effects](side-effects.md) - effect APIs, lifecycle корутин, актуальные значения и безопасное наблюдение за Compose state.
- [Compose Navigation](navigation.md) - destinations, routes, arguments, back stack, nested graphs и восстановление состояния.

## Production-качество

- [Compose Performance](performance.md) - измерения, идентичность элементов lazy-списков, stability, часто меняющийся state и устранение лишней работы.
- [Compose Testing](testing.md) - semantics, стабильные selectors, synchronization, test rules и детерминированные UI-тесты.
