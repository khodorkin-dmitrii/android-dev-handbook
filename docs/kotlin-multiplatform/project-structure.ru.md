# Структура проекта и source sets

Компиляция KMP строится вокруг трёх связанных понятий:

- **target** задаёт платформу и результат компиляции;
- **compilation** объединяет source sets для target и назначения, например основного кода или тестов;
- **source set** группирует исходники, зависимости, настройки компилятора и правила видимости.

Source set — больше, чем папка: компиляция для платформы включает её source set и доступные ему общие или промежуточные sets.

## Основные, тестовые и платформенные source sets

`commonMain` содержит код, компилируемый для всех объявленных targets. В нём доступны только API, общие для них. `commonTest` содержит общие тесты, обычно на `kotlin.test`. Примеры платформенных sets: `androidMain`, `jvmMain`, `iosArm64Main` и `iosSimulatorArm64Main`; `jvmTest` — тестовый set для JVM.

Названия тестовых Android source sets зависят от плагина. Android-KMP library plugin использует `androidHostTest` и `androidDeviceTest`, если соответствующие тесты включены. В старой интеграции с `com.android.library` используются `androidUnitTest` и `androidInstrumentedTest`.

Платформенные source sets видят объявления из общих предков; `commonMain` не видит платформенный код. Объявляйте зависимость в самом узком source set, охватывающем все нужные targets.

## Промежуточные source sets и иерархия

Родственные targets могут разделять промежуточный source set. Для iOS-устройства и симулятора стандартная иерархия создаёт `iosMain`. Если объявлены и другие Apple targets, `appleMain` может объединять общий для них код. Упрощённая схема:

```text
commonMain
├── androidMain
└── appleMain
    └── iosMain
        ├── iosArm64Main
        └── iosSimulatorArm64Main
```

Точная иерархия зависит от объявленных targets. Обычно достаточно стандартного шаблона Kotlin Gradle plugin. Явные связи `dependsOn` могут отключить его применение; изменяйте шаблон, только если стандартная группировка не подходит.

## Компактная модель Gradle

Для KMP-библиотеки с Android-KMP plugin основная конфигурация может выглядеть так (алиасы `libs` задаются в version catalog проекта):

```kotlin
kotlin {
    android {
        namespace = "com.example.shared"
        compileSdk = 36
        minSdk = 24
    }
    iosArm64()
    iosSimulatorArm64()

    sourceSets {
        commonMain.dependencies {
            implementation(libs.kotlinx.coroutines.core)
        }
        iosMain.dependencies {
            implementation(libs.ktor.client.darwin)
        }
    }
}
```

Для блока `android` нужен плагин `com.android.kotlin.multiplatform.library`. В проектах с `com.android.library` отличаются DSL target и названия тестовых sets; не смешивайте конфигурации разных плагинов.

## Модули и source sets

Gradle-модули задают границы сборки, зависимостей, API и владения кодом. Source sets определяют, для каких targets компилируется код *внутри* одного multiplatform-модуля. Начните с одного общего модуля, если этого достаточно; делите по фичам или зонам ответственности, когда граница полезна.

См. [Общий и платформенный код](shared-platform-code.md), [Multi-module Architecture](../architecture/multi-module.md) и [Внедрение KMP и компромиссы](adoption-tradeoffs.md).

## Источники

- [Структура KMP-проекта](https://kotlinlang.org/docs/multiplatform/multiplatform-discover-project.html)
- [Иерархия source sets](https://kotlinlang.org/docs/multiplatform/multiplatform-hierarchy.html)
- [Android-KMP library plugin](https://developer.android.com/kotlin/multiplatform/plugin)
