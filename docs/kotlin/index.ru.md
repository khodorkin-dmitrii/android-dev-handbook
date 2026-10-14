# Kotlin

Этот раздел посвящён возможностям Kotlin, наиболее важным для Android- и JVM-разработки: null-safety, моделированию типов, функциям, коллекциям, generics, инициализации и Java interoperability.

Практичный порядок изучения: начните с основ языка, затем перейдите к классам, функциям и коллекциям. Изучайте generics после знакомства со связями между типами, а статьи об инициализации и Java interoperability используйте для понимания типичных границ Android-приложения.

## Основы языка

- [Basics](basics.md) - переменные, null-safety, базовые типы, equality, casts и правила наследования.
- [Classes & Types](classes-and-types.md) - data, sealed, object, companion и value classes и их runtime-компромиссы.
- [Functions](functions.md) - extensions, function types, scope functions, inlining и non-local returns.

## Коллекции и переиспользуемые API

- [Collections](collections.md) - read-only и mutable collections, преобразования, sequences и стабильность ключей.
- [Generics](generics.md) - variance, projections, upper bounds, type erasure и `reified` type parameters.

## Инициализация и interoperability

- [`lateinit` и `lazy`](lateinit-lazy.md) - отложенная инициализация, проверки безопасности и thread-safety modes.
- [Kotlin vs Java](kotlin-vs-java.md) - nullability, visibility, properties, annotations, inheritance и JVM interoperability.
