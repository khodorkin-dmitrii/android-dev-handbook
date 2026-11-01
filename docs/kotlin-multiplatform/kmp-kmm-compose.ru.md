# KMP, KMM и Compose Multiplatform

Эти термины описывают разные области: Kotlin Multiplatform позволяет переиспользовать Kotlin-код, а Compose Multiplatform — необязательный способ переиспользовать UI.

| Термин | Значение | Типичное применение |
| --- | --- | --- |
| KMP | Kotlin Multiplatform | Общий код для выбранных целевых платформ |
| KMM | Устаревшее название Kotlin Multiplatform Mobile | Старые статьи и проекты для Android и iOS |
| Jetpack Compose | Android UI toolkit от Google | UI для Android |
| Compose Multiplatform | Мультиплатформенный UI framework от JetBrains | Общий Compose UI для поддерживаемых платформ |

## Kotlin Multiplatform и KMM

KMP — актуальное название технологии, которая компилирует общий Kotlin-код для нескольких целевых платформ. KMM было названием мобильного направления для Android и iOS; JetBrains отказалась от него в 2023 году. Это не отдельная технология, которую нужно выбирать вместо KMP.

Общими могут быть модели, сетевой слой, бизнес-правила и логика представления. Платформенные API по-прежнему требуют платформенного кода или абстракции. Модель компиляции описана в [обзоре Kotlin Multiplatform](overview.md).

## Jetpack Compose и Compose Multiplatform

Jetpack Compose — декларативный UI toolkit для Android. Compose Multiplatform переносит его модель программирования и API на другие поддерживаемые платформы. Он построен на KMP, но для KMP не обязателен. На Android зависимости Compose Multiplatform используют артефакты Jetpack Compose от Google; Android-специфичные API не становятся автоматически доступными в общем коде.

Проверяйте [стабильность платформ](https://kotlinlang.org/docs/multiplatform/supported-platforms.html) отдельно для KMP и Compose Multiplatform. Поддержка платформы в Kotlin не означает такой же поддержки и стабильности Compose UI. При выборе зависимостей проверяйте также [совместимость версий Compose](https://kotlinlang.org/docs/multiplatform/compose-compatibility-and-versioning.html).

## Допустимые комбинации

- Общие data- и domain-слои с Jetpack Compose на Android и SwiftUI на iOS.
- Общее состояние представления с нативным UI на каждой платформе.
- Общий Compose UI для поддерживаемых платформ.
- Общие только отдельные экраны; остальные остаются нативными.

Выбор зависит от требований продукта, платформенного UX, навыков команды и стоимости интеграции. Подробнее — в статье [«Архитектура и стратегии UI»](architecture-ui.md).

## Источники

- [JetBrains: обновление названия Kotlin Multiplatform](https://blog.jetbrains.com/kotlin/2023/07/update-on-the-name-of-kotlin-multiplatform/)
- [Compose Multiplatform и Jetpack Compose](https://kotlinlang.org/docs/multiplatform/compose-multiplatform-and-jetpack-compose.html)
- [Поддерживаемые платформы Kotlin Multiplatform и их стабильность](https://kotlinlang.org/docs/multiplatform/supported-platforms.html)
- [Совместимость и версии Compose Multiplatform](https://kotlinlang.org/docs/multiplatform/compose-compatibility-and-versioning.html)
