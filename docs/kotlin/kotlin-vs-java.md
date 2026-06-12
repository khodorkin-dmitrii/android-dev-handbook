# Kotlin vs Java

Kotlin и Java оба работают на JVM и хорошо взаимодействуют друг с другом, но Kotlin добавляет более современную type system и более компактный синтаксис.

## Сравнение языков

### Key differences

Kotlin не заменяет JVM-модель полностью, а строится поверх нее и улучшает безопасность, выразительность и interop с Java-кодом.

Ключевые отличия: null-safety встроена в язык, классы и методы `final` по умолчанию, нет checked exceptions, есть properties, `data class`, `sealed class` / `sealed interface`, extension functions, top-level functions, coroutines и более выразительные коллекции.

**Коротко:** Kotlin уменьшает boilerplate, делает часть ошибок видимой на этапе компиляции и при этом остается совместимым с Java API.

### Visibility modifiers

В Java модификатор по умолчанию - package-private. В Kotlin модификатор по умолчанию - `public`.

В Kotlin есть `public`, `private`, `protected` и `internal`. `internal` означает видимость внутри module, но при компиляции в JVM такой API технически становится public с name mangling, поэтому это не security boundary.

`protected` отличается важной деталью: в Kotlin `protected` виден только внутри класса и subclasses, а в Java `protected` также доступен другим классам из того же package.

**Главная мысль:** основная разница - Java package-private vs Kotlin `public` by default, плюс Kotlin `internal` и более строгий `protected`.

| Modifier | Kotlin meaning | Java comparison |
|---|---|---|
| `public` | Доступен отовсюду. Модификатор по умолчанию. | Аналог `public`, но в Java default access - не `public`, а package-private. |
| `private` | Доступен внутри класса или файла, если это top-level declaration. | Аналог `private`. Java package-private - отдельный механизм, прямого аналога в Kotlin нет. |
| `protected` | Доступен внутри класса и subclasses. | В Java шире: доступен subclasses и всем классам внутри того же package. |
| `internal` | Доступен внутри Kotlin module. | Прямого аналога в Java нет. На JVM обычно компилируется как `public` с name mangling. |
| package-private | В Kotlin такого модификатора нет. | В Java это default visibility, если модификатор не указан. |

### Null-safety в Kotlin и Java

В Kotlin nullability является частью type system: `String` не может быть `null`, а `String?` может. Компилятор заставляет обработать nullable value через safe call `?.`, Elvis operator `?:`, null-check или другое явное решение.

В Java `null` обычно не выражен в типе, поэтому `NullPointerException` чаще обнаруживается только в runtime. Аннотации вроде `@Nullable` и `@NonNull` помогают, но это не базовая часть Java type system.

**Важно:** Kotlin не гарантирует абсолютную защиту от `NullPointerException`. Остаются `!!`, platform types из Java, ошибки инициализации, reflection и некоторые interop-сценарии.

**Коротко:** Kotlin делает null-safety compile-time проблемой, но при работе с Java API все равно нужна осторожность.

### Platform types

Platform type - это тип, пришедший из Java, у которого Kotlin не знает точную nullability. В IDE он часто отображается как `T!`, например `String!`.

С таким значением Kotlin ослабляет null-checks: его можно присвоить и в `String?`, и в `String`, но non-null вариант может упасть в runtime, если Java реально вернула `null`.

**Практический совет:** на границе с Java API лучше явно выбирать nullable тип, проверять `null` или опираться на корректные nullability annotations.

**Коротко:** platform types - это компромисс Java interop, где Kotlin не может полностью гарантировать null-safety.

### Checked exceptions

В Kotlin нет checked exceptions на уровне языка. Компилятор не заставляет ловить `IOException` или объявлять `throws` в сигнатуре.

При вызове Java API из Kotlin checked exception все равно может быть выброшен в runtime, поэтому его нужно обрабатывать осознанно, если это часть contract.

Если Kotlin-функцию нужно удобно вызывать из Java и дать Java-компилятору увидеть `throws`, используют `@Throws`.

**Коротко:** Kotlin treats all exceptions as unchecked, but for Java interop `@Throws` can expose exceptions in the Java signature.

## JVM и interop

### `Int`: primitive или object на JVM

В Kotlin `Int` выглядит как обычный тип: у него можно вызывать методы, и он ведет себя как class-like type на уровне языка.

На JVM компилятор обычно использует primitive `int`, когда это возможно. Но в nullable типах, generics и некоторых interop-сценариях происходит boxing в `java.lang.Integer`.

Примеры: `val x: Int = 10` обычно primitive; `val x: Int? = 10` и `List<Int>` требуют boxed representation.

```kotlin
val count: Int = 10
val optionalCount: Int? = 10
val counts: List<Int> = listOf(1, 2, 3)
```

**Коротко:** Kotlin hides primitive vs boxed distinction at the language level, but the JVM backend optimizes to primitives where possible.

### Kotlin properties в Java

Kotlin property обычно компилируется в private backing field и accessor methods. Для `val` генерируется getter, для `var` - getter и setter.

Например, `val name: String` из Java обычно виден как `getName()`, а `var age: Int` - как `getAge()` и `setAge(int)`.

Если property начинается с `is`, getter может называться `isOpen()`, а setter - `setOpen(...)`.

**Коротко:** Kotlin properties are not magic fields for Java; Java usually sees getters and setters.

### Static members

В Kotlin нет прямого ключевого слова `static` для членов класса. Вместо этого используются top-level declarations, `object declarations` и `companion object`.

Top-level functions и properties компилируются в static members специального generated class. `object` дает singleton. `companion object` дает static-like доступ через имя класса в Kotlin.

Для Java interop иногда нужны `@JvmStatic`, `@JvmField`, `const val` или `@file:JvmName`, чтобы API выглядел более Java-friendly.

**Коротко:** Kotlin replaces `static` with top-level declarations, objects and companion objects, while JVM bytecode still may contain static members.

### Companion object из Java

`companion object` - это реальный object, связанный с классом. Из Kotlin его members можно вызывать как `ClassName.member()`.

Из Java без дополнительных аннотаций members companion object обычно доступны через `ClassName.Companion.member()`.

Если добавить `@JvmStatic` к функции в companion object, Java сможет вызвать ее как `ClassName.method()`. При этом instance-метод в `Companion` тоже остается.

**Коротко:** `companion object` looks static from Kotlin, but from Java it is usually accessed through `Companion` unless `@JvmStatic` is used.

### Top-level functions из Java

Top-level functions и properties в Kotlin компилируются в static methods / fields generated class на JVM.

По умолчанию имя generated class строится из имени файла: например, functions из `Utils.kt` будут доступны из Java примерно как `UtilsKt.someFunction()`.

Имя можно изменить через `@file:JvmName("BetterName")`. Для нескольких файлов можно использовать `@JvmMultifileClass`.

**Коротко:** top-level Kotlin functions are compiled as static members of a generated file facade class.

### `@JvmStatic`, `@JvmField`, `@JvmOverloads`, `@Throws`

`@JvmStatic` генерирует static method для функции или accessor-а в `object` / `companion object`, чтобы Java могла вызывать его как обычный static member.

`@JvmField` открывает property как field для Java без getter/setter, если property подходит под ограничения аннотации.

`@JvmOverloads` генерирует перегруженные Java-методы или конструкторы для Kotlin-функций с default parameters.

`@Throws` добавляет `throws` declaration в Java signature для Kotlin-функции, что важно для checked exceptions на стороне Java.

**Главная мысль:** эти аннотации нужны не для обычного Kotlin-кода, а чтобы Kotlin API выглядел удобнее и понятнее для Java callers.

### `open` / `final` по умолчанию

В Java классы и методы можно наследовать / переопределять по умолчанию, если они не `final`. В Kotlin наоборот: классы и members `final` по умолчанию.

Чтобы разрешить наследование класса или override метода / свойства, нужно явно написать `open`. При переопределении используется `override`.

Если override member не должен переопределяться дальше, его можно явно пометить `final override`.

**Коротко:** Kotlin forces explicit inheritance, which reduces accidental overriding and makes class contracts safer.

### Sealed classes из Java

Kotlin `sealed class` / `sealed interface` описывает ограниченную иерархию: direct subclasses известны compile-time и должны соблюдать ограничения Kotlin по package, module или source set.

В Kotlin это дает exhaustive `when` без `else`, если все варианты покрыты. В Java такой проверки Kotlin `when` нет, и использование зависит от того, как sealed hierarchy скомпилирована и какой Java level используется.

Начиная с современных JVM targets Kotlin может использовать Java sealed mechanisms там, где это совместимо, но на Android важно помнить о target / toolchain и не рассчитывать, что Java-код получит такой же ergonomic exhaustiveness.

**Главная мысль:** sealed hierarchy в Kotlin удобнее всего раскрывается внутри Kotlin-кода; Java interop зависит от bytecode target и версии Java.

### Data classes vs Java POJOs / records

Kotlin `data class` предназначен для хранения данных и автоматически генерирует `equals()`, `hashCode()`, `toString()`, `copy()` и `componentN()` по свойствам primary constructor.

Java POJO обычно требует ручной или generated boilerplate: fields, constructor, getters, `equals()`, `hashCode()` и `toString()`. Java `record` ближе к `data class` по идее, но это отдельная Java language feature с другой моделью и ограничениями.

**Важно:** `data class` не может быть `open`, `abstract`, `sealed` или `inner`. Свойства, объявленные в body класса, не участвуют в generated `equals()`, `hashCode()`, `copy()` и `componentN()`.

`copy()` делает shallow copy, поэтому mutable вложенные объекты будут разделяться между original и copy.

**Коротко:** `data class` is a concise Kotlin model type with generated value-like methods, but it is not deep immutable automatically.
