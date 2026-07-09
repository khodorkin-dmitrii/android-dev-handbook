# Gradle & Build System

`Gradle` - build system, который используется в Android-проектах. Он резолвит dependencies, конфигурирует modules, запускает build tasks, собирает artifacts и координирует testing, lint, code generation и publishing workflows.

`Android Gradle Plugin` (AGP) - Android-specific layer поверх Gradle. Gradle даёт общий build engine, а AGP понимает Android concepts: application/library modules, manifests, resources, build variants, APK/AAB packaging и Android-specific tasks.

## Что такое Gradle в Android?

В Android-проекте Gradle описывает, как source code превращается в app или library artifact. Он знает, какие modules существуют, какие plugins применены, какие dependencies нужны и какие tasks должны выполниться для выбранного variant.

Большинство современных Android-проектов используют Kotlin DSL файлы с расширением `.gradle.kts`. Build configuration - это code, поэтому его можно структурировать и переиспользовать, но он всё равно должен оставаться readable и predictable.

**Коротко:** Gradle - build engine, а Android Gradle Plugin добавляет Android-specific build behavior.

## Android project structure

Типичный Android-проект содержит несколько build-related файлов и папок:

- `settings.gradle.kts` - задаёт project name, plugin/dependency repositories и included modules;
- root `build.gradle.kts` - хранит shared build setup, plugin aliases или common configuration;
- module `build.gradle.kts` - конфигурирует app или library module;
- `gradle/libs.versions.toml` - version catalog с dependency и plugin coordinates;
- `app` - обычно основной application module;
- feature modules - user-facing features, например profile, checkout или settings;
- core modules - shared infrastructure, например network, database, design system или common models.

Конкретная структура зависит от размера проекта. Маленькое приложение может начать с одного `app` module, а большой проект обычно растёт в feature и core modules.

## Gradle files in a multi-module project

В multi-module project файл `settings.gradle.kts` подключает modules:

```kotlin
include(":app")
include(":feature:profile")
include(":core:network")
```

Root configuration обычно хранит shared plugin/version setup и repositories. Module configuration определяет, чем является каждый module: `com.android.application`, `com.android.library`, `org.jetbrains.kotlin.android` и т.д.

Dependencies должны быть направленными. Feature modules могут зависеть от core contracts, data modules могут предоставлять implementations, а app module связывает всё вместе. Cyclic dependencies - признак того, что границы modules нужно пересмотреть.

Когда configuration копируется по многим modules, лучше использовать convention plugins вместо copy-paste. Convention plugins держат общие Android/Kotlin settings в одном месте и делают module files короче.

**Важно:** multi-module builds помогают только при понятных module boundaries. Случайные dependencies между modules усложняют и build, и architecture.

## Android Gradle Plugin

`Android Gradle Plugin` связывает Gradle с Android toolchain. Он добавляет Android-specific DSL blocks, tasks и variant handling.

Типичная AGP configuration:

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

AGP также отвечает за manifest merging, resource processing, generated `R` classes, `BuildConfig`, signing, packaging, lint integration и APK/AAB generation.

## Dependencies

Dependencies объявляются в module `build.gradle.kts` files. Они описывают, что нужно module для compilation, testing или runtime.

Частые dependency configurations:

- `implementation` - dependency используется внутри module;
- `api` - dependency exposed как часть public API module;
- `compileOnly` - dependency нужна только для compilation, но не попадает в runtime;
- `runtimeOnly` - dependency нужна только в runtime;
- `kapt` - annotation processing через Kotlin annotation processing;
- `ksp` - Kotlin Symbol Processing, часто быстрее и Kotlin-friendly, чем `kapt`.

Держи dependencies ближе к module, который реально их использует. Не стоит по умолчанию складывать все dependencies в app module или глобальный shared module.

## implementation vs api

По умолчанию предпочитай `implementation`. Он оставляет dependency внутренней для module и улучшает encapsulation.

Используй `api` только когда types из dependency являются частью public contract module. Например, если public function возвращает type из другой library, consumers module должны иметь этот type на compile classpath.

```kotlin
dependencies {
    implementation(libs.okhttp)
    api(project(":core:model"))
}
```

Слишком частое использование `api` протаскивает implementation details наружу и может замедлять incremental builds, потому что больше downstream modules нужно recompilе-ить при изменениях dependency.

**Коротко:** `implementation` скрывает dependencies, `api` exposes их. Используй `api` только для public contracts.

## Build types, flavors and variants

`buildTypes` описывают, как приложение собирается для разных целей. Частые примеры - `debug` и `release`.

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

`productFlavors` описывают product dimensions, например environment, brand или distribution channel. Комбинация build types и flavors создаёт build variants. Например, `demoDebug`, `demoRelease`, `prodDebug` и `prodRelease`.

Variants мощные, но слишком большое количество flavors умножает build complexity. Используй их, когда продукту действительно нужны разные builds, а не как замену runtime configuration.

## APK, AAB and app size

### Что такое APK?

APK (Android Package) - устанавливаемый пакет Android-приложения.

Это artifact, который Android может установить на устройство. Обычно APK содержит:

- скомпилированный код приложения в виде `.dex` файлов;
- Android resources и assets;
- `AndroidManifest.xml`;
- native libraries, если приложение их использует;
- signing metadata.

APK удобен для local testing, CI artifacts, внутреннего распространения и прямой установки через `adb install`. Например, debug builds часто собираются как APK и устанавливаются напрямую на emulator или физическое устройство.

### Что такое AAB?

AAB (Android App Bundle) - publishing format, а не пакет, который можно установить напрямую.

App bundle содержит скомпилированный код и resources приложения, но генерация APK откладывается до Google Play. Когда пользователь устанавливает приложение, Google Play генерирует и отдаёт optimized APKs под configuration конкретного устройства.

На практике это значит, что пользователю не нужно скачивать все возможные варианты resources, которые есть в приложении.

### APK vs AAB

Главное отличие - где создаётся финальный устанавливаемый APK.

При традиционном APK разработчик собирает и распространяет один installable package. Если это universal APK, внутри могут быть resources и native libraries для разных device configurations: разных ABIs, screen densities и languages.

При AAB разработчик загружает bundle в Google Play. Google Play затем создаёт набор optimized APKs для конкретного устройства. Установленное приложение может состоять из base APK, configuration APKs и, при необходимости, feature APKs.

Коротко:

- APK - устанавливаемый пакет;
- AAB - publishing package, из которого генерируются optimized APKs.

### Почему AAB может уменьшить размер приложения?

AAB может уменьшить download size, потому что Google Play доставляет только код и resources, нужные конкретному устройству.

Частые split dimensions:

- CPU architecture / ABI, например `arm64-v8a`;
- screen density, например `xxhdpi`;
- language resources;
- optional dynamic feature modules.

Например, устройству не нужно скачивать native libraries для всех CPU architectures или изображения для всех screen densities. Ему нужны только части, которые соответствуют его configuration.

Это особенно полезно для крупных приложений с большим количеством resources, translations, native libraries или optional features.

### Dynamic features and asset delivery

App bundles также поддерживают более гибкие delivery models.

Dynamic feature modules позволяют доставлять часть функциональности только тогда, когда она нужна, или только для устройств, которые подходят под определённые условия. Это помогает уменьшить initial install и вынести редко используемые возможности из base module.

Для games или приложений с крупным media content можно использовать Play Asset Delivery, чтобы доставлять большие assets гибче.

Но это не значит, что любое приложение нужно дробить на множество modules. Dynamic delivery полезен, когда feature большая, optional или нужна только части аудитории. Для маленького приложения это может добавить лишнюю сложность.

### Ограничения и практические заметки

AAB - предпочтительный publishing format для Google Play, но он не заменяет APK во всех workflow.

Важные практические моменты:

- AAB нельзя установить напрямую через `adb install`;
- для local testing из AAB нужны generated APKs или `bundletool`;
- internal testing и sideloading часто проще делать через APK;
- non-Google app stores могут всё ещё требовать APK или поддерживать собственный bundle format;
- Play App Signing становится частью стандартного Google Play publishing flow.

### App size optimization

AAB помогает уменьшить delivered size, но не заменяет обычную оптимизацию размера приложения.

Важные техники:

- включай R8 для release builds;
- удаляй unused code и resources;
- включай resource shrinking;
- избегай unnecessary dependencies;
- оставляй native libraries только для поддерживаемых ABIs;
- не поставляй unused assets, languages или большие raw resources;
- выноси крупную optional functionality в dynamic feature modules только когда продукт реально выигрывает от этой сложности.

R8 особенно важен, потому что он может удалять unreachable code, оптимизировать bytecode, сокращать names и уменьшать DEX size. Resource shrinking помогает удалить resources, которые больше не reachable из приложения.

### Коротко

APK - устанавливаемый Android package. Он содержит compiled code, resources, assets, manifest, native libraries и signing information.

AAB - publishing format, который используется в Google Play. Разработчик загружает app bundle, а Google Play генерирует optimized APKs под configuration конкретного устройства. Это может уменьшить download size, потому что пользователь получает только нужные ABI, density, language resources и optional feature modules.

В реальных проектах APK всё ещё полезен для local testing и direct installation, а AAB является стандартным форматом для распространения через Google Play.

## Source sets

`source sets` позволяют проекту предоставлять разный code и resources для разных variants.

Частые source sets:

- `src/main` - общий source для всех variants;
- `src/debug` - debug-only source и resources;
- `src/release` - release-only source и resources;
- `src/test` - local unit tests;
- `src/androidTest` - instrumented tests.

Flavor и variant-specific source sets могут быть полезны, но они также могут прятать behavior. Держи variant-specific code маленьким и легко обнаруживаемым.

## Version catalogs

`version catalogs` хранят dependency и plugin coordinates в `gradle/libs.versions.toml`.

Пример:

```toml
[versions]
retrofit = "2.11.0"

[libraries]
retrofit = { module = "com.squareup.retrofit2:retrofit", version.ref = "retrofit" }
```

После этого dependency можно использовать так:

```kotlin
dependencies {
    implementation(libs.retrofit)
}
```

Version catalogs делают dependency names consistent и централизуют versions. Они не заменяют dependency discipline: unused, duplicated или incorrectly scoped dependencies всё равно нужно чистить.

## Gradle wrapper

`Gradle wrapper` - project-local способ запускать конкретную Gradle version. Он включает `gradlew`, `gradlew.bat` и files внутри `gradle/wrapper`.

Developers и CI должны использовать wrapper вместо globally installed Gradle:

```shell
./gradlew assembleDebug
```

Так builds остаются reproducible, потому что все используют одну Gradle version, настроенную проектом.

## Build performance basics

Build performance зависит от module graph, dependency scope, task configuration, annotation processing, caching и того, как часто tasks становятся invalidated.

Практические основы:

- предпочитай `implementation` вместо `api`;
- избегай unnecessary module dependencies;
- держи annotation processors под контролем;
- используй KSP вместо KAPT, когда libraries это поддерживают;
- избегай тяжелой работы во время Gradle configuration phase;
- держи convention build logic reusable;
- включай и учитывай Gradle build/cache features там, где это уместно;
- избегай постоянно меняющихся generated files, которые invalidates много tasks.

**Практический совет:** build performance обычно улучшается удалением ненужной работы, а не добавлением новой build logic.

## Common pitfalls

Частые проблемы с Gradle и build system:

- cyclic или overly broad module dependencies;
- использование `api`, когда достаточно `implementation`;
- все dependencies сложены в app module;
- одинаковый Android/Kotlin config копируется по многим modules;
- слишком много flavors и variants;
- hidden behavior в variant-specific source sets;
- hardcoded versions вне version catalog;
- slow annotation processing;
- network или file generation work запускается во время configuration;
- local Gradle или IDE state попадает в git.

**Главная мысль:** хороший Android build явный, направленный и скучный. Он должен делать modules понятными, а builds предсказуемыми.
