# OOP

Object-oriented programming (OOP) models a system as objects that combine state and behavior. The goal is not to create as many classes as possible, but to give each type a clear responsibility and keep dependencies explicit.

## Four OOP principles

### Encapsulation

Encapsulation protects an object's invariants by hiding mutable state behind a small API. `private` alone is not enough: callers should be able to request valid operations without coordinating internal fields themselves.

```kotlin
class Cart {
    private val items = mutableListOf<Item>()

    fun add(item: Item) {
        require(item.quantity > 0)
        items += item
    }

    fun snapshot(): List<Item> = items.toList()
}
```

`Cart` owns its mutable collection, validates changes and exposes a read-only snapshot instead of leaking the list.

### Abstraction

Abstraction exposes the capability a caller needs while hiding implementation details. An interface is useful for a contract without stored state; an abstract class can share state or implementation between closely related types.

```kotlin
interface UserRepository {
    suspend fun user(id: UserId): User
}
```

A `ViewModel` can depend on this contract rather than on Room or a network client.

### Inheritance

Inheritance expresses an **is-a** relationship and allows a subtype to replace its base type without surprising callers. Kotlin classes and members are final by default; use `open` only for an intentional extension point. Prefer shallow hierarchies. Android framework inheritance, such as `ViewModel`, does not imply that application behavior should also be organized into deep base classes.

### Polymorphism

Polymorphism lets code work through a common type while implementations vary. Production and test implementations of `UserRepository` can be supplied through dependency injection without changing the consumer.

## Prefer composition for reusable behavior

Composition models a **has-a** relationship and usually couples types less than implementation inheritance. Kotlin supports interface delegation when forwarding behavior would otherwise add boilerplate:

```kotlin
class RepositoryWrapper(
    private val delegate: UserRepository,
) : UserRepository by delegate
```

Use inheritance when substitutability is part of the model; use composition to assemble independent capabilities.

## Mutability and state ownership

An immutable object cannot change after creation. A read-only reference such as `val` or `List<T>` does not guarantee deep immutability: referenced objects may still be mutable. Immutable snapshots make UI state easier to reason about, test and render in Compose. Keep unavoidable mutation local to a clear owner, and expose state plus operations or events that request changes.

Related topics: [SOLID](solid.md), [Design Patterns](design-patterns.md), and [Architecture Basics](../architecture/basics.md).
