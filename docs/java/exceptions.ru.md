# Java Exceptions

Исключения в Java описывают ошибки выполнения и управляемые сбои, которые приложение может обработать или передать выше по стеку вызовов.

## Иерархия исключений

### `Error` vs `Exception`

В Java все throwable-сущности наследуются от `Throwable`. Две основные ветки - `Error` и `Exception`.

`Error` обычно означает серьёзную проблему уровня JVM/runtime, например `OutOfMemoryError` или `StackOverflowError`. Обычно такие ошибки не пытаются обрабатывать как обычный бизнес-кейс.

`Exception` - это ошибки, с которыми приложение потенциально может работать. `RuntimeException` - подтип `Exception` для unchecked ошибок, например `NullPointerException`, `IllegalArgumentException` или `IndexOutOfBoundsException`.

### Checked vs unchecked exceptions

Checked exceptions - исключения, которые Java заставляет либо обработать через `catch`, либо объявить в сигнатуре метода через `throws`.

Unchecked exceptions - `RuntimeException` и `Error`. Их можно не объявлять и не ловить, но это не значит, что их нужно игнорировать.

В Kotlin checked exceptions нет на уровне языка: компилятор не заставляет ловить Java checked exception. Поэтому при работе с Java API из Kotlin нужно самому понимать, какие ошибки возможны.

## Обработка исключений

### `try` / `catch` / `finally` / `throw` / `throws`

`try` оборачивает код, который может выбросить исключение. `catch` перехватывает и обрабатывает конкретный тип исключения.

`finally` выполняется после `try` / `catch` и обычно используется для cleanup. Но для closeable ресурсов в Java лучше использовать `try-with-resources`, потому что он безопаснее и короче.

`throw` явно выбрасывает исключение. `throws` в сигнатуре метода объявляет, что метод может выбросить checked exception, и переносит ответственность обработки на вызывающий код.

```java
try {
    repository.load();
} catch (IOException exception) {
    logger.log(exception);
} finally {
    repository.close();
}
```

**Практический совет:** не глуши исключение пустым `catch`. Если ошибка не может быть обработана на текущем уровне, её лучше пробросить выше, завернуть в доменное исключение или залогировать с достаточным контекстом.
