# Classes & Types

This section covers classes, object declarations and special Kotlin types that are often used in Android code for data models, UI state and APIs.

## Classes and models

### `data class`

`data class` - a class for storing data, for which Kotlin automatically generates `equals()`, `hashCode()`, `toString()`, `copy()` and `componentN()` based on properties from the primary constructor.

Minimum requirement: the primary constructor must have at least one parameter marked as `val` or `var`.

```kotlin
data class User(
    val id: Long,
    val name: String
)
```

**Important:** properties declared in the class body do not participate in generated `equals()`, `hashCode()`, `copy()` and `componentN()`. `copy()` performs a shallow copy, not a deep copy.

`data class` cannot be `open`, `abstract`, `sealed` or `inner`. In Android, `data class` is often used for DTO, domain models and UI state.

**In short:** `data class` reduces boilerplate for value-like models, but it does not make objects deeply immutable automatically.

### `sealed class` vs `enum class`

`enum class` describes a fixed set of singleton constants of one type. It is convenient for simple states without complex data or with the same set of properties and methods.

`sealed class` or `sealed interface` describes a restricted type hierarchy. Each subtype can be a separate `class`, `object` or `data class` and can hold different data.

The main advantage of `sealed` is exhaustive `when`: Kotlin can check that all variants are handled without `else`.

```kotlin
sealed class Result {
    data class Success(val data: User) : Result()
    data class Error(val message: String) : Result()
    object Loading : Result()
}
```

`enum` fits `Loading` / `Success` / `Error` only if the variants do not have different payloads. `sealed` is better if `Success` stores data and `Error` stores `Throwable` or message.

**In short:** `enum` is a fixed set of constants, `sealed` is a restricted type hierarchy with different subclasses and payloads.

## Objects

### `object` keyword

`object` in Kotlin is used for three main scenarios: anonymous objects, object declarations and companion objects.

An anonymous object is created directly at the usage site. It is convenient for one-off interface implementations or small objects without a separate named class.

```kotlin
val helloWorld = object {
    val hello = "Hello"
    val world = "World"

    override fun toString() = "$hello $world"
}
```

Object declaration declares a singleton. Such an object is initialized lazily on first access, and its initialization is thread-safe.

```kotlin
object DataProviderManager {
    fun registerDataProvider(provider: DataProvider) {
        // ...
    }
}
```

Companion object is associated with a class. Its members can be called through the class name, and the companion object itself is initialized when the corresponding class is loaded or resolved, which is close to Java static initializer semantics.

```kotlin
class MyClass {
    companion object Factory {
        fun create(): MyClass = MyClass()
    }
}

val instance = MyClass.create()
```

If the companion object name is omitted, it gets the name `Companion`.

**In short:** anonymous object is initialized immediately at the usage site, object declaration is initialized lazily on first access, and companion object is initialized together with the corresponding class.

### `object` / `companion object` / `class`

`class` describes a blueprint for objects. Each constructor call creates a new instance.

`object declaration` creates a singleton: one lazily initialized instance for the whole app or classloader. This is convenient for stateless helpers, constants or simple singletons, but global state can complicate testing.

`companion object` - a singleton associated with a specific class. From Kotlin, its members can be called as `ClassName.member()`, but this is not the same as Java `static` at the language level.

For Java interop, `@JvmStatic`, `@JvmField` or `const val` are sometimes used so companion / object APIs look more familiar from Java.

**In short:** `class` creates instances, `object` creates a singleton, `companion object` provides class-associated members.

## Special types

### `inline class` / `value class`

Value class - a Kotlin wrapper class around a single value, declared as `@JvmInline value class`. Previously, this feature was called inline class.

The main idea is to provide a domain type without unnecessary runtime allocation where the compiler can replace the wrapper with the underlying value.

```kotlin
@JvmInline
value class UserId(val value: String)
```

This type helps avoid confusing `UserId` with a regular `String`, even if a string value is stored inside.

Limitations: a value class must have exactly one property in the primary constructor, has no identity, cannot store backing fields other than the underlying value, and boxing is still possible in generics, nullable types and interface usage.

**In short:** value class improves type-safety with low overhead, but it is not a normal wrapper object in all runtime scenarios.
