# JVM / Android Runtime

Раздел про связь Java, JVM bytecode, DEX и Android Runtime. Это помогает понимать, почему Java/Kotlin-код может выглядеть похожим, но выполняться в Android не как обычное desktop/server Java-приложение.

## Runtime и компиляция

### Почему нельзя запустить обычный Java bytecode на Android напрямую?

Android не запускает обычные `.class` файлы напрямую как стандартная JVM. Java/Kotlin-код сначала компилируется в JVM bytecode, а затем Android toolchain преобразует его в DEX (Dalvik Executable).

DEX - формат bytecode для Android Runtime (ART), оптимизированный под мобильную среду и упаковку в APK/AAB. Поэтому Java source code и многие Java libraries можно использовать, если они совместимы с Android API, но raw `.class` bytecode сам по себе не является финальным runtime-форматом Android-приложения.

**Коротко:** Android использует ART и DEX, а не обычный JVM runtime для `.class` файлов.

### JIT compilation

JIT (Just-In-Time) compilation - это компиляция часто выполняемых участков bytecode в native machine code во время выполнения программы.

Идея в том, что runtime сначала может интерпретировать код, собирать profiling information, а затем оптимизировать hot paths. Это улучшает производительность повторяющегося кода, но добавляет runtime overhead и warm-up cost.

**Коротко:** JIT оптимизирует горячий код во время выполнения, в отличие от AOT, где компиляция происходит заранее.

### AOT / JIT в Android ART

ART (Android Runtime) выполняет Android-приложения из DEX bytecode и использует комбинацию interpretation, JIT и AOT/profile-guided compilation.

AOT (Ahead-Of-Time) компилирует код заранее, например во время установки или фоновой оптимизации. JIT компилирует hot code во время выполнения на основе профиля реального использования.

Практический смысл: Android старается балансировать startup time, размер скомпилированного кода, расход памяти и runtime performance. Поэтому корректнее говорить, что современный ART использует гибридный подход, а не только AOT или только JIT.
