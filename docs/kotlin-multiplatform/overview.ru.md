# Обзор Kotlin Multiplatform

Kotlin Multiplatform (KMP) позволяет компилировать общий Kotlin-код для нескольких объявленных targets. Один и тот же исходный код отдельно компилируется для каждого target в подходящий формат, например JVM-байткод, JavaScript или нативный бинарный файл. Единой универсальной среды выполнения здесь нет. Например, Android-приложение использует модуль как Kotlin/JVM-код, а iOS-приложение может вызывать Kotlin/Native-фреймворк из Swift. Исходный код общий, но итоговые бинарные файлы и границы взаимодействия различаются.

`commonMain` содержит код для всех targets multiplatform-модуля. В нём доступны общие Kotlin API и multiplatform-библиотеки, но нельзя напрямую вызывать API, которого нет хотя бы на одном target. Например, Android framework или JDK-only API недоступны в общем коде модуля, который также собирается для iOS. Платформенные интеграции размещают за интерфейсами, объявлениями `expect`/`actual` или в более узких [платформенных source sets](shared-platform-code.md). Выбирай самую простую границу, которая не пропускает платформенные API в общий код.

## Что можно переиспользовать

KMP не задаёт обязательный процент общего кода или архитектуру приложения. Общими могут быть:

- отдельные библиотеки, модели, валидация и алгоритмы;
- networking, сериализация, хранение данных, repositories и синхронизация;
- бизнес-правила, use cases и presentation state;
- отдельные UI-компоненты или целые экраны Compose Multiplatform.

Общий UI необязателен. Jetpack Compose на Android и SwiftUI на iOS могут использовать одну общую логику, а другой продукт может переиспользовать и Compose UI. Термины разобраны в статье [KMP, KMM и Compose Multiplatform](kmp-kmm-compose.md).

## Категории платформ

KMP поддерживает несколько семейств платформ, но их tooling и зрелость экосистемы различаются:

- Android и другие JVM targets;
- iOS и другие Apple targets через Kotlin/Native;
- desktop- и server-side приложения на JVM;
- JavaScript и Wasm для web;
- native targets, включая Linux и Windows.

Для Windows есть два разных подхода. JVM desktop-приложение может работать в Windows и использовать Compose Multiplatform Desktop. Windows Native target, например `mingwX64`, создаёт нативный код и имеет другие API, зависимости и tooling. Поддержка target в Kotlin также не означает такой же уровень стабильности Compose Multiplatform UI на этом target.

## Осознанный выбор KMP

KMP особенно полезен, когда платформы разделяют существенную часть поведения, а команда готова владеть и общим кодом, и нативной интеграцией. Граница может проходить после небольшого core или охватывать data, domain, presentation и UI. Выбор должен зависеть от требований продукта, совместимости библиотек, lifecycle и стоимости interoperability, а не от максимального процента общего кода.

Далее: [Структура проекта и Source Sets](project-structure.md), [Общий и платформенный код](shared-platform-code.md) и [Внедрение KMP и компромиссы](adoption-tradeoffs.md).

## Источники

- [Документация Kotlin Multiplatform](https://kotlinlang.org/docs/multiplatform/)
- [Стабильность поддерживаемых платформ](https://kotlinlang.org/docs/multiplatform/supported-platforms.html)
- [Использование платформенных API](https://kotlinlang.org/docs/multiplatform/multiplatform-connect-to-apis.html)
- [Способы интеграции с iOS](https://kotlinlang.org/docs/multiplatform/multiplatform-ios-integration-overview.html)
