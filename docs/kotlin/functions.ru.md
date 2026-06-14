# Functions

Раздел про функции Kotlin: extension functions, lambdas, higher-order functions, scope functions и inline-механизмы.

## Функции

### Extension functions

Extension function позволяет добавить функцию к существующему типу без наследования и без изменения исходного класса.

Например, `fun String.isEmail(): Boolean` можно вызывать как `"text".isEmail()`.

```kotlin
fun String.isEmail(): Boolean =
    contains("@") && contains(".")
```

**Важно:** extension functions resolved statically по compile-time типу receiver, а не виртуально как overridden methods. Они не имеют доступа к private members класса.

Если member function и extension function имеют одинаковую сигнатуру, member выигрывает.

**Коротко:** extensions improve readability and API ergonomics, but they do not actually modify the class and are statically dispatched.

### Lambda functions

Lambda - это function literal, который можно сохранить в переменную, передать как аргумент или вернуть из функции.

В Kotlin lambda часто используется в callbacks, collection operators, builders, Compose и coroutines APIs.

Синтаксис: `{ value -> value * 2 }`. Если параметр один и его имя не указано, можно использовать `it`.

```kotlin
val doubled = numbers.map { it * 2 }
```

Lambda может захватывать переменные из внешней области видимости. Важно помнить, что захват mutable state может усложнить reasoning и threading.

**Коротко:** lambda is an anonymous function value that enables concise callbacks and functional-style APIs.

### Higher-order functions

Higher-order function - это функция, которая принимает другую функцию как параметр или возвращает функцию.

Примеры в Kotlin: `map`, `filter`, `fold`, `onClick` callbacks, custom `retry(block: () -> T)`, Compose content lambdas.

Такие функции позволяют отделить общий control flow от конкретного поведения, но могут создавать overhead из-за function objects.

Для performance-sensitive случаев Kotlin предлагает inline functions, которые могут убрать часть overhead.

**Коротко:** higher-order functions make behavior configurable by passing functions as values.

## Scope и inline

### Scope functions: `let` / `run` / `with` / `apply` / `also`

Scope functions временно создают scope вокруг объекта и помогают писать более компактный код. Они отличаются receiver-ом (`this` или `it`) и возвращаемым значением.

`let` использует `it` и возвращает результат lambda. Часто применяется для nullable chain и transformation.

`run` использует `this` и возвращает результат lambda. Удобен для вычисления результата из нескольких операций над объектом.

`with` похож на `run`, но вызывается как обычная функция: `with(obj) { ... }`. Возвращает результат lambda.

`apply` использует `this` и возвращает сам объект. Часто используется для configuration или building.

`also` использует `it` и возвращает сам объект. Удобен для side effects: logging, debug, additional actions.

```kotlin
val user = User().apply {
    name = "Ada"
    isActive = true
}

val length = user.name?.let { it.length } ?: 0
```

**Коротко:** use `let` / `run` / `with` when you need lambda result, `apply` / `also` when you need the original object; `this` vs `it` affects readability.

### `inline` / `noinline` / `crossinline`

`inline` просит компилятор встроить тело функции и lambda-аргументы в место вызова. Это может уменьшить overhead higher-order functions и позволяет использовать reified type parameters.

`noinline` запрещает inline для конкретного lambda-параметра внутри inline function. Это нужно, если lambda надо сохранить в переменную, передать дальше или использовать как обычный function object.

`crossinline` запрещает non-local return из lambda. Это нужно, когда lambda вызывается не напрямую, например внутри другого object или `Runnable`.

**Важно:** `inline` не нужно использовать везде. Оно увеличивает bytecode size и полезно в основном для маленьких higher-order functions, performance-sensitive APIs и reified generics.

**Коротко:** `inline` removes some lambda overhead and enables `reified`, `noinline` keeps a lambda as an object, `crossinline` forbids non-local returns.

### `reified`

`reified` type parameter можно использовать только в inline function. Он позволяет обращаться к generic type `T` в runtime, например `value is T` или `T::class`.

Обычно из-за type erasure generic type недоступен в runtime. `inline` + `reified` работает потому, что компилятор подставляет реальный тип в место вызова.

Пример применения: `inline fun <reified T> Gson.fromJson(json: String): T` или `filterIsInstance<T>()`.

Без `reified` часто приходится передавать `Class<T>` или `KClass<T>` явно.

**Коротко:** `reified` keeps generic type information available inside an inline function despite JVM type erasure.
