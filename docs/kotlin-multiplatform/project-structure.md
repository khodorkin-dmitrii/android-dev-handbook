# Project Structure and Source Sets

KMP organizes compilation through three related concepts:

- a **target** describes where Kotlin compiles and the produced binary format;
- a **compilation** combines source sets for a target and purpose, such as production or tests;
- a **source set** owns sources, dependencies, compiler options, and visibility toward other source sets.

Source sets are therefore not simply folders. A platform compilation combines its platform source set with the common and intermediate source sets visible to it.

## Main, test, and platform source sets

`commonMain` is compiled for all declared targets, so it can only use APIs available to all of them. `commonTest` holds shared tests, commonly using `kotlin.test`. Target-specific production and test sets include `androidMain`/`androidUnitTest`, `jvmMain`/`jvmTest`, and individual Native sets such as `iosArm64Main` and `iosSimulatorArm64Main`.

Platform source sets can see declarations from the common source sets they depend on; `commonMain` cannot see platform-only declarations. Put each dependency in the narrowest source set whose targets it supports.

## Intermediate source sets and hierarchy

Related targets can share an intermediate source set. For iOS device and simulator targets, the default hierarchy template normally creates `iosMain`; broader Apple combinations may also receive `appleMain`. A conceptual hierarchy is:

```text
commonMain
├── androidMain
├── jvmMain
└── appleMain
    ├── iosArm64Main
    └── iosSimulatorArm64Main
```

This is not a complete or universal tree. The Kotlin Gradle plugin applies its default hierarchy template according to declared targets. Custom intermediate source sets and explicit `dependsOn` relationships are useful only when the default hierarchy does not represent a real sharing group; manual edges can affect application of the default template.

## Compact Gradle model

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

The exact Android target DSL can vary with the Android/KMP plugin setup; the important concept is that targets create compilations and participate in a source-set hierarchy.

## Modules and source sets

Gradle modules define larger build, dependency, API, and ownership boundaries. Source sets define which targets compile code inside one multiplatform module. A project may use one shared module or feature-oriented multiplatform modules; there is no universal structure.

See [Shared vs Platform-Specific Code](shared-platform-code.md) for choosing what belongs in each set, [Multi-module Architecture](../architecture/multi-module.md), and [KMP Adoption and Trade-offs](adoption-tradeoffs.md).

## References

- [KMP project structure](https://kotlinlang.org/docs/multiplatform/multiplatform-discover-project.html)
- [Hierarchical project structure](https://kotlinlang.org/docs/multiplatform/multiplatform-hierarchy.html)
