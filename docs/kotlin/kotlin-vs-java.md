# Kotlin vs Java

Kotlin/JVM and Java share the JVM ecosystem and can coexist in one project. Kotlin offers explicit nullability, concise syntax and language features that reduce boilerplate. On Android, their compiled code is converted to DEX and runs on ART, rather than a desktop JVM.

## Language comparison

### Key differences

- Kotlin has nullable types, properties, extension functions, top-level functions and default/named arguments.
- Kotlin classes and ordinary members are final by default; inheritance is explicit.
- Kotlin does not enforce checked exceptions.
- Modern Java also has records and sealed types; these are not exclusive Kotlin capabilities, although their semantics differ.
- Kotlin provides `suspend` support; coroutine builders, dispatchers and Flow primarily come from `kotlinx.coroutines`. A suspending function does not automatically run on a background thread.

Kotlin's read-only collections are not necessarily immutable. More concise code also does not automatically mean faster execution: measure allocations and runtime performance where they matter.

### Visibility modifiers

For ordinary Java classes and members, omitting an access modifier means package-private; interface members have different rules. Kotlin declarations are generally `public` by default.

| Modifier | Kotlin meaning | Java comparison |
|---|---|---|
| `public` | Accessible wherever the containing declaration is accessible. Default visibility. | Must normally be written explicitly on classes and class members. |
| `private` | Visible inside the declaring class, or inside the file for top-level declarations. | Java has no top-level functions or file-private equivalent. |
| `protected` | Visible inside the class and subclasses; unavailable at top level. | Java also permits access from the same package. |
| `internal` | Visible within a Kotlin compilation module. | No direct equivalent. |
| package-private | No direct Kotlin modifier. | Access from the same package. |

A Kotlin module is a set of files compiled together, such as a Gradle source set; configured friend relationships can allow additional access, notably from tests. On JVM, `internal` declarations become public to Java. Internal members may have mangled names, but this does not hide every internal API. It is not a security boundary.

### Null-safety in Kotlin and Java

Kotlin distinguishes `String` from `String?`. Accessing a nullable receiver requires a safe call (`?.`), a null check, or an explicit assertion such as `!!`; Elvis (`?:`) provides a fallback.

Java reference types do not intrinsically encode nullability. Nullability annotations and analysis tools help, and Kotlin understands supported annotations on Java APIs.

Kotlin still permits runtime null failures through `!!`, Java interoperability, or initialization problems. Non-null types reduce risk; they do not validate arbitrary external data.

### Platform types

A Java reference with unspecified nullability can appear in Kotlin as a platform type, displayed as `T!` in tooling. This notation cannot be written in Kotlin source.

Kotlin allows such a value to be used as nullable or non-null, but choosing non-null may fail at runtime if Java supplies `null`. At API boundaries, use a nullable local value and handle absence, or validate the contract explicitly. Annotations can eliminate this ambiguity.

### Checked exceptions

Kotlin does not require catching a Java checked exception or declaring it in a function signature. The exception can still occur, so recovery must follow the API contract.

Use `@Throws` when Java callers need a checked exception in the generated method signature. The annotation neither handles the exception nor changes its runtime behavior.

## JVM and interop

### `Int`: primitive or object on JVM

Kotlin exposes one `Int` type with callable methods. JVM code uses primitive `int` where possible, while nullable values and generic collections generally need boxed `Integer` values.

```kotlin
val count: Int = 10
val optionalCount: Int? = 10
val counts: List<Int> = listOf(1, 2, 3)
val packedCounts: IntArray = intArrayOf(1, 2, 3)
```

`IntArray` maps to `int[]`; `Array<Int>` uses boxed elements. Runtime optimizations may remove some allocations, but boxing is relevant in performance-sensitive code. Avoid referential equality (`===`) for numeric value comparisons.

### Kotlin properties in Java

A public `val` normally exposes a getter; a public `var` exposes a getter and setter, unless setter visibility is restricted. A backing field exists only when needed: a computed property can have none.

For example, `val name: String` exposes `getName()`, while `var age: Int` exposes `getAge()` and `setAge(int)`. For `var isOpen: Boolean`, accessor names are `isOpen()` and `setOpen(boolean)`; the `is` naming rule also applies to non-Boolean properties.

`val` means no setter, not that the returned object is immutable or that a custom getter always returns the same value. Field exposure through `@JvmField` or `const val` is a separate API choice.

### Static members

Kotlin has no `static` keyword. Use top-level declarations for standalone functions/constants and `object` when singleton identity is useful. A `companion object` associates an object with a class and permits access through the class name in Kotlin.

These source-level constructs have different JVM representations; calling a member through a class name in Kotlin does not itself make it a Java static method.

### Companion object from Java

An unnamed companion is normally accessed as `ClassName.Companion` from Java. A named companion uses its declared name.

```kotlin
class Parser {
    companion object {
        @JvmStatic
        fun parse(text: String): Int = text.toInt()
    }
}
```

Java can call `Parser.parse("42")` because of `@JvmStatic`. For a companion function, the instance method `Parser.Companion.parse("42")` also remains available.

### Top-level functions from Java

A function in `Utils.kt` normally becomes a static method such as `UtilsKt.someFunction()`. Top-level properties normally expose static accessors, not public fields.

`@file:JvmName("BetterName")` changes the facade name. To share one facade across multiple files in the same package, use the same `@file:JvmName` together with `@file:JvmMultifileClass` in each file. Top-level extensions also become static methods, with the receiver passed as an argument; they do not add virtual members to the receiver class.

### `@JvmStatic`, `@JvmField`, `@JvmOverloads`, `@Throws`

| Annotation | Purpose for Java callers |
|---|---|
| `@JvmStatic` | Exposes a function or property accessor in an object/companion as a static method. |
| `@JvmField` | Exposes an eligible property's backing field without accessors. |
| `@JvmOverloads` | Generates overloads that progressively omit default-valued parameters from the end of the parameter list; it does not generate every argument combination. |
| `@Throws` | Adds declared exceptions to the JVM method signature. |

Without generated or manually written overloads, Java callers normally pass all function arguments; Kotlin named-argument syntax is unavailable in Java. Use these annotations where the Java-facing API benefits, rather than adding them to every declaration.

### `open` / `final` by default

Ordinary Kotlin classes and concrete members are final unless opened. `abstract` members are implicitly open, and an `override` remains overridable unless marked `final override`. A class containing an open member must itself permit inheritance for subclasses to use it.

Ordinary Java instance methods can usually be overridden unless final or private; static methods are hidden, not overridden. Java records are final, so “everything is open in Java” is also an overstatement.

### Sealed classes from Java

Kotlin requires direct subclasses of a sealed class/interface to be named and in the same package and module. Multiplatform declarations have additional source-set rules. An open direct subclass can allow further indirect subclasses.

Kotlin can check that `when` covers every case. With JVM target 17 or higher, Kotlin emits the JVM permitted-subclasses information used by Java sealed hierarchies. Lower targets do not provide the same JVM-level restriction, particularly for sealed interfaces.

Java also supports exhaustive handling of sealed types with suitable language features. On Android, check the toolchain, bytecode target and desugaring support instead of equating the build JDK version with available language/runtime features.

### Data classes vs Java POJOs / records

A Kotlin `data class` derives `equals()`, `hashCode()`, `toString()`, `copy()` and `componentN()` from primary-constructor properties, subject to generation rules and existing implementations. Body properties are excluded from that generated value representation. Data classes cannot be `open`, `abstract`, `sealed` or `inner`.

A Java POJO typically needs manual or generated value methods. A Java record has final component fields and accessors such as `name()`, but no automatically generated Kotlin-style `copy()` or destructuring functions. Kotlin data-class constructor properties can be `val` or `var`.

Neither model guarantees deep immutability. Kotlin `copy()` is shallow, so nested mutable objects remain shared. A Kotlin data class is not automatically a JVM record.

## Related topics

- [Kotlin Basics](basics.md)
- [Classes & Types](classes-and-types.md)
- [Collections](collections.md)
- [Functions](functions.md)

## References

- [Calling Java from Kotlin](https://kotlinlang.org/docs/java-interop.html)
- [Calling Kotlin from Java](https://kotlinlang.org/docs/java-to-kotlin-interop.html)
- [Sealed classes and interfaces](https://kotlinlang.org/docs/sealed-classes.html)
- [Data classes](https://kotlinlang.org/docs/data-classes.html)
