# Design Patterns

Design patterns are reusable solutions for common design problems. They do not replace understanding the task, but they provide a shared language for discussing code structure.

GoF (Gang of Four) described 23 main patterns, usually split into three groups:

- Creational: `Abstract Factory`, `Builder`, `Factory Method`, `Prototype`, `Singleton`.
- Structural: `Adapter`, `Bridge`, `Composite`, `Decorator`, `Facade`, `Flyweight`, `Proxy`.
- Behavioral: `Chain of Responsibility`, `Command`, `Interpreter`, `Iterator`, `Mediator`, `Memento`, `Observer`, `State`, `Strategy`, `Template Method`, `Visitor`.

Below are the main patterns that often appear in practice or are visible in APIs.

## Main Patterns

### Factory Method and Abstract Factory

Factory Method is a creational pattern that encapsulates creation of one object type when client code does not need to know the concrete class.

Abstract Factory is a creational pattern that creates a family of related objects. It is useful when a whole set of implementations needs to be replaced, for example different UI components, parsers or platform-specific dependencies.

**In short:** Factory Method solves creation of one product, Abstract Factory solves creation of a family of related products.

### Singleton

Singleton is a creational pattern that guarantees one shared instance of a class and a global access point to it.

In Android, singleton is often used for stateless services, repositories, caches or clients, but it is better to create such objects through a DI container instead of writing a manual static singleton.

The main risk of Singleton is hidden dependencies, global state, harder tests and lifecycle problems.

### Observer

Observer is a behavioral pattern where a subscriber object receives notifications about changes in another object.

In Android, a similar idea appears in listeners, `LiveData`, `Flow`, callbacks and UI state subscriptions. One data source notifies several subscribers about new values.

Remember lifecycle and unsubscription, otherwise memory leak or events after screen destruction are possible.

### Adapter

Adapter is a structural wrapper pattern that lets objects with incompatible interfaces work together.

In Android, this can be a mapper between API model and domain model, a wrapper around a legacy service or `RecyclerView.Adapter`, which adapts data to UI.

The idea is to avoid changing existing code and add a compatibility layer instead.

### Strategy

Strategy is a behavioral pattern that moves a changeable algorithm into a separate object behind a common interface.

This is useful when there are several behavior variants: different validators, sorters, formatters, retry policies, pricing rules or navigation strategies.

Instead of a large `when`, choose the required strategy and call a common method.

### Decorator

Decorator is a structural pattern that adds new behavior to an object without changing its class and without creating a complex inheritance hierarchy.

It wraps the original object and implements the same interface. For example, logging, caching, retry or analytics can be added around `Repository` or a network client.

**In short:** Decorator extends behavior through composition, not inheritance.
