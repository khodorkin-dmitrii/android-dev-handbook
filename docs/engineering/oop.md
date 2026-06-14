# OOP

OOP (Object-Oriented Programming) is a design approach where a program is built around objects: data and behavior connected together.

## OOP Basics

### What is OOP?

OOP helps model a domain through classes, objects, their responsibilities and interactions. This makes it easier to split code into understandable parts, reuse logic and reduce coupling.

**In short:** OOP organizes code around objects with state and behavior, using encapsulation, inheritance, polymorphism and abstraction.

### 4 OOP principles

The main principles of OOP (Object-Oriented Programming): encapsulation, inheritance, polymorphism and abstraction.

### Encapsulation / inheritance / polymorphism / abstraction

Encapsulation is hiding internal state and implementation details behind a public API. For example, a field is made `private`, and access to it is controlled through methods or properties.

Inheritance is a mechanism that lets a new class be described based on an existing parent class, reusing its properties and methods. Use it carefully because deep class hierarchies often increase coupling.

Polymorphism is the ability to work with different objects through a common type. For example, `ViewModel` depends on a `Repository` interface, and the concrete implementation is supplied through DI.

Abstraction is extracting meaningful information and behavior of an object without binding code to implementation details. In Kotlin and Java this is usually interfaces, abstract classes and public contracts.

### Mutability / immutability

Mutability means an object can be changed after creation. Immutability means an object cannot be changed or appears unchanged from the outside.

Immutability makes reasoning about state easier, reduces the risk of unexpected changes and is especially useful in concurrency, UI state and Compose. Mutability is convenient for local optimizations, but requires control over the state owner.

**Key idea:** immutable state is easier to test, safer to pass between layers and easier to use in reactive UI.
