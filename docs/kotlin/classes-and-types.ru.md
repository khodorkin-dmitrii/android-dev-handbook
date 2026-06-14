# Classes & Types

Раздел про классы, объектные декларации и специальные типы Kotlin, которые часто используются в Android-коде для моделей данных, состояния UI и API.

## Классы и модели

### `data class`

`data class` - это класс для хранения данных, для которого Kotlin автоматически генерирует `equals()`, `hashCode()`, `toString()`, `copy()` и `componentN()` по свойствам primary constructor.

Минимальное требование: в primary constructor должен быть хотя бы один параметр, помеченный `val` или `var`.

```kotlin
data class User(
    val id: Long,
    val name: String
)
```

**Важно:** свойства, объявленные в body класса, не участвуют в generated `equals()`, `hashCode()`, `copy()` и `componentN()`. `copy()` делает shallow copy, а не deep copy.

`data class` не может быть `open`, `abstract`, `sealed` или `inner`. В Android `data class` часто используют для DTO, domain models и UI state.

**Коротко:** `data class` reduces boilerplate for value-like models, but it does not make objects deeply immutable automatically.

### `sealed class` vs `enum class`

`enum class` описывает фиксированный набор singleton-констант одного типа. Он удобен для простых состояний без сложных данных или с одинаковым набором свойств и методов.

`sealed class` или `sealed interface` описывает закрытую иерархию типов. Каждый subtype может быть отдельным `class`, `object` или `data class` и хранить разные данные.

Главное преимущество `sealed` - exhaustive `when`: Kotlin может проверить, что все варианты обработаны без `else`.

```kotlin
sealed class Result {
    data class Success(val data: User) : Result()
    data class Error(val message: String) : Result()
    object Loading : Result()
}
```

`enum` подходит для `Loading` / `Success` / `Error`, только если у вариантов нет разных payload. `sealed` лучше, если `Success` хранит data, а `Error` хранит `Throwable` или message.

**Коротко:** `enum` is a fixed set of constants, `sealed` is a restricted type hierarchy with different subclasses and payloads.

## Объекты

### `object` keyword

`object` в Kotlin используется для трех основных сценариев: anonymous objects, object declarations и companion objects.

Anonymous object создается прямо в месте использования. Он удобен для одноразовой реализации interface или небольшого объекта без отдельного named class.

```kotlin
val helloWorld = object {
    val hello = "Hello"
    val world = "World"

    override fun toString() = "$hello $world"
}
```

Object declaration объявляет singleton. Такой объект инициализируется лениво, при первом доступе, и его инициализация thread-safe.

```kotlin
object DataProviderManager {
    fun registerDataProvider(provider: DataProvider) {
        // ...
    }
}
```

Companion object связан с классом. Его members можно вызывать через имя класса, а сам companion object инициализируется при загрузке или разрешении соответствующего класса, что близко к Java static initializer semantics.

```kotlin
class MyClass {
    companion object Factory {
        fun create(): MyClass = MyClass()
    }
}

val instance = MyClass.create()
```

Если имя companion object не указано, он получает имя `Companion`.

**Коротко:** anonymous object инициализируется сразу при использовании, object declaration - лениво при первом доступе, companion object - вместе с соответствующим классом.

### `object` / `companion object` / `class`

`class` описывает blueprint для объектов. Каждый вызов constructor создает новый instance.

`object declaration` создает singleton: один лениво инициализируемый instance на все приложение или classloader. Это удобно для stateless helpers, constants или simple singletons, но global state может усложнить тестирование.

`companion object` - singleton, связанный с конкретным классом. Из Kotlin его members можно вызывать как `ClassName.member()`, но это не то же самое, что Java `static` на уровне языка.

Для Java interop иногда используют `@JvmStatic`, `@JvmField` или `const val`, чтобы companion / object API выглядел привычнее для Java.

**Коротко:** `class` creates instances, `object` creates a singleton, `companion object` provides class-associated members.

## Специальные типы

### `inline class` / `value class`

Value class - это Kotlin-класс-обертка вокруг одного value, объявленный как `@JvmInline value class`. Раньше эта возможность называлась inline class.

Основная идея - дать доменный тип без лишней runtime allocation там, где компилятор может заменить wrapper на underlying value.

```kotlin
@JvmInline
value class UserId(val value: String)
```

Такой тип помогает не путать `UserId` с обычной `String`, даже если внутри хранится строковое значение.

Ограничения: value class должен иметь ровно одно property в primary constructor, не имеет identity, не может хранить backing fields кроме underlying value, а boxing все равно возможен в generics, nullable types и interface usage.

**Коротко:** value class improves type-safety with low overhead, but it is not a normal wrapper object in all runtime scenarios.
