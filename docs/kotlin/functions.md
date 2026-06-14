# Functions

This section covers Kotlin functions: extension functions, lambdas, higher-order functions, scope functions and inline mechanisms.

## Functions

### Extension functions

Extension function lets you add a function to an existing type without inheritance and without modifying the original class.

For example, `fun String.isEmail(): Boolean` can be called as `"text".isEmail()`.

```kotlin
fun String.isEmail(): Boolean =
    contains("@") && contains(".")
```

**Important:** extension functions are resolved statically by the compile-time type of the receiver, not virtually like overridden methods. They do not have access to private members of the class.

If a member function and an extension function have the same signature, the member wins.

**In short:** extensions improve readability and API ergonomics, but they do not actually modify the class and are statically dispatched.

### Lambda functions

Lambda is a function literal that can be stored in a variable, passed as an argument or returned from a function.

In Kotlin, lambda is often used in callbacks, collection operators, builders, Compose and coroutines APIs.

Syntax: `{ value -> value * 2 }`. If there is one parameter and its name is omitted, `it` can be used.

```kotlin
val doubled = numbers.map { it * 2 }
```

Lambda can capture variables from the outer scope. Remember that capturing mutable state can complicate reasoning and threading.

**In short:** lambda is an anonymous function value that enables concise callbacks and functional-style APIs.

### Higher-order functions

Higher-order function - a function that takes another function as a parameter or returns a function.

Examples in Kotlin: `map`, `filter`, `fold`, `onClick` callbacks, custom `retry(block: () -> T)`, Compose content lambdas.

Such functions let you separate common control flow from specific behavior, but can create overhead because of function objects.

For performance-sensitive cases, Kotlin offers inline functions, which can remove part of that overhead.

**In short:** higher-order functions make behavior configurable by passing functions as values.

## Scope and inline

### Scope functions: `let` / `run` / `with` / `apply` / `also`

Scope functions temporarily create a scope around an object and help write more compact code. They differ by receiver (`this` or `it`) and return value.

`let` uses `it` and returns the lambda result. It is often used for nullable chains and transformations.

`run` uses `this` and returns the lambda result. It is convenient for calculating a result from several operations on an object.

`with` is similar to `run`, but is called as a regular function: `with(obj) { ... }`. It returns the lambda result.

`apply` uses `this` and returns the object itself. It is often used for configuration or building.

`also` uses `it` and returns the object itself. It is convenient for side effects: logging, debug, additional actions.

```kotlin
val user = User().apply {
    name = "Ada"
    isActive = true
}

val length = user.name?.let { it.length } ?: 0
```

**In short:** use `let` / `run` / `with` when you need lambda result, `apply` / `also` when you need the original object; `this` vs `it` affects readability.

### `inline` / `noinline` / `crossinline`

`inline` asks the compiler to inline the function body and lambda arguments at the call site. This can reduce overhead of higher-order functions and enables reified type parameters.

`noinline` disables inlining for a specific lambda parameter inside an inline function. This is needed if the lambda must be stored in a variable, passed further or used as a regular function object.

`crossinline` forbids non-local return from the lambda. This is needed when the lambda is not called directly, for example inside another object or `Runnable`.

**Important:** `inline` should not be used everywhere. It increases bytecode size and is mainly useful for small higher-order functions, performance-sensitive APIs and reified generics.

**In short:** `inline` removes some lambda overhead and enables `reified`, `noinline` keeps a lambda as an object, `crossinline` forbids non-local returns.

### `reified`

`reified` type parameter can be used only in an inline function. It allows accessing generic type `T` at runtime, for example `value is T` or `T::class`.

Usually, because of type erasure, a generic type is not available at runtime. `inline` + `reified` works because the compiler substitutes the real type at the call site.

Example use cases: `inline fun <reified T> Gson.fromJson(json: String): T` or `filterIsInstance<T>()`.

Without `reified`, `Class<T>` or `KClass<T>` often has to be passed explicitly.

**In short:** `reified` keeps generic type information available inside an inline function despite JVM type erasure.
