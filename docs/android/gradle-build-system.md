# Gradle & Build System

Gradle is the build tool used by Android projects. It resolves dependencies, configures modules, selects and executes tasks, and produces test or distribution artifacts. The Android Gradle Plugin (AGP) adds Android-specific concepts such as manifests, resources, SDK levels, build variants, signing, lint, and APK/AAB packaging.

## Gradle, AGP, and the build lifecycle

Gradle is the general build engine; AGP is a plugin that teaches it how to build Android applications and libraries. Kotlin, KSP, serialization, and other plugins add their own tasks and configuration.

A Gradle invocation has three main phases:

1. **Initialization** - reads the settings file and determines which projects participate in the build.
2. **Configuration** - evaluates build logic, applies plugins, and creates/configures the task graph.
3. **Execution** - runs the selected tasks and their dependencies.

Code that configures a task runs when Gradle configures that task; a task action such as `doLast {}` or `@TaskAction` runs during execution if the task actually runs. With lazy task registration, an unrelated task may never be configured. A configuration-cache hit can also reuse the task graph without rerunning the configuration phase.

This distinction matters for performance. Reading files, resolving values eagerly, or running external processes during configuration makes every invocation slower and can break configuration-cache compatibility. Custom work should normally be modeled as tasks with declared inputs and outputs.

## Tasks and execution diagnostics

A **task** is a unit of build work, such as compiling Kotlin, running tests, or packaging an APK. Gradle selects the requested task and its prerequisites (for example, dependencies declared with `dependsOn` or inferred from task outputs consumed by another task). A task can be part of the execution graph without running its actions: Gradle may mark it `UP-TO-DATE`, `FROM-CACHE`, `SKIPPED`, or `NO-SOURCE`.

To investigate a task, answer two separate questions:

1. **Why was it selected?** Run the original command with `--dry-run`, for example `./gradlew :app:assembleDebug --dry-run`, to see the task graph without running task actions. Then inspect the requested task's dependency chain and relevant plugin or build-script configuration. The graph shows *what* was selected; it does not explain every dependency edge automatically.
2. **Why did its actions run again?** Run the original command with `--info` and find the task's up-to-date or execution reason. Check changed inputs or outputs, missing outputs, a changed task implementation, absent previous execution history, disabled up-to-date checks, or `--rerun-tasks`. A Build Scan (`--scan`) can help compare task outcomes and timings; check what it captures before publishing one.

Use the same command and build variant that triggered the unexpected task. `--dry-run` cannot tell you whether its actions would have been up to date in a real build.

## Project structure and repositories

A typical Kotlin DSL project contains:

- `settings.gradle.kts` - names the build, includes modules, and usually configures plugin and dependency repositories;
- root `build.gradle.kts` - declares shared plugin versions or minimal root-level configuration;
- module `build.gradle.kts` - applies plugins and configures one application, library, or feature module;
- `gradle/libs.versions.toml` - optional version catalog for dependency and plugin aliases;
- `gradle.properties` - project-wide Gradle properties;
- `gradle/wrapper` plus `gradlew` / `gradlew.bat` - pins and launches the project's Gradle version.

Plugin repositories and library repositories serve different purposes:

```kotlin
// settings.gradle.kts
pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositories {
        google()
        mavenCentral()
    }
}

include(":app", ":feature:profile", ":core:network")
```

Keep repository declarations centralized when possible. Adding arbitrary repositories inside modules makes dependency resolution harder to audit and reproduce.

## Modules and shared build logic

Each module applies plugins that define its role, for example `com.android.application` or `com.android.library`. Dependencies should follow clear directions: features may depend on stable core APIs, while the application module acts as the final composition root. Cycles usually indicate misplaced responsibilities or missing contracts.

If many modules repeat the same Android and Kotlin setup, extract it into convention plugins, commonly in an included build such as `build-logic`. Convention plugins provide type-safe, testable shared defaults while keeping module scripts small. Avoid a large `subprojects {}` block that invisibly mutates every module.

Modularization does not automatically improve build speed. It helps only when boundaries enable parallel work and prevent broad recompilation; excessive modules and dependencies add configuration and maintenance cost.

## Android Gradle Plugin configuration

AGP exposes the `android` DSL:

```kotlin
android {
    namespace = "com.example.app"
    compileSdk = 36

    defaultConfig {
        applicationId = "com.example.app"
        minSdk = 26
        targetSdk = 36
        versionCode = 1
        versionName = "1.0"
    }
}
```

- `compileSdk` controls which Android APIs are available at compile time.
- `minSdk` is the lowest API level on which the app can be installed.
- `targetSdk` declares the Android behavior level against which the app was tested and may enable newer platform behavior changes.
- `namespace` is used for generated classes such as `R`; an app's `applicationId` identifies the installed and published application.

AGP also performs manifest merging, resource processing, code generation, DEX conversion, signing, lint integration, shrinking, and packaging. Gradle, AGP, the JDK, Kotlin, and Android Studio have compatibility constraints, so upgrades should be performed together with their official compatibility guidance.

## Dependency configurations

Dependencies belong in the module that uses them:

```kotlin
dependencies {
    implementation(libs.okhttp)
    testImplementation(libs.junit)
    androidTestImplementation(libs.androidx.junit)
    ksp(libs.room.compiler)
}
```

Common configurations include:

- `implementation` - available to the module but not exposed on consumers' compile classpaths;
- `api` - exposed to consumers because dependency types form part of the module's public API;
- `compileOnly` - needed to compile but absent from the runtime package;
- `runtimeOnly` - needed at runtime but not for compilation;
- `testImplementation` and `androidTestImplementation` - local and instrumented test dependencies;
- `ksp` or `kapt` - dependencies used by the corresponding code-generation tool.

Prefer `implementation`. Use `api` when a public signature genuinely exposes a dependency type. Overusing `api` weakens encapsulation and can cause changes to invalidate more downstream compilation.

KSP understands Kotlin symbols directly and is generally preferable when a library supports it. Migration still requires validation: not every annotation processor has a KSP implementation, and generated behavior can differ.

### Version catalogs

A version catalog centralizes aliases and coordinates:

```toml
[versions]
retrofit = "2.11.0"

[libraries]
retrofit = { module = "com.squareup.retrofit2:retrofit", version.ref = "retrofit" }
```

```kotlin
dependencies {
    implementation(libs.retrofit)
}
```

Catalogs make names consistent, but they do not enforce dependency boundaries or guarantee that all libraries use one version. Use dependency locking or verification when stronger reproducibility or supply-chain protection is required.

## Build types, flavors, variants, and source sets

Build types usually describe development stages such as `debug` and `release`. Product flavors describe product editions such as brand, environment, or distribution channel. AGP creates a variant from their combination.

```kotlin
// app/build.gradle.kts (com.android.application)
android {
    flavorDimensions += "edition"
    productFlavors {
        create("demo") {
            dimension = "edition"
            applicationIdSuffix = ".demo"
        }
        create("production") { dimension = "edition" }
    }
    buildTypes {
        getByName("debug") { applicationIdSuffix = ".debug" }
        getByName("release") { isMinifyEnabled = true }
    }
}
```

This creates `demoDebug`, `demoRelease`, `productionDebug`, and `productionRelease`. Build one APK with, for example, `./gradlew :app:assembleDemoDebug` or `./gradlew :app:assembleProductionRelease`. The suffixes give the editions and debug builds distinct application IDs so they can coexist on a device; release signing still needs to be configured for distribution.

Source sets provide code and resources for a scope: `src/main`, `src/debug`, `src/release`, `src/test`, `src/androidTest`, or a flavor/variant-specific directory. For the same resource in `demoDebug`, the merge priority is `src/demoDebug` > `src/debug` > `src/demo` > `src/main`, so the `demoDebug` resource wins when all four define it. This overlay rule applies to resources; duplicate Kotlin or Java classes in active source sets cause a build error instead of overriding one another. More flavors multiply variants, tasks, CI work, and places where behavior can hide. Prefer runtime configuration when separate build artifacts are not actually required, and never place secrets in `BuildConfig` or resources: packaged values can be extracted.

## APK, AAB, and shrinking

An APK is an installable package containing DEX code, resources, the manifest, and optional native libraries. It is convenient for local installation, testing, and distribution outside stores.

An Android App Bundle (AAB) is a publishing artifact, not something installed directly with `adb install`. Google Play turns it into device-specific APKs, potentially splitting by ABI, screen density, language, or dynamic feature. Use `bundletool` when you need to inspect or test APKs generated from a bundle.

AAB delivery can reduce download size, but it does not remove the need to optimize the application. Release builds should normally use R8 and resource shrinking, supported by tested keep rules. Also remove unused dependencies and assets, limit packaged ABIs and languages when appropriate, and introduce dynamic features only when their delivery benefit justifies the complexity.

## Wrapper and reproducible builds

Developers and CI should run the checked-in Gradle Wrapper:

```shell
./gradlew assembleDebug
./gradlew test
```

The wrapper downloads the version declared in `gradle-wrapper.properties`, so a global Gradle installation is unnecessary. Commit the wrapper files, upgrade them deliberately, and verify the distribution checksum. Reproducibility also depends on pinned dependencies, controlled repositories, matching JDK/toolchain versions, and avoiding environment-dependent build logic.

## Build performance and diagnosis

Optimize measured bottlenecks rather than relying on folklore. Build scans, Gradle profiling, task output, and Android Studio Build Analyzer can reveal slow configuration, non-incremental processors, cache misses, and unexpectedly invalidated tasks.

Useful principles:

- keep task inputs and outputs explicit so up-to-date checks and caching work;
- use the build cache to reuse task outputs and the configuration cache to reuse configuration results - they solve different problems;
- avoid unnecessary `clean` builds, dynamic dependency versions, and changing generated files;
- prefer lazy Gradle APIs and do no expensive work while configuring the build;
- reduce broad module dependencies and migrate from KAPT to KSP where supported;
- confirm improvements with representative local and CI builds.

## Common pitfalls

- confusing Gradle with AGP or treating Android Studio as the build system;
- incompatible Gradle, AGP, JDK, or Kotlin versions;
- exposing internal dependencies through `api`;
- cyclic or overly broad module dependencies;
- duplicated or hidden cross-module configuration;
- excessive flavors and variant-specific behavior;
- secrets embedded in build files or packaged constants;
- custom tasks without declared inputs and outputs;
- running network, process, or file-generation work during configuration;
- assuming a cache, KSP migration, or modularization is faster without measuring.

**Key idea:** a healthy Android build is explicit, reproducible, and unsurprising. Its module graph, inputs, outputs, and variant differences should be easy to explain.

## Related topics

- [Multi-module Architecture](../architecture/multi-module.md)
- [Performance & Memory](performance-memory.md)
- [Testing Strategy](../testing/strategy.md)

