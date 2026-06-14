# JVM / Android Runtime

This section covers the relationship between Java, JVM bytecode, DEX and Android Runtime. It helps explain why Java/Kotlin code can look familiar but run on Android differently from a regular desktop/server Java application.

## Runtime and Compilation

### Why cannot regular Java bytecode run directly on Android?

Android does not run regular `.class` files directly like a standard JVM. Java/Kotlin code is first compiled to JVM bytecode, then the Android toolchain converts it to DEX (Dalvik Executable).

DEX is the bytecode format for Android Runtime (ART), optimized for the mobile environment and packaging into APK/AAB. So Java source code and many Java libraries can be used if they are compatible with Android APIs, but raw `.class` bytecode itself is not the final runtime format of an Android application.

**In short:** Android uses ART and DEX, not a regular JVM runtime for `.class` files.

### JIT compilation

JIT (Just-In-Time) compilation is the compilation of frequently executed bytecode sections into native machine code while the program is running.

The idea is that the runtime can first interpret code, collect profiling information, and then optimize hot paths. This improves performance of repeated code but adds runtime overhead and warm-up cost.

**In short:** JIT optimizes hot code at runtime, unlike AOT where compilation happens ahead of time.

### AOT / JIT in Android ART

ART (Android Runtime) runs Android applications from DEX bytecode and uses a combination of interpretation, JIT and AOT/profile-guided compilation.

AOT (Ahead-Of-Time) compiles code ahead of time, for example during installation or background optimization. JIT compiles hot code at runtime based on the real usage profile.

Practical meaning: Android tries to balance startup time, compiled code size, memory usage and runtime performance. So it is more accurate to say that modern ART uses a hybrid approach, not only AOT or only JIT.
