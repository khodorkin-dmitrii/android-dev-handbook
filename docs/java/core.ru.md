# Java Core

Базовые темы Java, которые важны для Android-разработки: `Object`, равенство объектов, коллекции, generics, модификаторы доступа, приведение типов и singleton.

## Объекты и равенство

### `Object` class

`Object` - базовый класс для всех reference types в Java. Если класс явно ничего не наследует, он неявно наследуется от `Object`.

Ключевые методы `Object`: `toString()`, `equals()`, `hashCode()`, `getClass()`, `clone()`, `wait()`, `notify()` и `notifyAll()`. Методы `wait()` / `notify()` связаны с monitor lock и многопоточностью, а `clone()` используется редко и требует осторожности.

**Важно:** `finalize()` встречается в старых материалах, но в современном Java/Android-коде на него нельзя полагаться для cleanup. Для ресурсов лучше использовать `try-with-resources`, `close()`, lifecycle-aware cleanup или явное управление ресурсами.

### `equals()` / `hashCode()` contract

`equals()` определяет логическое равенство объектов, а `hashCode()` возвращает числовой хэш, который используют `HashMap`, `HashSet` и другие hash-based коллекции.

Главный контракт: если `a.equals(b) == true`, то `a.hashCode()` должен быть равен `b.hashCode()`. Обратное не гарантируется: одинаковый `hashCode()` не означает, что объекты равны, потому что возможны collisions.

Если переопределяешь `equals()`, почти всегда нужно переопределить `hashCode()`. Иначе объект может некорректно работать в `HashMap` / `HashSet`: добавился, но потом не находится.

### Класс как ключ `HashMap`

Если custom class используется как ключ в `HashMap`, нужно корректно переопределить `equals()` и `hashCode()`.

`HashMap` сначала использует `hashCode()` для выбора bucket, а затем `equals()` для проверки конкретного ключа среди возможных collisions. Если контракт нарушен, `get()` и `remove()` могут не найти объект даже при логически равном ключе.

В Kotlin `data class` генерирует `equals()` и `hashCode()` автоматически по свойствам primary constructor. Но mutable поля в ключе `HashMap` опасны: если поле, участвующее в `hashCode()`, изменилось после вставки, ключ может стать недоступным.

## Generics и коллекции

### Generics и примитивы в Java

Java generics работают только с reference types, поэтому `List<int>` невозможен. Для примитивов используются wrapper types: `Integer`, `Long`, `Boolean` и т.д.

Из-за type erasure generic-типы в runtime в основном теряют информацию о конкретном `T`, а операции работают через `Object` и casts. Примитивы не являются `Object`, поэтому для них нужен boxing/unboxing.

На Android это важно для производительности: коллекции вроде `List<Integer>` могут создавать лишние allocations по сравнению с массивами `int[]` или специализированными структурами.

### `Iterator` и `Iterable`

`Iterable` - интерфейс для объектов, которые можно перебирать. Он содержит метод `iterator()`, который возвращает `Iterator`.

`Iterator` - объект, который выполняет сам обход: `hasNext()` проверяет наличие следующего элемента, `next()` возвращает следующий элемент, `remove()` опционально удаляет текущий элемент.

`for-each` в Java работает поверх `Iterable`. Важно не менять коллекцию напрямую во время обхода обычным iterator, иначе можно получить `ConcurrentModificationException`. Для удаления во время обхода используют `iterator.remove()` или безопасные альтернативы.

### Java Collections hierarchy

`Collection` - базовый интерфейс для большинства коллекций Java: `List`, `Set`, `Queue` и `Deque`. `List` хранит упорядоченные элементы, `Set` хранит уникальные элементы, `Queue` / `Deque` описывают очереди.

`Map` не наследуется от `Collection`, потому что хранит пары key-value, а не одиночные элементы. `HashMap`, `TreeMap` и `LinkedHashMap` - разные реализации `Map` с разными гарантиями порядка и сложности.

**Главная мысль:** Java Collections Framework - это набор интерфейсов и реализаций для хранения групп объектов, где важно понимать не только API, но и сложность операций, порядок элементов и требования к `equals()` / `hashCode()`.

## Типы и доступ

### Модификаторы доступа Java

В Java есть `public`, `protected`, package-private и `private`.

`public` доступен отовсюду. `private` доступен только внутри класса. Если модификатор не указан, используется package-private: доступ только внутри того же package.

`protected` в Java означает доступ внутри package и из subclasses. Это частая ловушка: `protected` не означает только "доступно наследникам".

### Type checks and casting: `instanceof`

`instanceof` проверяет, является ли объект экземпляром конкретного класса или интерфейса. Это runtime-проверка типа перед безопасным downcast.

Обычно `instanceof` используют, когда код работает с базовым типом, но для конкретного subtype нужно вызвать специфичное поведение. В современном дизайне часто лучше использовать polymorphism, но сам механизм важно понимать.

```java
class Animal {
}

class Cat extends Animal {
    void meow() {
        System.out.println("meow");
    }
}

Animal animal = new Cat();

if (animal instanceof Cat) {
    Cat cat = (Cat) animal;
    cat.meow();
}
```

В новых версиях Java можно использовать pattern matching for `instanceof`:

```java
if (animal instanceof Cat cat) {
    cat.meow();
}
```

В Android-проектах доступность зависит от версии Java language features и toolchain.

### Java Singleton implementation

В Java нет отдельного ключевого слова для Singleton. Классический вариант - `private` constructor, `private static` instance и `public static getInstance()`.

```java
public class MySingleton {
    private static final MySingleton INSTANCE = new MySingleton();

    private MySingleton() {
    }

    public static MySingleton getInstance() {
        return INSTANCE;
    }
}
```

Такой eager singleton прост и thread-safe за счёт class loading. Для ленивой инициализации используют holder pattern или enum singleton. Double-checked locking возможен, но его легко написать неправильно без `volatile`.
