# Java

Раздел охватывает темы Java, наиболее важные для Android- и JVM-разработки: семантику объектов, коллекции, generics, исключения, многопоточность и инструменты Android Runtime.

Практический порядок изучения: начните с основ языка и стандартной библиотеки. Затем разберите обработку исключений и многопоточность, после чего изучите, как Java- и Kotlin-код компилируется, оптимизируется и выполняется на Android.

## Основы языка

- [Java Core](core.md) - контракты `Object`, equality, коллекции, generics, boxing, модификаторы доступа, casts и время жизни singleton.
- [Java Exceptions](exceptions.md) - checked и unchecked exceptions, распространение ошибок, освобождение ресурсов, сохранение cause, Kotlin interoperability и границы обработки сбоев в Android.

## Многопоточность

- [Java Concurrency](concurrency.md) - Java Memory Model, visibility, мониторы, interruption, executors, futures, atomic operations и concurrent collections.

## JVM и Android Runtime

- [JVM / Android Runtime](jvm-android-runtime.md) - путь от JVM bytecode до DEX, D8 и R8, desugaring, выполнение в ART, Baseline Profiles, Zygote, процессы и managed memory.
