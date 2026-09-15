# Kotlin Basics

Core Kotlin topics that are important before working with Android code: mutability, null-safety, root types, comparison, casts, and inheritance rules.

## Language basics

### `val` vs `var`

`val` declares a read-only reference: after initialization, it cannot be reassigned. `var` declares a mutable reference that can be assigned a new value.

Important: `val` does not make the referenced object immutable. For example, `val list = mutableListOf(1, 2, 3)` prevents reassigning `list`, but does not prevent changing its contents through `list.add(4)`.

```kotlin
val names = mutableListOf("Ada", "Linus")
names.add("Grace")

var count = 1
count = 2
```

Prefer starting with `val` and switch to `var` only when reassignment is actually needed. This reduces accidental state changes and makes code easier to reason about.

### Nullable types

A nullable type can hold `null`. Nullability is part of Kotlin's type system: `String` cannot be `null`, while `String?` can.

The compiler requires nullable values to be handled explicitly. Common tools are the safe-call operator `?.`, the Elvis operator `?:`, a `null` check followed by a smart cast, and, in rare cases, the not-null assertion `!!`.

```kotlin
val name: String? = user.name
val length = name?.length ?: 0
```

The `!!` operator disables this compiler protection and can cause a `NullPointerException`. Avoid it unless a non-null invariant is guaranteed and cannot be expressed more safely.

Java interoperability is another important boundary. Java declarations with unknown nullability become platform types, so Kotlin may allow an unsafe access that fails at runtime. Treat values coming from Java or Android APIs according to their nullability annotations and documented contracts.

### `Any` / `Unit` / `Nothing`

`Any` is the common supertype of all non-nullable Kotlin types, similar to Java `Object`. It provides `equals()`, `hashCode()`, and `toString()`. Use `Any?` when `null` must also be allowed.

`Unit` is the result type of a function that does not return a useful value. It is similar to Java `void`, but `Unit` is a real type with the single value `Unit`. The explicit return type is usually omitted.

`Nothing` has no values. It represents an expression that never completes normally, such as one that always throws an exception or loops forever. Because `Nothing` is a subtype of every Kotlin type, calls such as `error()` can be used where any result type is expected.

```kotlin
fun log(message: String) {
    println(message)
}

fun fail(message: String): Nothing {
    throw IllegalStateException(message)
}
```

### `==` vs `===`

`==` checks structural equality through `equals()`. The expression `a == b` is roughly equivalent to `a?.equals(b) ?: (b == null)`.

`===` checks referential equality: whether two references point to the same object.

For a `data class`, generated `equals()` compares properties declared in the primary constructor. Arrays are a notable exception: their `equals()` implementation uses identity, so use `contentEquals()` or `contentDeepEquals()` when comparing array contents.

```kotlin
data class User(val id: Long)

val first = User(1)
val second = User(1)

println(first == second)  // true
println(first === second) // false
```

`===` is needed much less often, usually when object identity itself matters, such as verifying that two references point to the same cached instance.

### `as` and `as?`

`as` performs an unsafe cast. It throws `ClassCastException` when the value has an incompatible type. Casting `null` to a non-nullable type also fails at runtime.

`as?` performs a safe cast. It returns the value with the requested type, or `null` when the cast is not possible.

```kotlin
val value: Any = "Android"

val text = value as String
val number = value as? Int
```

An explicit cast is often unnecessary. After a compatible `is` check, the compiler can smart-cast a stable value:

```kotlin
if (value is String) {
    println(value.length)
}
```

### `open` / `final` by default

In Java, classes and methods can be inherited or overridden unless they are `final`. Kotlin takes the opposite approach: classes and overridable members are `final` by default.

Mark a class or member as `open` to allow inheritance or overriding. An override uses `override`; use `final override` to prevent further overrides.

```kotlin
open class BaseRepository {
    open fun load() = "data"
}

class UserRepository : BaseRepository() {
    final override fun load() = "users"
}
```

This makes extension points explicit and reduces accidental changes to inherited behavior.

## Related topics

- [`lateinit` vs `lazy`](lateinit-lazy.md)
