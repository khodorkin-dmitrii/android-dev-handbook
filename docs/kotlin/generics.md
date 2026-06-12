# Generics

Раздел про generics в Kotlin: type safety, type erasure и variance через `in` / `out`.

## Основы generics

### Generics Java vs Kotlin

Generics позволяют писать код, работающий с разными типами, сохраняя type safety: `List<String>`, `Repository<User>`, `Result<T>`.

И Java, и Kotlin на JVM используют type erasure: конкретный generic type обычно недоступен в runtime.

Kotlin добавляет declaration-site variance через `out` / `in`, nullable type system, star-projections и reified type parameters для inline functions.

В Java variance обычно выражается use-site wildcards: `? extends T` и `? super T`. В Kotlin чаще пишут `out T` и `in T` прямо в declaration.

**Коротко:** Kotlin generics are still erased on JVM, but Kotlin gives stronger syntax for variance and reified support in inline functions.

## Variance

### Variance: `in` / `out`

Variance описывает, как generic type с subtype-отношениями ведет себя относительно другого generic type.

`out` означает producer: тип можно безопасно читать как `T`, но нельзя принимать `T` как input. Пример: `Source<out T>`. Это похоже на Java `? extends T`.

`in` означает consumer: тип можно безопасно принимать как `T`, но чтение будет менее точным. Пример: `Sink<in T>`. Это похоже на Java `? super T`.

Простая формула PECS: Producer Extends, Consumer Super. В Kotlin: producer - `out`, consumer - `in`.

**Коротко:** use `out` when a type only produces `T`, use `in` when it only consumes `T`.

### Covariance / contravariance / invariance

Covariance означает сохранение subtype-направления. Если `Cat` наследуется от `Animal`, то `Producer<Cat>` можно использовать как `Producer<Animal>`. В Kotlin это обычно `out T`.

Contravariance означает обратное направление. Если `Cat` наследуется от `Animal`, то `Consumer<Animal>` можно использовать как `Consumer<Cat>`. В Kotlin это обычно `in T`.

Invariance означает, что generic types не считаются subtype друг друга: `MutableList<Cat>` не является `MutableList<Animal>`. Это защищает от type-safety ошибок при записи.

Пример проблемы: если бы `MutableList<Cat>` можно было передать как `MutableList<Animal>`, туда можно было бы добавить `Dog`, что сломало бы список котов.

**Коротко:** covariance is for producers, contravariance is for consumers, invariance is the default when both read and write are possible.
