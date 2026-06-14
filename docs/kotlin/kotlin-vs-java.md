# Kotlin vs Java

Kotlin and Java both run on the JVM and interoperate well, but Kotlin adds a more modern type system and more compact syntax.

## Language comparison

### Key differences

Kotlin does not replace the JVM model completely. It builds on top of it and improves safety, expressiveness and interop with Java code.

Key differences: null-safety is built into the language, classes and methods are `final` by default, there are no checked exceptions, and Kotlin has properties, `data class`, `sealed class` / `sealed interface`, extension functions, top-level functions, coroutines and more expressive collections.

**In short:** Kotlin reduces boilerplate, makes some errors visible at compile time and remains compatible with Java APIs.

### Visibility modifiers

In Java, the default modifier is package-private. In Kotlin, the default modifier is `public`.

Kotlin has `public`, `private`, `protected` and `internal`. `internal` means visibility inside a module, but when compiled to JVM such API technically becomes public with name mangling, so it is not a security boundary.

`protected` has an important difference: in Kotlin, `protected` is visible only inside the class and subclasses, while in Java `protected` is also available to other classes in the same package.

**Key idea:** the main difference is Java package-private vs Kotlin `public` by default, plus Kotlin `internal` and stricter `protected`.

| Modifier | Kotlin meaning | Java comparison |
|---|---|---|
| `public` | Accessible from everywhere. Default modifier. | Similar to `public`, but Java default access is package-private, not `public`. |
| `private` | Accessible inside the class or file if this is a top-level declaration. | Similar to `private`. Java package-private is a separate mechanism with no direct Kotlin equivalent. |
| `protected` | Accessible inside the class and subclasses. | Broader in Java: accessible to subclasses and all classes in the same package. |
| `internal` | Accessible inside a Kotlin module. | No direct Java equivalent. On JVM, usually compiled as `public` with name mangling. |
| package-private | Kotlin has no such modifier. | In Java this is default visibility when no modifier is specified. |

### Null-safety in Kotlin and Java

In Kotlin, nullability is part of the type system: `String` cannot be `null`, while `String?` can. The compiler forces nullable values to be handled through safe call `?.`, Elvis operator `?:`, null-check or another explicit solution.

In Java, `null` is usually not expressed in the type, so `NullPointerException` is more often discovered only at runtime. Annotations like `@Nullable` and `@NonNull` help, but they are not a core part of the Java type system.

**Important:** Kotlin does not guarantee absolute protection from `NullPointerException`. `!!`, platform types from Java, initialization errors, reflection and some interop scenarios remain.

**In short:** Kotlin makes null-safety a compile-time concern, but Java API boundaries still require caution.

### Platform types

Platform type - a type coming from Java where Kotlin does not know exact nullability. In the IDE it is often shown as `T!`, for example `String!`.

For such a value, Kotlin relaxes null-checks: it can be assigned both to `String?` and `String`, but the non-null variant can fail at runtime if Java actually returned `null`.

**Practical note:** at the Java API boundary, prefer explicitly choosing a nullable type, checking `null` or relying on correct nullability annotations.

**In short:** platform types are a Java interop compromise where Kotlin cannot fully guarantee null-safety.

### Checked exceptions

Kotlin has no checked exceptions at the language level. The compiler does not force you to catch `IOException` or declare `throws` in the signature.

When calling Java API from Kotlin, a checked exception can still be thrown at runtime, so it should be handled intentionally if it is part of the contract.

If a Kotlin function should be convenient to call from Java and Java compiler should see `throws`, use `@Throws`.

**In short:** Kotlin treats all exceptions as unchecked, but for Java interop `@Throws` can expose exceptions in the Java signature.

## JVM and interop

### `Int`: primitive or object on JVM

In Kotlin, `Int` looks like a regular type: methods can be called on it, and it behaves like a class-like type at the language level.

On JVM, the compiler usually uses primitive `int` when possible. But in nullable types, generics and some interop scenarios, boxing to `java.lang.Integer` happens.

Examples: `val x: Int = 10` is usually primitive; `val x: Int? = 10` and `List<Int>` require boxed representation.

```kotlin
val count: Int = 10
val optionalCount: Int? = 10
val counts: List<Int> = listOf(1, 2, 3)
```

**In short:** Kotlin hides primitive vs boxed distinction at the language level, but the JVM backend optimizes to primitives where possible.

### Kotlin properties in Java

Kotlin property is usually compiled into a private backing field and accessor methods. For `val`, a getter is generated; for `var`, a getter and setter are generated.

For example, `val name: String` is usually visible from Java as `getName()`, while `var age: Int` is visible as `getAge()` and `setAge(int)`.

If a property starts with `is`, the getter may be named `isOpen()`, and the setter - `setOpen(...)`.

**In short:** Kotlin properties are not magic fields for Java; Java usually sees getters and setters.

### Static members

Kotlin has no direct `static` keyword for class members. Instead, it uses top-level declarations, `object declarations` and `companion object`.

Top-level functions and properties are compiled into static members of a special generated class. `object` provides a singleton. `companion object` provides static-like access through the class name in Kotlin.

For Java interop, `@JvmStatic`, `@JvmField`, `const val` or `@file:JvmName` are sometimes needed so the API looks more Java-friendly.

**In short:** Kotlin replaces `static` with top-level declarations, objects and companion objects, while JVM bytecode still may contain static members.

### Companion object from Java

`companion object` is a real object associated with a class. From Kotlin, its members can be called as `ClassName.member()`.

From Java, without additional annotations, companion object members are usually available through `ClassName.Companion.member()`.

If `@JvmStatic` is added to a function in a companion object, Java can call it as `ClassName.method()`. The instance method in `Companion` still remains.

**In short:** `companion object` looks static from Kotlin, but from Java it is usually accessed through `Companion` unless `@JvmStatic` is used.

### Top-level functions from Java

Top-level functions and properties in Kotlin are compiled into static methods / fields of a generated class on JVM.

By default, the generated class name is based on the file name: for example, functions from `Utils.kt` will be available from Java roughly as `UtilsKt.someFunction()`.

The name can be changed with `@file:JvmName("BetterName")`. For several files, `@JvmMultifileClass` can be used.

**In short:** top-level Kotlin functions are compiled as static members of a generated file facade class.

### `@JvmStatic`, `@JvmField`, `@JvmOverloads`, `@Throws`

`@JvmStatic` generates a static method for a function or accessor in an `object` / `companion object`, so Java can call it as a regular static member.

`@JvmField` exposes a property as a field for Java without getter/setter, if the property matches the annotation restrictions.

`@JvmOverloads` generates overloaded Java methods or constructors for Kotlin functions with default parameters.

`@Throws` adds a `throws` declaration to the Java signature of a Kotlin function, which matters for checked exceptions on the Java side.

**Key idea:** these annotations are not needed for regular Kotlin code, but help make Kotlin APIs more convenient and understandable for Java callers.

### `open` / `final` by default

In Java, classes and methods can be inherited / overridden by default if they are not `final`. Kotlin is the opposite: classes and members are `final` by default.

To allow class inheritance or method / property override, write `open` explicitly. Overrides use `override`.

If an overridden member should not be overridden further, it can be explicitly marked as `final override`.

**In short:** Kotlin forces explicit inheritance, which reduces accidental overriding and makes class contracts safer.

### Sealed classes from Java

Kotlin `sealed class` / `sealed interface` describes a restricted hierarchy: direct subclasses are known at compile time and must follow Kotlin restrictions by package, module or source set.

In Kotlin, this gives exhaustive `when` without `else` if all variants are covered. Java does not have this Kotlin `when` check, and usage depends on how the sealed hierarchy is compiled and which Java level is used.

Starting with modern JVM targets, Kotlin can use Java sealed mechanisms where compatible, but on Android it is important to remember target / toolchain and not assume Java code will get the same ergonomic exhaustiveness.

**Key idea:** sealed hierarchy in Kotlin is most convenient inside Kotlin code; Java interop depends on bytecode target and Java version.

### Data classes vs Java POJOs / records

Kotlin `data class` is designed for storing data and automatically generates `equals()`, `hashCode()`, `toString()`, `copy()` and `componentN()` based on properties from the primary constructor.

Java POJO usually requires manual or generated boilerplate: fields, constructor, getters, `equals()`, `hashCode()` and `toString()`. Java `record` is closer to `data class` conceptually, but it is a separate Java language feature with a different model and restrictions.

**Important:** `data class` cannot be `open`, `abstract`, `sealed` or `inner`. Properties declared in the class body do not participate in generated `equals()`, `hashCode()`, `copy()` and `componentN()`.

`copy()` performs a shallow copy, so mutable nested objects will be shared between the original and the copy.

**In short:** `data class` is a concise Kotlin model type with generated value-like methods, but it is not deep immutable automatically.
