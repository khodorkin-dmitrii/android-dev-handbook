# Структура проекта и Source Sets

KMP организует компиляцию через три связанных понятия:

- **target** описывает платформу компиляции и формат результата;
- **compilation** объединяет source sets для target и назначения, например production или tests;
- **source set** определяет исходники, зависимости, compiler options и видимость других source sets.

Поэтому source sets - не просто папки. Platform compilation объединяет platform source set с доступными ему common и intermediate source sets.

## Main, test и platform source sets

`commonMain` компилируется для всех объявленных targets, поэтому использует только доступные каждому из них API. В `commonTest` находятся общие тесты, обычно на `kotlin.test`. К target-specific production и test sets относятся `androidMain`/`androidUnitTest`, `jvmMain`/`jvmTest` и отдельные Native sets, например `iosArm64Main` и `iosSimulatorArm64Main`.

Platform source sets видят declarations из common source sets, от которых зависят. `commonMain` не видит platform-only declarations. Зависимость следует помещать в самый узкий source set, targets которого она поддерживает.

## Intermediate source sets и hierarchy

Родственные targets могут использовать intermediate source set. Для iOS device и simulator targets default hierarchy template обычно создаёт `iosMain`, а для более широкой группы Apple targets может создать `appleMain`. Концептуальный пример:

```text
commonMain
├── androidMain
├── jvmMain
└── appleMain
    ├── iosArm64Main
    └── iosSimulatorArm64Main
```

Это не полное и не универсальное дерево. Kotlin Gradle plugin применяет default hierarchy template по объявленным targets. Custom intermediate source sets и явные `dependsOn` нужны, только когда стандартная hierarchy не отражает реальную группу переиспользования. Ручные связи могут влиять на применение default template.

## Компактная модель Gradle

```kotlin
kotlin {
    androidTarget()
    jvm()
    iosArm64()
    iosSimulatorArm64()

    sourceSets {
        commonMain.dependencies {
            implementation(libs.kotlinx.coroutines.core)
        }
        iosMain.dependencies {
            implementation(libs.apple.supported.library)
        }
    }
}
```

Конкретный Android target DSL зависит от Android/KMP plugin setup. Важно, что targets создают compilations и участвуют в hierarchy source sets.

## Modules и source sets

Gradle modules задают крупные границы сборки, зависимостей, API и владения. Source sets определяют, для каких targets компилируется код внутри одного multiplatform-модуля. Возможен один shared module или feature-oriented multiplatform modules - универсальной структуры нет.

См. [Общий и платформенный код](shared-platform-code.md), [Multi-module Architecture](../architecture/multi-module.md) и [Внедрение KMP и компромиссы](adoption-tradeoffs.md).

## Источники

- [Структура KMP-проекта](https://kotlinlang.org/docs/multiplatform/multiplatform-discover-project.html)
- [Hierarchical project structure](https://kotlinlang.org/docs/multiplatform/multiplatform-hierarchy.html)
