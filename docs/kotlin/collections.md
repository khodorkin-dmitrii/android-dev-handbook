# Collections

Kotlin provides `List`, `Set`, and `Map` collection types, each with read-only and mutable interfaces. The interface controls which operations are available through a reference; it does not by itself guarantee immutability.

## Core collections

### `List`, `Set`, and `Map`

- `List<T>` preserves element order, supports indexed access, and allows duplicates.
- `Set<T>` stores unique elements. Do not depend on iteration order unless the concrete implementation defines it.
- `Map<K, V>` stores key-value pairs with unique keys. It is a collection type, but does not extend `Collection`.

Choose by semantics. For example, use a list for ordered UI items, a set for selected IDs, and a map for lookup by ID.

### `List` vs `MutableList`

`List<T>` is a read-only interface: it does not expose `add()`, `remove()`, or indexed assignment. `MutableList<T>` extends it with write operations.

```kotlin
val mutable = mutableListOf(1, 2)
val readOnly: List<Int> = mutable

mutable.add(3)
println(readOnly) // [1, 2, 3]
```

Read-only does not mean immutable. Both references point to the same object, so mutations through another reference remain visible. Likewise, `val` prevents reassigning a variable, not changing a mutable collection:

```kotlin
val items = mutableListOf("A")
items += "B" // allowed
```

Expose `List<T>` when callers should not mutate the collection. If they also need a stable snapshot, create a defensive copy such as `source.toList()` and do not retain or expose a mutable alias. This is still shallow: mutable elements can change. Persistent immutable collections are available through a separate library when stronger guarantees are required.

## Operations

### Transform, select, and aggregate

Common operations are expressive when their intent is clear:

- `map` transforms every element.
- `filter` keeps matching elements.
- `flatMap` transforms elements into iterables and flattens them.
- `fold` combines elements starting with an initial accumulator.
- `forEach` performs side effects; use transformations to build values.

```kotlin
val names = users
    .filter { it.isActive }
    .map { it.name }

val totalAge = users.fold(0) { total, user -> total + user.age }
```

These operations return results without changing the source collection. Functions such as `sort()` mutate a mutable list in place, while `sorted()` returns a new list. Make that distinction explicit in state-management code.

Collection pipelines are eager and can create intermediate collections. `asSequence()` processes a pipeline lazily and may avoid intermediates or stop early, for example before `first()` or after `take()`. It also adds overhead, so do not assume it is faster for small collections or simple chains; measure performance-sensitive paths.

## Practical guidance

- Keep mutable collections inside their owner and expose read-only views or snapshots.
- Avoid mutating a collection while iterating over it unless the API explicitly supports that operation.
- Do not use mutable objects as set elements or map keys if fields involved in `equals()` or `hashCode()` can change.
- Prefer operations that communicate intent, but use a loop when it is clearer or avoids unnecessary allocations in a hot path.

## Related topics

- [Kotlin Basics](basics.md)
- [Functions](functions.md)
- [Generics](generics.md)
- [UI State Architecture](../architecture/ui-state.md)

## References

- [Kotlin collections overview](https://kotlinlang.org/docs/collections-overview.html)
- [Collection operations overview](https://kotlinlang.org/docs/collection-operations.html)
- [Sequences](https://kotlinlang.org/docs/sequences.html)
