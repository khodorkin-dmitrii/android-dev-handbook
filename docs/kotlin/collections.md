# Collections

This section covers Kotlin collections: read-only and mutable interfaces, real immutability and basic operations over data sets.

## Core collections

### `List` vs `MutableList`

`List<T>` in Kotlin is a read-only interface: through such a reference, you cannot call `add()`, `remove()` or `set()`. `MutableList<T>` is a mutable interface that allows changing the collection.

**Important:** read-only does not mean immutable. If the same mutable list is passed as `List<T>`, the owner of the mutable reference can still change the data.

```kotlin
val mutable = mutableListOf(1, 2)
val readOnly: List<Int> = mutable

mutable.add(3)
println(readOnly) // [1, 2, 3]
```

In APIs, prefer returning `List<T>` when caller code should not mutate the collection, and `MutableList<T>` only when mutation is part of the contract.

**In short:** `List` is read-only from this reference, `MutableList` allows mutation, but `List` is not a deep immutability guarantee.

### Read-only vs immutable collections

Read-only collection means the collection cannot be changed through the given interface. Immutable collection means the collection cannot change at all after creation.

Standard Kotlin `List`, `Set` and `Map` are read-only interfaces, but a mutable implementation may be underneath.

For example, `val list: List<Int> = mutableListOf(1, 2)` does not allow calling `list.add()`, but the original mutable reference can add elements.

For a truly immutable model, control the owner of the mutable collection, make defensive copies or use immutable collections if they are available in the project.

**In short:** Kotlin read-only collections protect the API surface, but they do not guarantee true immutability of the underlying object.

## Operations

### `map` / `flatMap` / `filter` / `fold` / `forEach`

`map` transforms each collection element and returns a new collection of results.

`filter` keeps only elements that match the predicate.

`flatMap` first transforms each element into a collection or iterable result, then flattens the results into one list.

`fold` accumulates one final value by traversing the collection with an initial value and accumulator function.

`forEach` performs a side effect for each element and usually should not be used to build a new result.

```kotlin
val names = users
    .filter { it.isActive }
    .map { it.name }

val totalAge = users.fold(0) { acc, user -> acc + user.age }
```

**In short:** `map` transforms, `filter` selects, `flatMap` transforms and flattens, `fold` accumulates, `forEach` is for side effects.
