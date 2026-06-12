# Collections

Раздел про коллекции Kotlin: read-only и mutable interfaces, реальную immutability и базовые операции над наборами данных.

## Основные коллекции

### `List` vs `MutableList`

`List<T>` в Kotlin - read-only interface: через такую ссылку нельзя вызвать `add()`, `remove()` или `set()`. `MutableList<T>` - mutable interface, который позволяет изменять коллекцию.

**Важно:** read-only не значит immutable. Если один и тот же mutable list передан как `List<T>`, владелец mutable reference все еще может изменить данные.

```kotlin
val mutable = mutableListOf(1, 2)
val readOnly: List<Int> = mutable

mutable.add(3)
println(readOnly) // [1, 2, 3]
```

В API лучше возвращать `List<T>`, если вызывающий код не должен менять коллекцию, и `MutableList<T>` только когда mutation является частью contract.

**Коротко:** `List` is read-only from this reference, `MutableList` allows mutation, but `List` is not a deep immutability guarantee.

### Read-only vs immutable collections

Read-only collection означает, что через данный interface нельзя изменить коллекцию. Immutable collection означает, что коллекция не может измениться вообще после создания.

Стандартные Kotlin `List`, `Set` и `Map` являются read-only interfaces, но под ними может находиться mutable implementation.

Например, `val list: List<Int> = mutableListOf(1, 2)` не дает вызвать `list.add()`, но original mutable reference может добавить элементы.

Для реальной immutable модели нужно контролировать владельца mutable коллекции, делать defensive copy или использовать immutable collections, если они доступны в проекте.

**Коротко:** Kotlin read-only collections protect the API surface, but they do not guarantee true immutability of the underlying object.

## Операции

### `map` / `flatMap` / `filter` / `fold` / `forEach`

`map` преобразует каждый элемент коллекции и возвращает новую коллекцию результатов.

`filter` оставляет только элементы, которые соответствуют predicate.

`flatMap` сначала преобразует каждый элемент в коллекцию или iterable result, а потом flatten-ит результаты в один список.

`fold` аккумулирует одно итоговое значение, проходя по коллекции с initial value и accumulator function.

`forEach` выполняет side effect для каждого элемента и обычно не должен использоваться для построения нового результата.

```kotlin
val names = users
    .filter { it.isActive }
    .map { it.name }

val totalAge = users.fold(0) { acc, user -> acc + user.age }
```

**Коротко:** `map` transforms, `filter` selects, `flatMap` transforms and flattens, `fold` accumulates, `forEach` is for side effects.
