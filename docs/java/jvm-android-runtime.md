# JVM / Android Runtime

Java and Kotlin source can target Android, but an Android app does not run inside a conventional desktop/server JVM. The build toolchain produces DEX bytecode, and Android Runtime (ART) executes it using interpretation and compiled native code.

## From source code to DEX

A simplified Android build pipeline is:

```text
Java/Kotlin source
        ↓ javac / Kotlin compiler
JVM bytecode (.class files)
        ↓ D8 or R8 + desugaring
DEX bytecode (.dex files)
        ↓ packaging
APK installed on a device
        ↓ ART
interpreted or compiled machine code
```

Java libraries usually arrive as JAR or AAR artifacts containing `.class` files. During the Android build, D8 converts JVM bytecode to DEX. In optimized builds, R8 can additionally shrink, optimize, and obfuscate code before producing DEX.

An Android App Bundle (`.aab`) is a publishing format, not the file ART directly executes. Google Play uses it to generate APKs tailored to a device; installed APKs contain the DEX and resources used at runtime.

One DEX file has reference limits, including the well-known 65,536 method-reference limit. Apps that exceed them use multiple DEX files. Modern Android build tools handle multidex automatically for `minSdk` 21 and above; older versions need legacy multidex support.

## JDK, language level, and Android APIs

Three versions that are often confused have different roles:

- **Gradle JDK** runs Gradle and the Android Gradle Plugin during the build.
- **Java/Kotlin language and bytecode targets** control which source features and JVM bytecode level compilers produce.
- **`compileSdk` and `minSdk`** determine which Android APIs are visible at compile time and available on devices.

Using a newer JDK to build the app does not make every JDK API available on Android. Android provides its own Java-compatible core libraries. A library must use APIs supported by the target Android versions or supplied through supported desugaring/backports.

### Desugaring

Desugaring rewrites newer language constructs into forms older Android runtimes understand during D8/R8 compilation. Core library desugaring can also package implementations of selected newer Java APIs and rewrite calls to them.

Desugaring is not a universal JVM compatibility layer: it supports specific features and APIs. Always check Android documentation and `minSdk` requirements when adopting a Java API.

## ART execution model

### Interpretation, JIT, and AOT

ART executes DEX using a hybrid strategy:

- **Interpretation** can start code without first compiling all of it.
- **JIT (Just-In-Time)** compiles frequently executed code while the app runs and records profiling information.
- **AOT (Ahead-Of-Time)** compiles selected code before execution, including profile-guided work performed during installation or background device optimization.

The exact strategy varies by Android version and device state. It balances startup latency, storage occupied by compiled code, memory use, installation time, and steady-state performance. It is therefore inaccurate to describe modern ART as purely interpreted, JIT-only, or AOT-only.

Baseline Profiles provide ART with likely hot code paths from the first launch, so selected code can be compiled before real users exercise it. They complement runtime profiles rather than replacing JIT or guaranteeing that all application code is AOT-compiled.

## Processes, Zygote, and memory

Android normally runs each app in its own Linux process with its own ART instance and sandboxed UID. Components from the same application usually share that process, but Android can create or terminate the process according to system needs; an application object is not a permanent system-wide singleton.

New app processes are commonly forked from **Zygote**, a pre-initialized process containing framework classes and resources. Copy-on-write memory sharing makes process startup and common framework memory more efficient.

ART uses garbage collection for managed Java/Kotlin objects. Garbage collection removes objects that are no longer reachable; it does not close files, sockets, cursors, or other external resources. Close those deterministically. Allocation rate, retained references, and GC pauses can still affect frames and responsiveness, so diagnose memory and performance with measurements rather than manual `System.gc()` calls.

## Practical implications

- Do not assume behavior or APIs merely because code works on a desktop JVM.
- Keep build JDK compatibility separate from device API compatibility.
- Treat reflection, JNI, dynamic class loading, and serialization carefully when R8 is enabled; required code may need precise keep rules.
- Measure release builds because DEX layout, R8 optimization, profiles, and ART compilation can make them behave differently from debug builds.
- Use Baseline Profiles and benchmarks for important startup and interaction paths instead of trying to control JIT/AOT directly.

## Related topics

- [Java Core](core.md)
- [Gradle & Build System](../android/gradle-build-system.md)
- [Performance & Memory](../android/performance-memory.md)

## References

- [Android Runtime and Dalvik](https://source.android.com/docs/core/runtime)
- [Java versions in Android builds](https://developer.android.com/build/jdks)
- [Java language features and API desugaring](https://developer.android.com/studio/write/java8-support)
- [R8 app optimization](https://developer.android.com/topic/performance/app-optimization/enable-app-optimization)
- [Baseline Profiles](https://developer.android.com/topic/performance/baselineprofiles/overview)
- [Android memory management](https://developer.android.com/topic/performance/memory-overview)
