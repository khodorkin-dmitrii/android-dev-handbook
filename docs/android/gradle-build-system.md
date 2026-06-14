# Gradle & Build System

Gradle is the build system used by Android projects. It resolves dependencies, configures modules, runs build tasks, packages artifacts and coordinates testing, lint, code generation and publishing workflows.

The Android Gradle Plugin (AGP) is the Android-specific layer on top of Gradle. Gradle provides the general build engine, while AGP understands Android concepts such as application/library modules, manifests, resources, build variants, APK/AAB packaging and Android-specific tasks.

## What is Gradle in Android?

In an Android project, Gradle describes how source code becomes an app or library artifact. It knows which modules exist, which plugins are applied, which dependencies are needed and which tasks must run for a selected variant.

Most modern Android projects use Kotlin DSL files with the `.gradle.kts` extension. The build configuration is code, so it can be structured and reused, but it should still stay readable and predictable.

**In short:** Gradle is the build engine, and Android Gradle Plugin adds Android-specific build behavior.

## Android project structure

A typical Android project contains several build-related files and folders:

- `settings.gradle.kts` - defines the project name, plugin/dependency repositories and included modules;
- root `build.gradle.kts` - keeps shared build setup, plugin aliases or common configuration;
- module `build.gradle.kts` - configures an app or library module;
- `gradle/libs.versions.toml` - version catalog with dependency and plugin coordinates;
- `app` - usually the main application module;
- feature modules - user-facing features such as profile, checkout or settings;
- core modules - shared infrastructure such as network, database, design system or common models.

The exact structure depends on project size. A small app can start with one `app` module, while a larger app usually grows into feature and core modules.

## Gradle files in a multi-module project

In a multi-module project, `settings.gradle.kts` includes modules:

```kotlin
include(":app")
include(":feature:profile")
include(":core:network")
```

The root configuration usually holds shared plugin/version setup and repositories. Module configuration defines what each module is: `com.android.application`, `com.android.library`, `org.jetbrains.kotlin.android` and so on.

Dependencies should be directional. Feature modules can depend on core contracts, data modules can provide implementations, and the app module wires everything together. Cyclic dependencies are a sign that module boundaries need to be adjusted.

When configuration is copied across many modules, prefer convention plugins over copy-paste. Convention plugins keep common Android/Kotlin settings in one place and make module files shorter.

**Important:** multi-module builds help only when module boundaries are clear. Random dependencies between modules make the build and architecture harder to maintain.

## Android Gradle Plugin

Android Gradle Plugin connects Gradle with the Android toolchain. It adds Android-specific DSL blocks, tasks and variant handling.

Common AGP configuration includes:

```kotlin
android {
    namespace = "com.example.app"
    compileSdk = 35

    defaultConfig {
        minSdk = 26
        targetSdk = 35
    }
}
```

AGP also handles manifest merging, resource processing, generated `R` classes, BuildConfig, signing, packaging, lint integration and APK/AAB generation.

## Dependencies

Dependencies are declared in module `build.gradle.kts` files. They describe what a module needs to compile, test or run.

Common dependency configurations:

- `implementation` - dependency is used internally by the module;
- `api` - dependency is exposed as part of the module public API;
- `compileOnly` - dependency is needed only for compilation, not packaged at runtime;
- `runtimeOnly` - dependency is needed only at runtime;
- `kapt` - annotation processing through Kotlin annotation processing;
- `ksp` - Kotlin Symbol Processing, often faster and more Kotlin-friendly than `kapt`.

Keep dependencies close to the module that actually uses them. Avoid putting every dependency in the app module or a global shared module by default.

## implementation vs api

Prefer `implementation` by default. It keeps the dependency internal to the module and improves encapsulation.

Use `api` only when types from the dependency are part of the module public contract. For example, if a public function returns a type from another library, consumers of the module need that type on their compile classpath.

```kotlin
dependencies {
    implementation(libs.okhttp)
    api(project(":core:model"))
}
```

Using `api` too often leaks implementation details and can slow incremental builds, because more downstream modules need to be recompiled when the dependency changes.

**In short:** `implementation` hides dependencies, `api` exposes them. Use `api` only for public contracts.

## Build types, flavors and variants

Build types describe how the app is built for different purposes. Common examples are `debug` and `release`.

```kotlin
android {
    buildTypes {
        debug {
            isDebuggable = true
        }
        release {
            isMinifyEnabled = true
        }
    }
}
```

`productFlavors` describe product dimensions such as environment, brand or distribution channel. Combining build types and flavors creates build variants. For example, `demoDebug`, `demoRelease`, `prodDebug` and `prodRelease`.

Variants are powerful, but too many flavors multiply build complexity. Use them when the product really needs different builds, not as a replacement for runtime configuration.

## Source sets

Source sets let a project provide different code and resources for different variants.

Common source sets:

- `src/main` - shared source for all variants;
- `src/debug` - debug-only source and resources;
- `src/release` - release-only source and resources;
- `src/test` - local unit tests;
- `src/androidTest` - instrumented tests.

Flavor and variant-specific source sets can be useful, but they can also hide behavior. Keep variant-specific code small and easy to discover.

## Version catalogs

Version catalogs store dependency and plugin coordinates in `gradle/libs.versions.toml`.

Example:

```toml
[versions]
retrofit = "2.11.0"

[libraries]
retrofit = { module = "com.squareup.retrofit2:retrofit", version.ref = "retrofit" }
```

Then the dependency can be used as:

```kotlin
dependencies {
    implementation(libs.retrofit)
}
```

Version catalogs make dependency names consistent and centralize versions. They do not replace dependency discipline: unused, duplicated or incorrectly scoped dependencies still need cleanup.

## Gradle wrapper

Gradle wrapper is the project-local way to run a specific Gradle version. It includes `gradlew`, `gradlew.bat` and files under `gradle/wrapper`.

Developers and CI should use the wrapper instead of a globally installed Gradle:

```shell
./gradlew assembleDebug
```

This keeps builds reproducible because everyone uses the same Gradle version configured by the project.

## Build performance basics

Build performance depends on module graph, dependency scope, task configuration, annotation processing, caching and how often tasks become invalidated.

Practical basics:

- prefer `implementation` over `api`;
- avoid unnecessary module dependencies;
- keep annotation processors under control;
- use KSP instead of KAPT when libraries support it;
- avoid heavy work during Gradle configuration phase;
- keep convention build logic reusable;
- enable and respect Gradle build/cache features where appropriate;
- avoid constantly changing generated files that invalidate many tasks.

**Practical note:** build performance is usually improved by removing unnecessary work, not by adding more build logic.

## Common pitfalls

Common Gradle and build-system problems:

- cyclic or overly broad module dependencies;
- using `api` where `implementation` is enough;
- putting all dependencies into the app module;
- duplicating the same Android/Kotlin config across many modules;
- too many flavors and variants;
- hidden behavior in variant-specific source sets;
- hardcoded versions outside the version catalog;
- slow annotation processing;
- running network or file generation work during configuration;
- committing local Gradle or IDE state.

**Key idea:** a good Android build is explicit, directional and boring. It should make modules easy to understand and builds predictable.
