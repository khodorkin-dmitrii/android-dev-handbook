# Java Core

Core Java topics for Android development: object equality, collections, generics, access control, casts, and singleton lifetime.

## Objects and Equality

### The `Object` class

`Object` is the root of Java's class hierarchy. Ordinary classes without an explicit superclass extend it implicitly; arrays are objects too. Primitives are not objects, and interfaces do not extend `Object` as a superclass.

Useful methods include `toString()`, `equals()`, `hashCode()`, and `getClass()`. `Object.clone()` performs a shallow copy and normally requires `Cloneable`. Prefer explicit copying when ownership matters.

`wait()`, `notify()`, and `notifyAll()` require ownership of the object's monitor; see [Java Concurrency](concurrency.md). Do not rely on `finalize()` for resource cleanup. Use explicit closing or `try-with-resources`; see [Java Exceptions](exceptions.md).

### The `equals()` / `hashCode()` contract

For references, Java `==` compares identity. `Object.equals()` does the same by default; classes such as `String` override it to compare values. Use `Objects.equals(a, b)` for null-safe equality. Arrays need `Arrays.equals()` or `Arrays.deepEquals()` for content comparison.

A valid `equals()` is reflexive, symmetric, transitive, and consistent while relevant state is unchanged; a non-null object must not equal `null`.

**Equal objects must have equal hashes.** Unequal objects may share a hash. When defining value equality, implement `equals()` and `hashCode()` together using compatible state.

### A class as a `HashMap` key

Overriding these methods is necessary for custom **value equality**, not for every key class: inherited identity equality is valid when identity is intended.

`HashMap` uses a hash to narrow the search, then identifies a matching key by identity or equality. Keep all state involved in equality and hashing stable while the key is stored. Otherwise lookup or removal may fail even using the same object.

Prefer immutable identifiers as keys. Kotlin data classes generate equality and hashing from primary-constructor properties, but mutable properties or mutable nested objects can still make unsafe keys.

## Generics and Collections

### Generics and primitives

Java type arguments must be reference types: use `List<Integer>`, not `List<int>`. Boxing converts primitives to wrappers; unboxing reverses it. Unboxing `null` throws `NullPointerException`, and `==` between two wrappers compares identity, not numeric value.

Type erasure replaces a type parameter with its leftmost bound, or `Object` when unbounded; the compiler inserts casts where needed. Generic signatures may remain as metadata, but an ordinary list does not carry an enforceable runtime element-type argument.

`List<Integer>` is not a subtype of `List<Number>`. Wildcards express permitted use:

- `List<? extends Number>`: read elements as `Number`; cannot safely add a non-null element.
- `List<? super Integer>`: add `Integer` values; reads have type `Object`.

Avoid raw types and unchecked casts. See [Generics](../kotlin/generics.md) for variance and erasure concepts.

Boxed collections may cost more memory and allocations than `int[]` or specialized structures. Boxing does not necessarily allocate a new object every time; optimize measured hot paths.

### `Iterator` and `Iterable`

`Iterable.iterator()` creates an iterator; `hasNext()` checks availability and `next()` returns the next element or throws `NoSuchElementException` when exhausted. Java enhanced `for` supports both `Iterable` and arrays; arrays do not implement `Iterable`.

For an iterator that supports removal, call `remove()` after `next()`, at most once per returned element. It may otherwise throw `UnsupportedOperationException` or `IllegalStateException`.

Structural changes outside an ordinary fail-fast iterator can cause `ConcurrentModificationException`, even in one thread. Detection is best-effort, not a thread-safety guarantee. Concurrent collections have their own iteration contracts.

### Collection interfaces and implementations

| Interface | Meaning | Common implementation |
|---|---|---|
| `List` | Indexed sequence, duplicates allowed | `ArrayList` |
| `Set` | Unique elements | `HashSet` |
| `Queue` | Processing queue; ordering depends on implementation | `PriorityQueue` |
| `Deque` | Queue with operations at both ends; extends `Queue` | `ArrayDeque` |
| `Map` | Unique keys mapped to values; not a `Collection` | `HashMap` |

`Collection` extends `Iterable`; `Map` exposes collection views through `keySet()`, `values()`, and `entrySet()`.

`HashMap` has no iteration-order guarantee and offers expected constant-time basic lookup with well-distributed hashes. `LinkedHashMap` normally preserves insertion order and can use access order. `TreeMap` sorts by natural ordering or a comparator, with logarithmic lookup; comparison returning zero determines key equivalence.

Unmodifiable collections are not necessarily immutable snapshots: a wrapper can reflect changes to its backing collection. See [Collections](../kotlin/collections.md).

## Types and Access

### Access modifiers

For class members:

- `public`: accessible wherever the declaring type is accessible, subject to module boundaries where applicable.
- `private`: accessible within the enclosing top-level class's body, including its nested classes.
- No modifier: package-private, accessible in the same package. Subpackages are separate packages.
- `protected`: accessible in the same package and under subclass-access rules outside it.

Outside the package, a subclass cannot use an arbitrary superclass instance to access a protected instance member: the qualifying reference must have the subclass's type or a subtype. Top-level classes support `public` or package-private, not `private` or `protected`. Interface members have different implicit modifiers.

### Type checks and casting: `instanceof`

`instanceof` tests runtime type compatibility and returns `false` for `null`. A cast changes the reference's compile-time type, not the object. An incompatible reference cast throws `ClassCastException`; casting `null` to a reference type yields `null`.

```java
static void printText(Object value) {
    if (value instanceof String) {
        String text = (String) value;
        System.out.println(text.length());
    }
}
```

With a toolchain and language level supporting pattern matching:

```java
static void printText(Object value) {
    if (value instanceof String text) {
        System.out.println(text.length());
    }
}
```

For Android, distinguish the JDK running Gradle, the configured Java language level, and available runtime APIs. Installing a newer JDK alone does not enable every feature or library API. Prefer polymorphism when repeated type checks duplicate subtype behavior.

### Singleton implementation and lifetime

```java
public final class MySingleton {
    private static final MySingleton INSTANCE = new MySingleton();

    private MySingleton() {}

    public static MySingleton getInstance() {
        return INSTANCE;
    }
}
```

This creates the instance during class initialization, not necessarily at app startup. Class-initialization guarantees safely publish it; they do not make later mutations thread-safe. A holder class can defer construction until its accessor is used. An enum is another option; double-checked locking requires `volatile` and correct synchronization.

The static instance belongs to that loaded class, not all application processes. Android process death loses its state. Avoid retaining Activity or View references in long-lived objects; dependency injection can make ownership and test substitution clearer. See [DI Basics](../di/basics.md).

## References

- [Object contracts](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Object.html)
- [Type erasure](https://docs.oracle.com/javase/tutorial/java/generics/erasure.html)
- [HashMap](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/HashMap.html)
- [JLS access control](https://docs.oracle.com/javase/specs/jls/se25/html/jls-6.html#jls-6.6)
- [JLS enhanced for](https://docs.oracle.com/javase/specs/jls/se25/html/jls-14.html#jls-14.14.2)
- [JLS class initialization](https://docs.oracle.com/javase/specs/jls/se25/html/jls-12.html#jls-12.4.2)
- [Java versions in Android builds](https://developer.android.com/build/jdks)
