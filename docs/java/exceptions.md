# Java Exceptions

Java exceptions represent failures that interrupt normal control flow. Code can handle them locally, translate them at an abstraction boundary, or let them propagate up the call stack.

## Exception Hierarchy

### `Throwable`, `Error`, and `Exception`

Only `Throwable` instances can be thrown or caught. Its two main branches are `Error` and `Exception`.

`Error` usually signals a serious JVM or runtime condition, such as `OutOfMemoryError` or `StackOverflowError`. Application code normally does not catch `Error` for recovery. Catching `Throwable` is therefore usually too broad and can also interfere with cancellation or shutdown mechanisms.

`Exception` represents failures an application may be able to handle. `RuntimeException` is its unchecked branch and includes programming or contract violations such as `NullPointerException`, `IllegalArgumentException`, and `IndexOutOfBoundsException`.

### Checked vs unchecked exceptions

A checked exception is any `Throwable` subtype that is not a subtype of `RuntimeException` or `Error`. Java requires code to catch it or declare it with `throws`.

Unchecked exceptions (`RuntimeException` and `Error`) do not have this compile-time requirement. This does not make them harmless: catch an exception only where the code can recover, add useful context, translate it, or perform boundary-level reporting.

Kotlin has no checked exceptions at the language level. The compiler does not require callers to catch exceptions declared by Java APIs, so Kotlin code must still understand their contracts. Use `@Throws` when a Kotlin function must expose declared exceptions to Java callers, including Java-based frameworks.

## Exception Handling

### `try`, `catch`, `finally`, `throw`, and `throws`

`try` encloses code that may fail. `catch` handles matching types; place more specific catches before broader ones because an earlier catch makes later subtypes unreachable. Multi-catch handles alternatives with the same response:

```java
try {
    repository.load();
} catch (IOException | SecurityException exception) {
    logger.log(exception);
    throw new DataLoadException("Unable to load data", exception);
}
```

`throw` throws one exception instance. `throws` declares possible checked exceptions in a method signature and transfers the handling obligation to the caller. Overriding methods cannot add broader checked exceptions than the overridden method permits.

`finally` normally runs whether the `try` completes, returns, or throws, so it can release resources that are not `AutoCloseable`. It is not an absolute guarantee: process or VM termination may prevent it. Avoid `return` or `throw` inside `finally`, because it can hide the original result or exception.

### Try-with-resources

For `AutoCloseable` resources, prefer try-with-resources. Resources close automatically in reverse declaration order:

```java
try (InputStream input = files.open()) {
    return input.readAllBytes();
}
```

If both the body and `close()` fail, the body exception remains primary and the close failure is available through `getSuppressed()`. A manual `finally` block can accidentally replace the original failure.

### Preserve context and causes

Do not use an empty `catch`, catch broad exceptions around unrelated work, or log and immediately rethrow the same exception at every layer. These patterns either hide failures or create duplicate logs.

When translating a low-level exception, preserve the original cause:

```java
throw new DataLoadException("Unable to read user profile", exception);
```

Add context that helps diagnose the operation, but do not log secrets, tokens, personal data, or full response bodies. Exceptions should describe exceptional failures, not routine branches such as an expected empty search result.

On Android, an uncaught exception on the main thread normally terminates the app process. Handle expected failures near the appropriate boundary, convert them into UI state when useful, and keep the original cause available for diagnostics.

## Related topics

- [Java Core](core.md)
- [Java Concurrency](concurrency.md)
- [Coroutines: Scopes & Cancellation](../coroutines-flow/scopes-cancellation.md)

## References

- [Java Language Specification: Exceptions](https://docs.oracle.com/javase/specs/jls/se25/html/jls-11.html)
- [`Throwable`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Throwable.html)
- [The try-with-resources statement](https://docs.oracle.com/javase/tutorial/essential/exceptions/tryResourceClose.html)
- [Kotlin exceptions](https://kotlinlang.org/docs/exceptions.html)
- [Kotlin `@Throws`](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin/-throws/)
