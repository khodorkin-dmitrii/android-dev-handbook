# Generics

This section covers generics in Kotlin: type safety, type erasure and variance through `in` / `out`.

## Generics basics

### Generics Java vs Kotlin

Generics allow writing code that works with different types while preserving type safety: `List<String>`, `Repository<User>`, `Result<T>`.

Both Java and Kotlin on JVM use type erasure: the concrete generic type is usually unavailable at runtime.

Kotlin adds declaration-site variance through `out` / `in`, nullable type system, star-projections and reified type parameters for inline functions.

In Java, variance is usually expressed through use-site wildcards: `? extends T` and `? super T`. In Kotlin, `out T` and `in T` are more often written directly in the declaration.

**In short:** Kotlin generics are still erased on JVM, but Kotlin gives stronger syntax for variance and reified support in inline functions.

## Variance

### Variance: `in` / `out`

Variance describes how a generic type with subtype relationships behaves relative to another generic type.

`out` means producer: the type can be safely read as `T`, but cannot accept `T` as input. Example: `Source<out T>`. This is similar to Java `? extends T`.

`in` means consumer: the type can safely accept `T`, but reading will be less precise. Example: `Sink<in T>`. This is similar to Java `? super T`.

Simple PECS formula: Producer Extends, Consumer Super. In Kotlin: producer - `out`, consumer - `in`.

**In short:** use `out` when a type only produces `T`, use `in` when it only consumes `T`.

### Covariance / contravariance / invariance

Covariance means preserving the subtype direction. If `Cat` inherits from `Animal`, then `Producer<Cat>` can be used as `Producer<Animal>`. In Kotlin this is usually `out T`.

Contravariance means the opposite direction. If `Cat` inherits from `Animal`, then `Consumer<Animal>` can be used as `Consumer<Cat>`. In Kotlin this is usually `in T`.

Invariance means generic types are not considered subtypes of each other: `MutableList<Cat>` is not `MutableList<Animal>`. This protects against type-safety errors when writing.

Example problem: if `MutableList<Cat>` could be passed as `MutableList<Animal>`, a `Dog` could be added to it, breaking the list of cats.

**In short:** covariance is for producers, contravariance is for consumers, invariance is the default when both read and write are possible.
