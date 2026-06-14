# Design Patterns

Design patterns - повторяемые решения типовых задач проектирования. Они не заменяют понимание задачи, но дают общий язык для обсуждения структуры кода.

GoF (Gang of Four, Банда четырёх) выделили 23 основных паттерна, которые обычно делят на три группы:

- Creational / порождающие: `Abstract Factory`, `Builder`, `Factory Method`, `Prototype`, `Singleton`.
- Structural / структурные: `Adapter`, `Bridge`, `Composite`, `Decorator`, `Facade`, `Flyweight`, `Proxy`.
- Behavioral / поведенческие: `Chain of Responsibility`, `Command`, `Interpreter`, `Iterator`, `Mediator`, `Memento`, `Observer`, `State`, `Strategy`, `Template Method`, `Visitor`.

Ниже - основные паттерны, которые часто встречаются на практике или видны в API.

## Основные паттерны

### Factory Method и Abstract Factory

Factory Method - порождающий паттерн, который инкапсулирует создание одного типа объекта, когда клиентскому коду не нужно знать конкретный класс.

Abstract Factory - порождающий паттерн, который создаёт семейство связанных объектов. Он полезен, когда нужно подменять целый набор реализаций, например разные UI components, parsers или platform-specific dependencies.

**Коротко:** Factory Method решает создание одного продукта, Abstract Factory - создание семейства связанных продуктов.

### Singleton

Singleton - порождающий паттерн, который гарантирует один общий instance класса и глобальную точку доступа к нему.

В Android singleton часто используется для stateless services, repositories, caches или clients, но лучше создавать такие объекты через DI container, а не писать ручной static singleton.

Главный риск Singleton - скрытые зависимости, global state, сложные тесты и проблемы с lifecycle.

### Observer

Observer - поведенческий паттерн, где объект-подписчик получает уведомления об изменениях другого объекта.

В Android похожая идея есть в listeners, `LiveData`, `Flow`, callbacks и UI state subscriptions. Один источник данных сообщает нескольким подписчикам о новых значениях.

Важно помнить про lifecycle и отписку, иначе можно получить memory leak или события после уничтожения экрана.

### Adapter

Adapter - структурный паттерн-прослойка, который позволяет объектам с несовместимыми interfaces работать вместе.

В Android это может быть mapper между API model и domain model, wrapper вокруг legacy service или `RecyclerView.Adapter`, который адаптирует данные к UI.

Идея: не менять существующий код, а добавить прослойку совместимости.

### Strategy

Strategy - поведенческий паттерн, который выносит изменяемый алгоритм в отдельный объект за общим interface.

Это удобно, когда есть несколько вариантов поведения: разные validators, sorters, formatters, retry policies, pricing rules или navigation strategies.

Вместо большого `when` можно выбрать нужную strategy и вызвать общий метод.

### Decorator

Decorator - структурный паттерн, который добавляет объекту новое поведение, не меняя его класс и не создавая сложную иерархию наследования.

Он оборачивает исходный объект и реализует тот же interface. Например, можно добавить logging, caching, retry или analytics вокруг `Repository` или network client.

**Коротко:** Decorator расширяет поведение через composition, а не inheritance.
