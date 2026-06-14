# SOLID

SOLID is a set of object-oriented design principles that help make code more maintainable, extensible and testable.

SOLID stands for SRP, OCP, LSP, ISP and DIP: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion.

These are not strict rules, but guidelines. Their goal is to reduce coupling, increase cohesion and make system changes easier without cascading breakages.

**In short:** SOLID helps design classes with clear responsibility, depend on abstractions and extend behavior without constantly changing existing code.

## SOLID Principles

### Single Responsibility Principle

Single Responsibility Principle (SRP) means a class should have one main reason to change.

In Android this means `ViewModel` should not format UI, call the network, parse JSON and work with the database at the same time. It is better to split responsibility between `ViewModel`, `UseCase`, `Repository`, `Mapper` and `DataSource`.

A typical smell: a class becomes a god object and knows too much about different layers.

### Open/Closed Principle

Open/Closed Principle (OCP) means code should be open for extension but closed for modification.

The idea is to add new behavior through new implementations, strategies or composition instead of constantly editing a large `if` / `else` or `when` block.

In Android, an example can be several `Formatter`, `Validator` or `PaymentHandler` implementations behind a common interface.

### Liskov Substitution Principle

Liskov Substitution Principle (LSP) means a subtype should correctly replace the base type without breaking expected behavior.

If code expects an object of a base class or interface, any implementation should follow its contract. Problems appear when a subtype unexpectedly throws exceptions, ignores methods or changes behavior semantics.

In practice, this is an argument for careful inheritance and well-described interfaces.

### Interface Segregation Principle

Interface Segregation Principle (ISP) means it is better to have several small specific interfaces than one large universal interface.

A class should not depend on methods it does not need. This simplifies testing, mocking and replacing implementations.

In Android this is visible in `Repository` / `DataSource` API: it is better to separate read, write, sync, analytics and navigation contracts if they are actually used by different clients.

### Dependency Inversion Principle

Dependency Inversion Principle (DIP) means high-level logic should not directly depend on low-level details. Both levels should depend on abstractions.

For example, `ViewModel` depends on a `Repository` interface, not directly on a Retrofit service. The concrete implementation is provided through DI.

This reduces coupling and makes code easier to test because tests can provide a fake or mock implementation.
