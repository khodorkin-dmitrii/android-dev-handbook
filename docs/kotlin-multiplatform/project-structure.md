# Project Structure and Source Sets

KMP organizes compilation through three related concepts:

- a **target** specifies the platform and output to compile for;
- a **compilation** combines source sets for a target and purpose, such as production or tests;
- a **source set** groups sources, dependencies, compiler options, and visibility rules.

A source set is more than a folder: a target compilation includes its platform source set and the common or intermediate sets it depends on.

## Main, test, and platform source sets

`commonMain` contains code compiled for every declared target. It can use only APIs available to all of them. `commonTest` contains shared tests, commonly using `kotlin.test`. Platform sets include `androidMain`, `jvmMain`, `iosArm64Main`, and `iosSimulatorArm64Main`; `jvmTest` is a target-specific test set.

Android test names depend on the plugin. The Android-KMP library plugin uses `androidHostTest` and `androidDeviceTest` when those tests are enabled. Older `com.android.library` integration uses `androidUnitTest` and `androidInstrumentedTest`.

Platform source sets can see declarations from their common ancestors; `commonMain` cannot see platform-only declarations. Declare a dependency in the narrowest source set that covers every target needing it.

## Intermediate source sets and hierarchy

Related targets can share an intermediate source set. With iOS device and simulator targets, the default hierarchy creates `iosMain`. If the project also declares other Apple targets, `appleMain` can share code across them. A simplified hierarchy is:

```text
commonMain
├── androidMain
└── appleMain
    └── iosMain
        ├── iosArm64Main
        └── iosSimulatorArm64Main
```

The exact hierarchy depends on declared targets. Prefer the Kotlin Gradle plugin's default hierarchy. Explicit `dependsOn` edges can stop that template from applying; customize the template only when the default grouping is insufficient.

## Compact Gradle model

For a KMP library using the Android-KMP plugin, the core configuration can look like this (the `libs` aliases come from the project's version catalog):

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

The `android` block requires the `com.android.kotlin.multiplatform.library` plugin. Projects still using `com.android.library` have a different target DSL and test-set names; follow the matching plugin documentation rather than mixing configurations.

## Modules and source sets

Gradle modules define build, dependency, API, and ownership boundaries. Source sets define which targets compile code *within* one multiplatform module. Start with one shared module if it fits; split by feature or ownership when the boundary is useful.

See [Shared vs Platform-Specific Code](shared-platform-code.md), [Multi-module Architecture](../architecture/multi-module.md), and [KMP Adoption and Trade-offs](adoption-tradeoffs.md).

## References

- [KMP project structure](https://kotlinlang.org/docs/multiplatform/multiplatform-discover-project.html)
- [Source set hierarchy](https://kotlinlang.org/docs/multiplatform/multiplatform-hierarchy.html)
- [Android-KMP library plugin](https://developer.android.com/kotlin/multiplatform/plugin)
