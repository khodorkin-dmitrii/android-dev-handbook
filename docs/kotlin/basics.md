# Kotlin Basics

Core Kotlin topics that are important before working with Android code: mutability, null-safety, root types, comparison, casts and inheritance rules.

## Language basics

### `val` vs `var`

`val` - a read-only reference: after initialization, the variable cannot be reassigned. `var` - a mutable reference: a new value can be assigned to the variable.

Important: `val` does not make the object itself immutable. For example, `val list = mutableListOf(1, 2, 3)` prevents reassigning `list`, but does not prevent changing the list contents through `list.add(4)`.

```kotlin
val names = mutableListOf("Ada", "Linus")
names.add("Grace")

var count = 1
count = 2
```

In regular Kotlin code, prefer starting with `val` and switch to `var` only where changing the reference is actually needed. This reduces accidental state changes and makes code easier to read.

### Nullable types

Nullable type - a type that can hold `null`. In Kotlin, nullability is part of the type system: `String` cannot be `null`, while `String?` can.

The compiler forces nullable values to be handled explicitly. Usually this is done with safe call `?.`, Elvis operator `?:`, a `null` check with smart cast or, in rare cases, the not-null assertion `!!`.

```kotlin
val name: String? = user.name
val length = name?.length ?: 0
```

The main risk is `!!`. It disables compiler protection and can lead to `NullPointerException`, so production code should avoid it or use it only when the invariant is truly guaranteed.

### `Any` / `Unit` / `Nothing`

`Any` - the root non-null type in Kotlin, similar to Java `Object`. It has basic methods `equals()`, `hashCode()` and `toString()`. If a value can be `null`, `Any?` is used.

`Unit` - the result type of a function that does not return a useful value. It is close to Java `void`, but in Kotlin `Unit` is a real type with the single value `Unit`.

`Nothing` - a type with no values. It is used for code that never returns normally: for example, a function always throws an exception, calls `error()` or contains an infinite loop.

```kotlin
fun log(message: String): Unit {
    println(message)
}

fun fail(message: String): Nothing {
    throw IllegalStateException(message)
}
```

### `==` vs `===`

`==` checks structural equality - value equality through `equals()`. In Kotlin, `a == b` roughly expands to `a?.equals(b) ?: (b == null)`.

`===` checks referential equality - whether two variables point to the same object in memory.

For a `data class`, `==` compares properties from the primary constructor. `===` is needed much less often, usually when object identity matters: singleton, `object`, cache identity or checking that two references point to the same instance.

```kotlin
data class User(val id: Long)

val first = User(1)
val second = User(1)

println(first == second)  // true
println(first === second) // false
```

### `as` and `as?`

`as` - an unsafe cast. It casts an object to the specified type, but throws `ClassCastException` if the type is incompatible.

`as?` - a safe cast. It returns the object as the requested type or `null` if the cast is impossible.

```kotlin
val value: Any = "Android"

val text = value as String
val number = value as? Int
```

Often an explicit cast is not needed at all: after an `is` check, the compiler performs a smart cast.

```kotlin
if (value is String) {
    println(value.length)
}
```

### `open` / `final` by default

In Java, classes and methods can be inherited or overridden by default if they are not `final`. Kotlin is the opposite: classes and members are `final` by default.

To allow class inheritance or method/property override, write `open` explicitly. Overrides use `override`. If an overridden member should not be overridden further, it can be explicitly marked as `final override`.

```kotlin
open class BaseRepository {
    open fun load() = "data"
}

class UserRepository : BaseRepository() {
    final override fun load() = "users"
}
```

This approach forces extension points to be designed explicitly and reduces the risk of accidentally overriding behavior.
