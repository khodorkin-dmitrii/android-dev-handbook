# KMP, KMM и Compose Multiplatform

Эти термины связаны, но описывают разные области. Kotlin Multiplatform отвечает за переиспользование кода, а Compose frameworks относятся к UI.

| Термин | Значение | Что можно переиспользовать |
| --- | --- | --- |
| KMP | Multiplatform-технология Kotlin | Логику, data, presentation, UI или отдельные компоненты |
| KMM | Прежнее название мобильного направления | Исторически общий код Android и iOS |
| Jetpack Compose | Android UI toolkit | Android UI |
| Compose Multiplatform | Multiplatform Compose UI framework | UI для поддерживаемых targets |

## Kotlin Multiplatform и KMM

Kotlin Multiplatform, или KMP, - современное общее название технологии для переиспользования Kotlin-кода между объявленными targets. Kotlin Multiplatform Mobile, или KMM, - прежнее название мобильного направления. Оно встречается в старых статьях, репозиториях и названиях инструментов, но не является отдельной современной альтернативой KMP.

Модель компиляции описана в [обзоре Kotlin Multiplatform](overview.md).

## Jetpack Compose и Compose Multiplatform

Jetpack Compose - декларативный UI toolkit для Android. Compose Multiplatform переносит модель и API Compose на поддерживаемые non-Android платформы. Это UI framework поверх multiplatform-экосистемы, а не другое название KMP.

Поддержку Kotlin targets и Compose Multiplatform UI нужно оценивать отдельно. Kotlin может поддерживать target, в то время как Compose UI для него имеет другой уровень стабильности или отсутствует. Актуальный статус указывается отдельно для каждой платформы.

## Допустимые комбинации

KMP не требует Compose Multiplatform:

- общие data- и domain-слои с Jetpack Compose на Android и SwiftUI на iOS;
- общий presentation state с нативным UI на каждой платформе;
- общий Compose UI для поддерживаемых targets;
- гибрид, где часть экранов общая, а часть остаётся нативной.

Выбор зависит от требований к product parity, платформенному UX, владения кодом и стоимости интеграции. Подробнее: [Архитектура и стратегии UI](architecture-ui.md).

## Источники

- [Поддерживаемые платформы Kotlin Multiplatform и их стабильность](https://kotlinlang.org/docs/multiplatform/supported-platforms.html)
- [Совместимость и версии Compose Multiplatform](https://kotlinlang.org/docs/multiplatform/compose-compatibility-and-versioning.html)
