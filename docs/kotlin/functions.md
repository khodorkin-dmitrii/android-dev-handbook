# Functions

Kotlin treats functions as values: they can be stored, passed, and returned. This enables callbacks, collection operations, builders, Compose APIs, and reusable control flow.

## Extensions and function values

### Extension functions

An extension function makes a function callable on an existing type without inheritance or modifying that type:

```kotlin
fun String.looksLikeEmail(): Boolean =
    contains("@") && substringAfterLast("@").contains(".")
```

This is only a simple UI-level check, not full email validation. More importantly, extensions are resolved statically from the receiver's declared type. They cannot access the receiver's private or protected members, and a compatible member function always takes precedence over an extension.

Extensions improve API ergonomics, but broad extensions on common types such as `String` can pollute autocomplete or hide domain meaning. Keep them cohesive and place them near the owning feature or API.

### Lambdas and function types

A lambda is a function literal that can be stored, passed, or returned:

```kotlin
val transform: (Int) -> Int = { value -> value * 2 }
val doubled = numbers.map(transform)
```

`(A, B) -> C` describes a function taking `A` and `B` and returning `C`. `() -> Unit` has no parameters; `suspend () -> T` describes a suspending function; `A.(B) -> C` has receiver `A` and is common in type-safe builders and Compose-style DSLs.

For a single inferred parameter, `it` can replace an explicit name. Prefer a descriptive name when lambdas are nested or non-trivial. Lambdas can capture outer variables; capturing mutable state can make lifecycle, concurrency, and recomposition behavior harder to reason about.

### Higher-order functions

A higher-order function accepts or returns a function:

```kotlin
fun repeatAction(times: Int, action: (index: Int) -> Unit) {
    require(times >= 0)
    repeat(times) { index -> action(index) }
}
```

They separate reusable control flow from behavior. Function values may allocate objects and invoke indirectly, although the compiler and runtime can optimize many cases. Use `inline` selectively when its semantics or measured performance benefit justify it.

## Scope and inline functions

### Scope functions: `let` / `run` / `with` / `apply` / `also`

Scope functions differ mainly by how they expose the context object and what they return:

| Function | Context | Returns | Typical intent |
|---|---|---|---|
| `let` | `it` | Lambda result | Null-safe transformation |
| `run` | `this` | Lambda result | Configure and compute a result |
| `with(obj)` | `this` | Lambda result | Group calls on an existing object |
| `apply` | `this` | Context object | Object configuration |
| `also` | `it` | Context object | Additional side effect, such as logging |

```kotlin
val user = User().apply {
    name = "Ada"
    isActive = true
}

val length = user.name.takeIf { it.isNotBlank() }?.length ?: 0
```

Scope functions add no new language capability. Choose the one that makes ownership and return value obvious. Avoid long chains, nested scopes, and ambiguous `this` or `it` references.

### `inline`, `noinline`, and `crossinline`

Marking a function `inline` asks the compiler to inline the function and eligible lambda arguments at call sites. This can avoid function-object and virtual-call overhead, enables non-local returns from eligible lambdas, and allows `reified` type parameters. The compiler may warn when inlining is unlikely to help.

Inside an inline function:

- `noinline` keeps a lambda as a regular value so it can be stored or passed where an object is required.
- `crossinline` prevents a non-local `return`; use it when the lambda may run from another execution context, such as a `Runnable`.

Inlining can increase generated code size. It is most appropriate for small higher-order APIs and reified utilities, not as a default performance annotation.

### `reified`

A type parameter can be `reified` only in an inline function:

```kotlin
inline fun <reified T> Any?.isType(): Boolean = this is T
```

Because the concrete call-site type is substituted, the body can use `T::class`, `is T`, and APIs such as `filterIsInstance<T>()` without an explicit `Class<T>` or `KClass<T>` parameter.

This does not preserve every nested type argument at runtime. For example, checking `value is List<T>` cannot prove the runtime types of all list elements because those arguments are still erased.

## Related topics

- [Collections](collections.md)
- [Generics](generics.md)
- [Compose Basics](../compose/basics.md)

## References

- [Kotlin extensions](https://kotlinlang.org/docs/extensions.html)
- [Higher-order functions and lambdas](https://kotlinlang.org/docs/lambdas.html)
- [Scope functions](https://kotlinlang.org/docs/scope-functions.html)
- [Inline functions](https://kotlinlang.org/docs/inline-functions.html)
