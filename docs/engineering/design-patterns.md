# Design Patterns

Design patterns are named, reusable approaches to recurring design problems. They provide a shared vocabulary, not ready-made code or a reason to add abstractions before a problem appears.

The 23 Gang of Four (GoF) patterns are commonly grouped as:

- Creational: `Abstract Factory`, `Builder`, `Factory Method`, `Prototype`, `Singleton`.
- Structural: `Adapter`, `Bridge`, `Composite`, `Decorator`, `Facade`, `Flyweight`, `Proxy`.
- Behavioral: `Chain of Responsibility`, `Command`, `Interpreter`, `Iterator`, `Mediator`, `Memento`, `Observer`, `State`, `Strategy`, `Template Method`, `Visitor`.

The patterns below are especially common in Android code and APIs.

## Factory Method and Abstract Factory

**Factory Method** defines a creation operation that subclasses or implementations override to choose the concrete product. A standalone function such as `createParser(format)` that selects a class is usually called a simple factory, not the GoF Factory Method.

**Abstract Factory** creates a family of related products behind one contract. It can supply matching platform-specific services or UI components without exposing their concrete classes.

Use a constructor directly when creation is simple. A factory is useful when creation requires selection, validation, caching or several coordinated dependencies.

## Singleton and scoped instances

**Singleton** combines a single instance with global access. Global mutable state, hidden dependencies and test interference make manual singletons risky on Android.

Prefer explicit constructor dependencies managed by an application container or DI framework. A Hilt-scoped instance is unique within its component, not immortal: process death destroys the graph, and narrower components have shorter lifetimes. Thread safety of instance creation also does not make the object's mutable state thread-safe.

## Observer and reactive streams

**Observer** notifies registered subscribers when a subject changes. Android listeners and callbacks often follow this model. `StateFlow`, `SharedFlow` and `LiveData` provide related observable APIs, but their replay, buffering, lifecycle and error semantics differ.

A cold `Flow` normally starts its upstream work separately for each collector, so it is not simply a list of observers attached to one running subject. Collect UI streams with lifecycle-aware APIs and cancel callback subscriptions when their owner stops.

## Adapter

**Adapter** translates one existing interface into another expected by a client. Examples include wrapping a legacy callback API with a suspending contract or presenting third-party storage through an application interface.

A DTO-to-domain conversion is usually a mapper: it transforms data rather than adapting an object's interface. `RecyclerView.Adapter` adapts application data and view creation to the protocol expected by `RecyclerView`, although its framework role includes more than the minimal GoF pattern.

## Strategy and State

**Strategy** places interchangeable algorithms behind one contract. Validators, pricing policies or retry policies can be selected by configuration and used without a large conditional.

**State** also delegates behavior, but the selected object represents the owner's current state and transitions over time. Use sealed hierarchies and `when` when the set is closed and simple; use polymorphic state objects when each state owns substantial behavior and transitions.

## Decorator

**Decorator** wraps an object with the same contract and adds behavior before or after delegation. Logging, metrics or authorization can be layered without subclassing:

```kotlin
class MeasuredRepository(
    private val delegate: UserRepository,
    private val metrics: Metrics,
) : UserRepository by delegate {
    override suspend fun user(id: UserId): User =
        metrics.measure("load_user") { delegate.user(id) }
}
```

Kotlin's `by` removes forwarding boilerplate. If the wrapper controls access rather than adding responsibilities, **Proxy** may describe the intent better; if it translates an interface, it is an **Adapter**.

## Choosing a pattern

Name the concrete problem first: object creation, interface mismatch, varying algorithm, state-dependent behavior or added responsibility. Prefer language features and simple composition when they solve it clearly. Patterns are most useful when they make change boundaries easier to understand, not when they only add familiar class names.

Related topics: [OOP](oop.md), [SOLID](solid.md), and [DI Basics](../di/basics.md).
