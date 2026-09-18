# Generics

Generics express relationships between types while keeping reusable code type-safe: `List<String>`, `Repository<User>`, or `Result<T>`.

## Generics basics

### Kotlin and Java

Both Kotlin and Java on JVM use type erasure. Kotlin additionally supports declaration-site variance (`out` / `in`), star projections, and `reified` parameters in inline functions. Java usually expresses variance at the use site with `? extends T` and `? super T`.

A type parameter can belong to a class, interface, or function; its argument can often be inferred:

```kotlin
class Box<T>(val value: T)

fun <T> boxed(value: T): Box<T> = Box(value)

val box = boxed("Kotlin") // Box<String>
```

### Upper bounds and nullability

The default upper bound is `Any?`, so `T` can be nullable. Use `T : Any` to require a non-nullable type. A bound also exposes operations available on that type; multiple bounds in `where` must all be satisfied:

```kotlin
fun <T> longerFirst(a: T, b: T): T
    where T : CharSequence, T : Comparable<T> =
    if (a.length != b.length) {
        if (a.length > b.length) a else b
    } else {
        if (a >= b) a else b
    }
```

## Variance

### Declaration-site variance: `out` / `in`

Variance determines whether a subtype relationship between type arguments carries over to their generic types.

| Declaration | Direction when `Cat : Animal` | Role |
| --- | --- | --- |
| `Source<out T>` | `Source<Cat>` is a subtype of `Source<Animal>` | Produces `T` |
| `Sink<in T>` | `Sink<Animal>` is a subtype of `Sink<Cat>` | Consumes `T` |
| `Box<T>` | Neither `Box<Cat>` nor `Box<Animal>` is a subtype of the other | Invariant |

```kotlin
interface Source<out T> {
    fun next(): T
}

interface Sink<in T> {
    fun accept(value: T)
}

fun use(source: Source<String>, sink: Sink<Any>) {
    val objects: Source<Any> = source
    val strings: Sink<String> = sink
    strings.accept("hello")
}
```

For these interfaces, `out T` prevents adding an `accept(value: T)` member, while `in T` prevents adding a `next(): T` member. These restrictions concern positions of **`T`**, not all parameters or return values: a consumer can still return `Boolean` or `Unit`.

Without a variance modifier, type parameters are invariant, even if the implementation only reads them. For collections, `List` is covariant, but `MutableList` is invariant: allowing a `MutableList<Cat>` as a `MutableList<Animal>` would let callers insert a `Dog`.

Variance ensures type safety; it does not guarantee object immutability. See [Collections](collections.md).

### Use-site variance: type projections

A projection restricts how one reference to an invariant type may be used:

```kotlin
fun copyFirst(from: Array<out Number>, to: Array<in Number>) {
    require(from.isNotEmpty() && to.isNotEmpty())
    to[0] = from[0]
}

val source = arrayOf(1, 2)
val destination = arrayOf<Any>("initial")
copyFirst(source, destination)
```

- `from` produces `Number`; assigning elements through this reference is prohibited.
- `to` accepts `Number`; reading an element yields `Any?`.
- The arrays themselves are not made immutable.

### Star projections: `*`

`List<*>` means a list with an unknown element type, not `List<Any?>`. Its elements can be read as `Any?`. A `MutableList<*>` cannot safely accept an element, even `null`, because its actual element type is unknown. Operations such as `clear()` remain available.

More generally, a star projection permits reading at the parameter's upper bound when it has an output position, and prohibits supplying values in its input position.

## Runtime type information

### Type erasure and `reified`

For an arbitrary value, `is List<*>` can check the container type; `is List<String>` cannot verify its element type. An unchecked `as List<String>` cast does not validate all elements; neither does `as? List<String>`.

An inline function with `reified T` can perform `is T`, `as? T`, and use `T::class`:

```kotlin
inline fun <reified T> matches(value: Any?): Boolean = value is T

val text = matches<String>("hello") // true
val list = matches<List<String>>(listOf(42)) // true: only List is checked
```

`reified` does not recover erased nested type arguments. Validate elements explicitly when the data is untrusted; keep unavoidable unchecked casts local and justify their invariant. See [Functions](functions.md) for inline-function details.

## References

- [Kotlin: Generics](https://kotlinlang.org/docs/generics.html)
- [Kotlin: Type system](https://kotlinlang.org/spec/type-system.html)
- [Kotlin: Collections overview](https://kotlinlang.org/docs/collections-overview.html)
- [Kotlin: Inline functions](https://kotlinlang.org/docs/inline-functions.html)
