# SOLID

SOLID is a set of design principles for managing change in object-oriented code. The principles aim to increase cohesion, reduce unnecessary coupling and make behavior easier to replace and test. They are heuristics, not requirements to add an interface or layer for every class.

## Single Responsibility Principle (SRP)

A unit should have one cohesive responsibility and one main reason to change. This is about change boundaries, not about making every function a separate class.

An Android `ViewModel` may coordinate screen logic, but it should not also parse network JSON, execute SQL and format Android resources. Keep transport and persistence details in the data layer. Add a use case or mapper when it represents reusable logic or removes real complexity, not automatically.

**Smell:** changes to unrelated features repeatedly modify the same large class.

## Open/Closed Principle (OCP)

Stable code should allow expected variations to be added without repeatedly rewriting its core logic. Composition, strategies and polymorphism can replace a growing conditional when behavior genuinely varies:

```kotlin
interface PricePolicy {
    fun price(order: Order): Money
}

class Checkout(private val policy: PricePolicy) {
    fun total(order: Order): Money = policy.price(order)
}
```

OCP does not mean existing code must never change. Introducing extension points for hypothetical requirements adds complexity; extract an abstraction when a variation is known or repeated.

## Liskov Substitution Principle (LSP)

Every implementation of a base type must preserve its contract so callers do not need implementation-specific checks. A subtype should not require stronger preconditions, promise weaker results or introduce surprising failures and side effects.

If `UserRepository.user(id)` promises a user or a documented domain error, one implementation should not silently return stale data while another throws an undocumented exception. Tests against the shared contract are useful for multiple implementations.

LSP applies to interfaces as well as class inheritance.

## Interface Segregation Principle (ISP)

Clients should depend only on operations they use. Prefer cohesive, consumer-oriented contracts over one universal interface that forces implementations or test fakes to support irrelevant methods.

For example, a read-only screen may depend on `ObserveOrders`, while synchronization code uses `SyncOrders`. Do not split interfaces only to make them small: methods that change together and serve the same clients can remain together.

## Dependency Inversion Principle (DIP)

High-level policy should not be coupled directly to low-level details; both should meet at a boundary owned by the policy. A `ViewModel` can depend on an application-level `UserRepository` contract, while a data-layer implementation uses Room and Retrofit.

Constructor injection makes dependencies explicit, and Hilt or manual DI can assemble implementations. DI is a wiring technique; it does not satisfy DIP by itself. An interface is unnecessary when there is no meaningful boundary or alternative behavior.

## Applying SOLID pragmatically

Use SOLID to explain a concrete change: which responsibility is mixed, which contract is violated, or which dependency blocks testing. Prefer the simplest design that protects an observed variation. Extra layers, one-method interfaces and pass-through use cases can make navigation harder without improving changeability.

Related topics: [OOP](oop.md), [Design Patterns](design-patterns.md), [Architecture Basics](../architecture/basics.md), and [DI Basics](../di/basics.md).
