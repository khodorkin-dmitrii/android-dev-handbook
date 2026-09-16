# Classes & Types

Kotlin classes, object declarations and value types are useful for Android data models, UI state and APIs. Choose a type by its semantics, not just by how much boilerplate it removes.

## Classes and models

### `data class`

A `data class` normally gets generated `equals()`, `hashCode()`, `toString()`, `copy()` and `componentN()` functions based on its primary-constructor properties. Explicit implementations of the first three, or final inherited implementations, can replace their generation.

The primary constructor needs at least one parameter, and **all** its parameters must be `val` or `var`.

```kotlin
data class User(
    val id: Long,
    val name: String
)
```

Properties in the class body are excluded from these generated functions. `copy()` does not copy their current values. It is also shallow: referenced objects are shared, not recursively cloned.

A data class is not automatically immutable. Prefer `val` and immutable contents for UI state; changing a property involved in hashing while an instance is a map key or set element breaks lookup assumptions.

Data classes cannot be `open`, `abstract`, `sealed` or `inner`, but can extend another class or implement interfaces. Common uses include DTOs, domain models and UI state.

### `sealed class` vs `enum class`

An enum represents a fixed set of named instances. Constants can have properties and individual behavior, but are not fresh containers for each request's result.

A sealed hierarchy represents alternatives that can carry different data:

```kotlin
sealed interface UserResult {
    data class Success(val user: User) : UserResult
    data class Error(val message: String) : UserResult
    data object Loading : UserResult
}

fun label(result: UserResult): String = when (result) {
    is UserResult.Success -> result.user.name
    is UserResult.Error -> result.message
    UserResult.Loading -> "Loading"
}
```

Direct subtypes must be named and declared in the same package and module; they need not be in the same file. An open, non-sealed subtype can allow further inheritance outside that boundary. Multiplatform source sets impose additional restrictions.

A sealed class can hold shared constructor state; a sealed interface allows implementations with another superclass. Exhaustive `when` avoids `else` when all alternatives are covered; nullable inputs also need a null case.

Use enums for fixed choices such as sort order; use sealed types for results or states with variant-specific data. `data object` is useful for data-free alternatives: it generates readable `toString()` and structural equality, but no `copy()` or `componentN()`.

## Objects

### `object` keyword

An object expression creates an anonymous instance each time it executes, useful for one-off implementations:

```kotlin
val helloWorld = object {
    val hello = "Hello"
    val world = "World"

    override fun toString() = "$hello $world"
}
```

An object declaration defines a singleton initialized on first access. Initialization is thread-safe; later operations on mutable state are **not** automatically synchronized.

```kotlin
object UserNames {
    fun display(user: User): String = user.name.ifBlank { "Unknown" }
}
```

On JVM, the singleton belongs to its defining classloader, not all Android processes. Avoid holding Activity or View references in long-lived objects. Global mutable state also complicates test isolation.

### `object` / `companion object` / `class`

A class permits separate instances via constructor calls. An object declaration provides a shared instance. A companion object provides a class-associated instance, not one companion per enclosing instance:

```kotlin
class MyClass {
    companion object Factory {
        fun create(): MyClass = MyClass()
    }
}

val instance = MyClass.create()
```

An unnamed companion is called `Companion`. Its members are instance members even though Kotlin permits access through the class name. On JVM its initialization follows the enclosing class's static-initialization semantics; merely loading a class need not initialize it.

For Java callers, `@JvmStatic` exposes static methods, while `@JvmField` exposes eligible properties as fields; `const val` declares compile-time constants. These mechanisms are not interchangeable.

## Special types

### `inline class` / `value class`

A value class introduces a distinct type around one value. On JVM, use `@JvmInline`:

```kotlin
@JvmInline
value class UserId(val value: String)
```

Unlike a type alias, `UserId` is not interchangeable with `String`. It prevents accidental mixing of domain identifiers.

A value class has one read-only primary-constructor property. It may have methods, computed properties and validation in `init`, but no additional backing fields. It can implement interfaces, cannot extend another class, and is final.

The compiler can represent it as the underlying value, but boxing can occur with generics, interfaces and nullable usage. Do not promise allocation-free behavior in every context. Value classes have no referential identity; `===` is prohibited. JVM function-name mangling and Java-call-site constraints also matter for public APIs.

## Related topics

- [Kotlin Basics](basics.md)
- [Kotlin vs Java](kotlin-vs-java.md)
- [UI State Architecture](../architecture/ui-state.md)

## References

- [Kotlin: Data classes](https://kotlinlang.org/docs/data-classes.html)
- [Kotlin: Sealed classes and interfaces](https://kotlinlang.org/docs/sealed-classes.html)
- [Kotlin: Object declarations and expressions](https://kotlinlang.org/docs/object-declarations.html)
- [Kotlin: Inline value classes](https://kotlinlang.org/docs/inline-classes.html)
