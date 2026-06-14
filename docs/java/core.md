# Java Core

Core Java topics that matter in Android development: `Object`, object equality, collections, generics, access modifiers, type casting and singleton.

## Objects and Equality

### `Object` class

`Object` is the base class for all reference types in Java. If a class does not explicitly extend another class, it implicitly extends `Object`.

Key `Object` methods: `toString()`, `equals()`, `hashCode()`, `getClass()`, `clone()`, `wait()`, `notify()` and `notifyAll()`. `wait()` / `notify()` are related to monitor locks and concurrency, while `clone()` is rarely used and requires caution.

**Important:** `finalize()` appears in old materials, but modern Java/Android code should not rely on it for cleanup. For resources, prefer `try-with-resources`, `close()`, lifecycle-aware cleanup or explicit resource management.

### `equals()` / `hashCode()` contract

`equals()` defines logical equality of objects, while `hashCode()` returns a numeric hash used by `HashMap`, `HashSet` and other hash-based collections.

The main contract: if `a.equals(b) == true`, then `a.hashCode()` must be equal to `b.hashCode()`. The opposite is not guaranteed: the same `hashCode()` does not mean objects are equal, because collisions are possible.

If you override `equals()`, you almost always need to override `hashCode()`. Otherwise the object may behave incorrectly in `HashMap` / `HashSet`: it can be added, but later not found.

### Class as a `HashMap` key

If a custom class is used as a key in `HashMap`, it needs correct `equals()` and `hashCode()` implementations.

`HashMap` first uses `hashCode()` to choose a bucket, then uses `equals()` to check the specific key among possible collisions. If the contract is broken, `get()` and `remove()` may fail to find an object even with a logically equal key.

In Kotlin, `data class` generates `equals()` and `hashCode()` automatically from primary constructor properties. But mutable fields in a `HashMap` key are dangerous: if a field participating in `hashCode()` changes after insertion, the key can become unreachable.

## Generics and Collections

### Generics and primitives in Java

Java generics work only with reference types, so `List<int>` is impossible. Primitive values use wrapper types: `Integer`, `Long`, `Boolean` and so on.

Because of type erasure, generic types mostly lose information about the concrete `T` at runtime, and operations work through `Object` and casts. Primitives are not `Object`, so they require boxing/unboxing.

On Android this matters for performance: collections such as `List<Integer>` can create extra allocations compared with `int[]` arrays or specialized structures.

### `Iterator` and `Iterable`

`Iterable` is an interface for objects that can be iterated. It contains the `iterator()` method, which returns an `Iterator`.

`Iterator` is the object that performs the traversal: `hasNext()` checks whether there is a next element, `next()` returns the next element, and `remove()` optionally removes the current element.

Java `for-each` works on top of `Iterable`. Do not modify a collection directly while traversing it with a regular iterator, otherwise `ConcurrentModificationException` is possible. For removal during traversal, use `iterator.remove()` or safer alternatives.

### Java Collections hierarchy

`Collection` is the base interface for most Java collections: `List`, `Set`, `Queue` and `Deque`. `List` stores ordered elements, `Set` stores unique elements, and `Queue` / `Deque` describe queues.

`Map` does not extend `Collection` because it stores key-value pairs rather than individual elements. `HashMap`, `TreeMap` and `LinkedHashMap` are different `Map` implementations with different ordering guarantees and complexity characteristics.

**Key idea:** Java Collections Framework is a set of interfaces and implementations for storing groups of objects, where it is important to understand not only the API, but also operation complexity, element ordering and `equals()` / `hashCode()` requirements.

## Types and Access

### Java access modifiers

Java has `public`, `protected`, package-private and `private`.

`public` is accessible from anywhere. `private` is accessible only inside the class. If no modifier is specified, package-private is used: access is allowed only within the same package.

In Java, `protected` means access from within the package and from subclasses. This is a common pitfall: `protected` does not mean only "available to subclasses".

### Type checks and casting: `instanceof`

`instanceof` checks whether an object is an instance of a specific class or interface. It is a runtime type check before a safe downcast.

`instanceof` is usually used when code works with a base type, but a specific subtype needs subtype-specific behavior. In modern design, polymorphism is often better, but the mechanism itself is still important to understand.

```java
class Animal {
}

class Cat extends Animal {
    void meow() {
        System.out.println("meow");
    }
}

Animal animal = new Cat();

if (animal instanceof Cat) {
    Cat cat = (Cat) animal;
    cat.meow();
}
```

In newer Java versions, pattern matching for `instanceof` can be used:

```java
if (animal instanceof Cat cat) {
    cat.meow();
}
```

In Android projects, availability depends on the supported Java language features and toolchain.

### Java Singleton implementation

Java has no dedicated keyword for Singleton. The classic implementation uses a `private` constructor, `private static` instance and `public static getInstance()`.

```java
public class MySingleton {
    private static final MySingleton INSTANCE = new MySingleton();

    private MySingleton() {
    }

    public static MySingleton getInstance() {
        return INSTANCE;
    }
}
```

This eager singleton is simple and thread-safe because of class loading. For lazy initialization, use the holder pattern or enum singleton. Double-checked locking is possible, but easy to implement incorrectly without `volatile`.
