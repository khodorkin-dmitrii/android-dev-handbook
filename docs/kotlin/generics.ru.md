# Generics

Обобщения (generics) позволяют выразить связи между типами и сохранить типобезопасность переиспользуемого кода: `List<String>`, `Repository<User>` или `Result<T>`.

## Основы обобщений

### Kotlin и Java

И Kotlin, и Java на JVM используют стирание типов. Kotlin также поддерживает вариантность в объявлении (`out` / `in`), звёздные проекции и параметры `reified` в inline-функциях. В Java вариантность обычно задают в месте использования через `? extends T` и `? super T`.

Параметр типа может принадлежать классу, интерфейсу или функции; его аргумент часто выводится автоматически:

```kotlin
class Box<T>(val value: T)

fun <T> boxed(value: T): Box<T> = Box(value)

val box = boxed("Kotlin") // Box<String>
```

### Верхние границы и nullable-типы

Верхняя граница по умолчанию - `Any?`, поэтому `T` может быть nullable-типом. Ограничение `T : Any` запрещает nullable-аргумент типа. Граница также определяет доступные операции; несколько ограничений в `where` должны выполняться одновременно:

```kotlin
fun <T> longerFirst(a: T, b: T): T
    where T : CharSequence, T : Comparable<T> =
    if (a.length != b.length) {
        if (a.length > b.length) a else b
    } else {
        if (a >= b) a else b
    }
```

## Вариантность

### Вариантность в объявлении: `out` / `in`

Вариантность определяет, переносится ли отношение подтипов между аргументами типа на обобщённые типы.

| Объявление | Направление при `Cat : Animal` | Роль |
| --- | --- | --- |
| `Source<out T>` | `Source<Cat>` - подтип `Source<Animal>` | Производит `T` |
| `Sink<in T>` | `Sink<Animal>` - подтип `Sink<Cat>` | Потребляет `T` |
| `Box<T>` | Ни `Box<Cat>`, ни `Box<Animal>` не является подтипом другого | Инвариантный тип |

```kotlin
interface Source<out T> {
    fun next(): T
}

interface Sink<in T> {
    fun accept(value: T)
}

fun use(source: Source<String>, sink: Sink<Any>) {
    val objects: Source<Any> = source
    val strings: Sink<String> = sink
    strings.accept("hello")
}
```

В этих интерфейсах `out T` запрещает добавить метод `accept(value: T)`, а `in T` - метод `next(): T`. Ограничения касаются позиций **`T`**, а не любых параметров или возвращаемых значений: потребитель по-прежнему может возвращать `Boolean` или `Unit`.

Без модификатора вариантности параметры типа инвариантны, даже если реализация только читает значения. Среди коллекций `List` ковариантен, а `MutableList` инвариантен: если разрешить использовать `MutableList<Cat>` как `MutableList<Animal>`, в список котов можно будет добавить `Dog`.

Вариантность обеспечивает типобезопасность, но не гарантирует неизменяемость объекта. См. [Коллекции](collections.md).

### Вариантность в месте использования: проекции типов

Проекция ограничивает допустимые операции через конкретную ссылку на инвариантный тип:

```kotlin
fun copyFirst(from: Array<out Number>, to: Array<in Number>) {
    require(from.isNotEmpty() && to.isNotEmpty())
    to[0] = from[0]
}

val source = arrayOf(1, 2)
val destination = arrayOf<Any>("initial")
copyFirst(source, destination)
```

- Из `from` читаем `Number`; присваивать элементы через эту ссылку нельзя.
- В `to` можно записывать `Number`; при чтении элемента получаем `Any?`.
- Сами массивы не становятся неизменяемыми.

### Звёздные проекции: `*`

`List<*>` означает список с неизвестным типом элементов, а не `List<Any?>`. Его элементы можно читать как `Any?`. В `MutableList<*>` нельзя безопасно добавить элемент, даже `null`, поскольку фактический тип элементов неизвестен. При этом операции вроде `clear()` доступны.

В общем случае звёздная проекция позволяет читать значение как верхнюю границу параметра, если у него есть выходная позиция, и запрещает передавать значения в его входную позицию.

## Информация о типах во время выполнения

### Стирание типов и `reified`

Для произвольного значения проверка `is List<*>` определяет тип контейнера; `is List<String>` не может проверить тип его элементов. Непроверяемое приведение `as List<String>` не проверяет все элементы; `as? List<String>` этого тоже не делает.

Inline-функция с `reified T` позволяет выполнять `is T`, `as? T` и обращаться к `T::class`:

```kotlin
inline fun <reified T> matches(value: Any?): Boolean = value is T

val text = matches<String>("hello") // true
val list = matches<List<String>>(listOf(42)) // true: проверяется только List
```

`reified` не восстанавливает стёртые вложенные аргументы типов. Для недоверенных данных проверяйте элементы явно; неизбежные непроверяемые приведения изолируйте и обосновывайте инвариантом. Подробнее об inline-функциях см. [Функции](functions.md).

## Источники

- [Kotlin: Generics](https://kotlinlang.org/docs/generics.html)
- [Kotlin: Type system](https://kotlinlang.org/spec/type-system.html)
- [Kotlin: Collections overview](https://kotlinlang.org/docs/collections-overview.html)
- [Kotlin: Inline functions](https://kotlinlang.org/docs/inline-functions.html)
