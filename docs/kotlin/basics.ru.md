# Kotlin Basics

Базовые темы Kotlin, которые важно понимать перед работой с Android-кодом: изменяемость, null-safety, корневые типы, сравнение, приведение типов и правила наследования.

## Основы языка

### `val` vs `var`

`val` - read-only reference: после инициализации переменную нельзя переназначить. `var` - mutable reference: переменной можно присвоить новое значение.

Важно: `val` не делает сам объект immutable. Например, `val list = mutableListOf(1, 2, 3)` запрещает переназначить `list`, но не запрещает изменить содержимое списка через `list.add(4)`.

```kotlin
val names = mutableListOf("Ada", "Linus")
names.add("Grace")

var count = 1
count = 2
```

В обычном Kotlin-коде лучше начинать с `val` и переходить на `var` только там, где изменение ссылки действительно нужно. Это снижает количество случайных изменений состояния и делает код проще для чтения.

### Nullable types

Nullable type - это тип, который может хранить `null`. В Kotlin nullability является частью type system: `String` не может быть `null`, а `String?` может.

Компилятор заставляет явно обработать nullable value. Обычно для этого используют safe call `?.`, Elvis operator `?:`, проверку на `null` со smart cast или, в редких случаях, not-null assertion `!!`.

```kotlin
val name: String? = user.name
val length = name?.length ?: 0
```

Главный риск - `!!`. Он отключает защиту компилятора и может привести к `NullPointerException`, поэтому в production-коде его лучше избегать или использовать только там, где invariant действительно гарантирован.

### `Any` / `Unit` / `Nothing`

`Any` - корневой non-null тип в Kotlin, похожий на Java `Object`. У него есть базовые методы `equals()`, `hashCode()` и `toString()`. Если значение может быть `null`, используется `Any?`.

`Unit` - тип результата функции, которая не возвращает полезное значение. Это близко к Java `void`, но в Kotlin `Unit` является настоящим типом с единственным значением `Unit`.

`Nothing` - тип, у которого нет значений. Он используется для кода, который никогда нормально не возвращается: например, функция всегда выбрасывает exception, вызывает `error()` или содержит бесконечный loop.

```kotlin
fun log(message: String): Unit {
    println(message)
}

fun fail(message: String): Nothing {
    throw IllegalStateException(message)
}
```

### `==` vs `===`

`==` проверяет structural equality - равенство значений через `equals()`. В Kotlin выражение `a == b` примерно раскрывается как `a?.equals(b) ?: (b == null)`.

`===` проверяет referential equality - указывают ли две переменные на один и тот же объект в памяти.

Для `data class` оператор `==` сравнивает свойства из primary constructor. `===` нужен заметно реже, обычно когда важна identity объекта: singleton, `object`, cache identity или проверка, что две ссылки ведут на один instance.

```kotlin
data class User(val id: Long)

val first = User(1)
val second = User(1)

println(first == second)  // true
println(first === second) // false
```

### `as` and `as?`

`as` - unsafe cast. Он приводит объект к указанному типу, но если тип несовместим, будет `ClassCastException`.

`as?` - safe cast. Он возвращает объект нужного типа или `null`, если привести тип невозможно.

```kotlin
val value: Any = "Android"

val text = value as String
val number = value as? Int
```

Часто явный cast вообще не нужен: после проверки через `is` компилятор делает smart cast.

```kotlin
if (value is String) {
    println(value.length)
}
```

### `open` / `final` by default

В Java классы и методы можно наследовать или переопределять по умолчанию, если они не `final`. В Kotlin наоборот: классы и members `final` по умолчанию.

Чтобы разрешить наследование класса или override метода/свойства, нужно явно написать `open`. При переопределении используется `override`. Если переопределенный member не должен переопределяться дальше, его можно явно пометить как `final override`.

```kotlin
open class BaseRepository {
    open fun load() = "data"
}

class UserRepository : BaseRepository() {
    final override fun load() = "users"
}
```

Такой подход заставляет явно проектировать точки расширения и снижает риск случайного переопределения поведения.
