# Java Exceptions

Java exceptions describe runtime errors and controlled failures that an application can handle or pass higher up the call stack.

## Exception Hierarchy

### `Error` vs `Exception`

In Java, all throwable entities inherit from `Throwable`. The two main branches are `Error` and `Exception`.

`Error` usually means a serious JVM/runtime-level problem, for example `OutOfMemoryError` or `StackOverflowError`. These errors are usually not handled like regular business cases.

`Exception` represents errors that an application can potentially work with. `RuntimeException` is a subtype of `Exception` for unchecked errors such as `NullPointerException`, `IllegalArgumentException` or `IndexOutOfBoundsException`.

### Checked vs unchecked exceptions

Checked exceptions are exceptions that Java forces code either to handle with `catch` or declare in the method signature with `throws`.

Unchecked exceptions are `RuntimeException` and `Error`. They do not have to be declared or caught, but that does not mean they should be ignored.

Kotlin does not have checked exceptions at the language level: the compiler does not force Java checked exceptions to be caught. So when working with Java APIs from Kotlin, you need to understand which errors are possible.

## Exception Handling

### `try` / `catch` / `finally` / `throw` / `throws`

`try` wraps code that can throw an exception. `catch` intercepts and handles a specific exception type.

`finally` runs after `try` / `catch` and is usually used for cleanup. But for closeable resources in Java, `try-with-resources` is better because it is safer and shorter.

`throw` explicitly throws an exception. `throws` in a method signature declares that the method can throw a checked exception and shifts handling responsibility to the caller.

```java
try {
    repository.load();
} catch (IOException exception) {
    logger.log(exception);
} finally {
    repository.close();
}
```

**Practical note:** do not swallow an exception with an empty `catch`. If the error cannot be handled at the current level, it is better to pass it higher, wrap it in a domain exception or log it with enough context.
