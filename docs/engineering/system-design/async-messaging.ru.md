# Async Processing & Messaging

Синхронный request-response подходит, когда вызывающей стороне нужен немедленный результат, а работа укладывается в бюджет запроса. Асинхронная обработка разделяет принятие и завершение: система фиксирует намерение, возвращает состояние `accepted` или `pending`, а работу выполняет позже.

## Очереди и workers

Очередь буферизует работу между **producer**, который отправляет сообщения, и **consumer** или **worker**, который их обрабатывает. Она помогает поглощать всплески, контролировать параллелизм и выносить медленную или дорогую работу из HTTP-запроса.

```mermaid
sequenceDiagram
    participant App as Mobile App
    participant API
    participant Storage as Object Storage
    participant Queue
    participant Worker as Media Processing Worker
    participant DB as Database
    App->>API: create upload
    API-->>App: upload target and upload ID
    App->>Storage: upload bytes
    Storage->>Queue: upload completed
    Queue->>Worker: process durable object
    Worker->>Storage: write processed object
    Worker->>DB: update status and metadata
```

API создаёт стабильную запись о загрузке и возвращает адрес назначения, а байты медиафайла поступают в надёжное object storage. Задача на обработку ставится в очередь только после того, как загруженный объект стал доступен: worker не должен считать, что медиафайл существует, лишь потому что запись о загрузке уже создана. Клиент может получить статус `pending`, а затем опрашивать состояние, наблюдать событие или получить уведомление. Компромисс состоит в eventual processing: принятие запроса ещё не означает готовность результата.

Мобильный процесс может завершиться после получения `accepted` или `pending`. Серверу следует вернуть стабильный идентификатор операции или job, чтобы клиент позже восстановил её статус. Polling, realtime events или push могут инициировать обновление, но push-уведомление обычно должно запускать reconciliation или refresh, а не становиться source of truth.

Глубина очереди, возраст сообщения, суммарная capacity workers и частота ошибок являются важными эксплуатационными сигналами. Backpressure ограничивает producers или параллелизм workers, когда downstream-системы не справляются.

## Pub/sub и event-driven взаимодействие

В publish/subscribe producer публикует событие, не выбирая конкретного worker. Независимые subscribers реагируют на него, обеспечивая fan-out:

```mermaid
flowchart TD
    O[Order Service] -->|order event| B[[Message Broker]]
    B --> E[Email]
    B --> A[Analytics]
    B --> I[Inventory]
```

Прямая связанность уменьшается, но контракты остаются. Нужно определить схемы событий, владение, versioning, privacy, ordering и поведение при replay. Broker является инфраструктурой, а event-driven design - моделью взаимодействия.

## Семантика доставки и обработки

Сбой возможен до обработки или после неё, а acknowledgement может потеряться. Распространённые термины описывают ожидаемое поведение:

- **At-most-once** может потерять работу, но не инициирует повторную доставку со стороны broker.
- **At-least-once** повторяет доставку, поэтому consumers должны учитывать duplicates.
- **Exactly-once** имеет смысл только в точно заданной границе и наборе гарантий. Сквозные side effects часто всё равно требуют idempotency или deduplication.

Идемпотентный consumer может обработать одно логическое сообщение несколько раз, не применив бизнес-эффект повторно. Стабильные идентификаторы сообщения или операции помогают фиксировать выполненную работу.

Гарантия ordering также требует области действия. Глобальный порядок дорог и часто не нужен, а порядка в рамках аккаунта, диалога или partition может быть достаточно. Несколько workers и retries иначе способны изменить порядок сообщений.

## Retries и dead letters

Для временных ошибок используйте ограниченное число retries, backoff и jitter. **DLQ (Dead-Letter Queue)** изолирует сообщения, которые постоянно завершаются ошибкой, чтобы они не блокировали исправную работу. DLQ сама по себе не решает проблему: нужны alerts, диагностика, процедура replay или исправления и правила хранения.

Очередь не гарантирует выполнение работы ровно один раз. Надёжная постановка в очередь, идемпотентность consumer, observability и процедуры восстановления вместе определяют надёжность.

## См. также

- [Основы System Design](fundamentals.ru.md)
- [Scalability & Capacity](scalability-capacity.ru.md)
- [Reliability & Failure Handling](reliability.ru.md)
- [System Design Diagrams](diagrams.ru.md)
