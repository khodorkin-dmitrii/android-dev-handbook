---
hide:
  - navigation
---

## Основы System Design

### Что такое system design?

System design описывает, как продукт работает целиком: от клиентов и API до сервисов, хранилищ, кэшей, очередей, workers и внешних систем. Для мобильного инженера ключевой сдвиг - от кода внутри приложения к поведению всей распределённой системы.

### Чем system design отличается от архитектуры приложения?

Архитектура приложения организует код внутри одного клиента. System design прослеживает ответственность и данные между несколькими компонентами.

```text
Архитектура приложения: UI -> ViewModel -> use case -> repository -> local/remote data
System design: Mobile client -> APIs -> services -> databases / caches / queues / workers
```

### Что такое граница системы?

Граница системы определяет, чем владеет проектируемое решение, а что считает внешней зависимостью. Явные границы проясняют ответственность, контракты, trust zones и владение сбоями.

### Что такое функциональные требования?

Функциональные требования описывают, что должны уметь пользователи или другие системы: например, загружать media, отправлять сообщения, редактировать данные offline или получать уведомления.

### Что такое нефункциональные требования?

Нефункциональные требования описывают свойства и ограничения системы: latency, throughput, availability, durability, consistency, безопасность, стоимость и удобство эксплуатации.

### Почему предположения и ограничения нужно фиксировать явно?

Трафик, объём данных, регионы, качество связи, бюджет, ограничения платформы и регуляторные правила могут изменить дизайн. Скрытые предположения делают архитектуру корректной только пока реальность им соответствует.

### Что такое ответственность компонента?

Ответственность компонента - конкретная задача, которой он владеет. Хорошие границы уменьшают пересечение ролей и показывают, кто отвечает за данные, validation, persistence, retries или внешнее взаимодействие.

### Что такое интерфейс или контракт между компонентами?

Контракт определяет способ взаимодействия и гарантии сторон. Это может быть API, event schema, граница базы данных или protocol; важно описывать success, validation, compatibility и failure semantics.

### Что такое data ownership?

Data ownership означает, какой компонент авторитетно меняет конкретное состояние. Другие компоненты могут его кэшировать или реплицировать, но не должны незаметно становиться конкурирующими владельцами.

### Что такое source of truth?

Source of truth - основной владелец, из которого выводится конкретное представление состояния. Область важна: локальная база может быть source of truth для UI, а backend - authority для общего доменного состояния.

### Что такое latency?

Latency - время выполнения одной операции с выбранной точки измерения. Client-perceived latency может включать radio wakeup, DNS/TLS, сеть, серверную обработку, retries и локальный rendering.

### Что такое throughput?

Throughput - объём завершённой работы за единицу времени, например requests/sec, messages/sec или jobs/min. Высокий throughput не гарантирует низкую latency.

### Как выглядит базовый процесс system design?

Сначала определяют требования, затем ограничения и предположения, high-level architecture, data model и API, критические data flows, scaling strategy, failure handling и trade-offs. Процесс итеративный: новые ограничения могут менять более ранние решения.

## Scalability & Capacity

### Что такое scalability?

Scalability - способность системы выдерживать рост пользователей, трафика, данных или работы без неприемлемого ухудшения качества или стоимости.

### Что такое capacity planning?

Capacity planning помогает оценить, когда ресурс достигнет предела. Его задача - заранее найти вероятные ограничения, а не предсказать каждое production-число точно.

### Что такое RPS?

**RPS (Requests Per Second)** - число запросов в секунду. Это полезная метрика, но она не отражает размер payload, стоимость операции, число соединений, рост storage или внешние quotas.

### Почему среднего RPS недостаточно?

Среднее скрывает пики, региональную концентрацию, запуски кампаний, retries, bursts и дорогие endpoints. Capacity оценивают для пиковых критических путей, а не только по среднему за день.

### Что такое concurrency?

Concurrency - число операций или соединений, выполняющихся одновременно. Система может иметь умеренный RPS, но перегружаться из-за большого числа долгих или медленных запросов.

### Что такое вертикальное масштабирование?

Вертикальное масштабирование добавляет одному узлу CPU, память или I/O capacity. Оно проще, но одна машина имеет пределы и остаётся одним failure domain без отдельной redundancy.

### Что такое горизонтальное масштабирование?

Горизонтальное масштабирование добавляет больше узлов. Оно повышает capacity и redundancy, но требует routing, coordination, deployment, observability и управления состоянием между экземплярами.

### Что значит stateless service?

Stateless service хранит долговечное состояние запроса вне процесса, поэтому запрос можно направить любому взаимозаменяемому экземпляру. Временное in-memory состояние допустимо, если корректность не зависит от конкретного instance.

### Что такое load balancer?

Load balancer распределяет трафик между экземплярами. Он может улучшить utilization и availability, но не устраняет downstream bottleneck, например перегруженную базу.

### Что такое bottleneck?

Bottleneck - ресурс, который сейчас ограничивает performance или capacity системы. Это может быть CPU, записи в БД, hot partition, lock, connection pool, внешняя quota или медленный network path.

### Что такое hotspot?

Hotspot - непропорционально нагруженный key, partition, tenant, region или resource. Общая capacity может выглядеть достаточной, пока один hotspot создаёт latency и ошибки.

### Что такое backpressure?

Backpressure ограничивает, задерживает или отклоняет новую работу, когда downstream capacity исчерпана. Это не даёт очередям расти бесконечно и помогает перегруженным компонентам восстановиться.

### Как мобильные клиенты создают всплески нагрузки?

Polling intervals, reconnect storms после восстановления сети, push-triggered refresh, массовые app launches после уведомлений, retries и long-lived realtime connections могут создавать bursts, которых не видно по DAU и среднему RPS.

## Data Storage & Consistency

### Как выбирать хранилище?

Начинайте с data ownership, access patterns, требований к транзакциям и consistency, масштаба, failure behavior и стоимости. «SQL против NoSQL» - это инженерный выбор по требованиям, а не идеология.

### Когда удобно реляционное хранилище?

Реляционное хранилище удобно, когда важны связи, структурированные запросы, constraints и multi-record transactions. Реляционная база тоже может масштабироваться и не является только выбором для маленькой системы.

### Когда полезно нереляционное хранилище?

Document, key-value и wide-column storage подходят для простых известных access patterns, гибкой схемы, специализированных нагрузок или систем, где horizontal partitioning играет центральную роль.

### Что такое индекс?

Индекс - дополнительная структура данных, ускоряющая выбранные чтения. Он занимает storage и удорожает запись, поэтому индексы должны соответствовать реальным query patterns.

### Что такое replication?

Replication создаёт копии данных для redundancy, локальности или увеличения read capacity. Реплики могут отставать от primary, поэтому чтение копии иногда возвращает stale state.

### Что такое read replica?

Read replica обслуживает чтения из реплицированной копии вместо primary. Она снижает read load primary, но replication lag может нарушать ожидания immediate read-after-write.

### Что такое partitioning или sharding?

Partitioning, или sharding, делит данные между узлами, обычно по ключу. Неудачный partition key создаёт hot partitions, неравномерный storage и дорогие cross-partition operations.

### Что такое транзакция?

Транзакция объединяет операции под заданными гарантиями atomicity и isolation. Она нужна для защиты invariants, которые должны изменяться вместе.

### Что такое durability?

Durability отвечает на вопрос, переживут ли подтверждённые данные отказ процесса, узла или региона. Гарантия зависит от logging, replica acknowledgements и выбранной failure model.

### Что такое strong consistency?

Strong consistency - общий термин для гарантий, не позволяющих клиентам наблюдать произвольно устаревшее состояние. Когда точность важна, лучше явно назвать гарантию: linearizable reads, read-after-write или session-level consistency.

### Что такое eventual consistency?

Eventual consistency допускает временное расхождение реплик, но требует их сходимости после прекращения обновлений и успешной доставки. Это не случайные или неопределённые данные.

### Что такое read-after-write consistency?

Read-after-write consistency означает, что клиент может увидеть свою завершённую запись в последующих чтениях в заявленной области. Это особенно важно для пользовательских обновлений вроде изменения профиля.

### Что на самом деле говорит CAP theorem?

**CAP** - Consistency, Availability, Partition tolerance. При network partition для затронутой операции приходится выбирать компромисс между consistency и availability; CAP не означает «выбрать любые два свойства» для всей системы.

## Caching & Data Freshness

### Что такое cache?

Cache хранит переиспользуемую копию данных ближе к потребителю или в более быстром хранилище. Он снижает latency и source load, но создаёт вопросы freshness, invalidation, eviction и failure behavior.

### Что такое cache hit?

Cache hit происходит, когда нужное значение найдено и возвращается из cache. Cache miss переводит чтение к исходному source of truth.

### Что такое cache-aside?

В cache-aside приложение явно проверяет cache и при miss читает source of truth.

```text
Client -> Service -> Cache
                    | miss
                    v
                 Database
                    |
                    +-> populate cache
```

### Что такое TTL?

**TTL (Time To Live)** ограничивает время переиспользования cache entry. Короткий TTL обычно повышает freshness, но увеличивает misses и нагрузку на источник.

### Что такое cache invalidation?

Cache invalidation удаляет или протухает cached data после изменения авторитетного значения. Главная сложность - races, failed invalidations и связанные cache keys.

### Что такое eviction?

Eviction удаляет entries из-за истечения срока или нехватки ресурса. Политика eviction влияет на hit rate, использование памяти и то, какие данные остаются hot.

### Что такое cache warming?

Cache warming заранее загружает вероятно нужные entries. Это уменьшает cold-start misses, но чрезмерный warming может тратить ресурсы или перегружать зависимости.

### Что такое stale-while-revalidate?

Stale-while-revalidate быстро возвращает ограниченно устаревшее значение и обновляет его в фоне. Это компромисс между freshness, latency и availability.

### Что такое negative caching?

Negative caching на короткое время сохраняет известный отрицательный результат, например «resource not found». Transient network/server/auth failures нельзя кэшировать вслепую, иначе cache может скрыть восстановление.

### Что такое cache stampede?

Cache stampede, или thundering herd, возникает, когда множество клиентов одновременно перезагружают одну популярную запись после expiration. Помогают request coalescing, jittered TTL, bounded stale serving и controlled warming.

### Что происходит при отказе cache?

При недоступности cache трафик может резко провалиться в базу или другой источник. Capacity planning должен учитывать этот degraded mode.

### Что такое client-side cache?

Client-side cache хранит данные на устройстве, снижает latency и network usage и может поддерживать offline. Но это всё равно replica, для которой нужны правила refresh, staleness, storage и cleanup.

### Что означает freshness для mobile UI?

Freshness - продуктовый контракт, а не только timestamp. UI может показывать stale state, pending local writes и ситуацию, когда latest server state ещё неизвестен.

## Async Processing & Messaging

### Что такое asynchronous processing?

Asynchronous processing разделяет принятие и завершение. Система фиксирует intent, возвращает `pending` или `accepted`, а саму работу выполняет позже.

### Зачем выносить работу из request-response path?

Медленная или дорогая работа может не укладываться в request budget и удерживать серверные ресурсы. Background workers улучшают отзывчивость и помогают поглощать bursts.

### Что такое queue?

Queue буферизует работу между producers и consumers. Она помогает контролировать concurrency и обрабатывать jobs со скоростью, которую выдерживают downstream systems.

### Кто такой producer?

Producer создаёт и отправляет message или job в queue/broker. Он должен определять payload contract и момент durable acceptance.

### Кто такой consumer или worker?

Consumer/worker получает queued work и выполняет обработку. Он должен учитывать retries, duplicates, failures и observability согласно delivery model.

### Что такое pub/sub?

Publish/subscribe позволяет producer публиковать event без выбора конкретного consumer. Независимые subscribers реагируют на одно событие, обеспечивая fan-out.

### Что такое fan-out?

Fan-out означает, что одно событие запускает работу нескольких независимых consumers, например analytics, notifications и indexing.

### Что такое at-most-once delivery?

At-most-once избегает broker-driven redelivery, но работа может потеряться при сбое сообщения или acknowledgement.

### Что такое at-least-once delivery?

At-least-once повторяет доставку, поэтому consumers должны ожидать duplicates. Для side effects обычно нужна idempotency или deduplication.

### Что означает exactly-once?

Exactly-once имеет смысл только в чётко определённой границе и наборе гарантий. End-to-end business side effects часто всё равно требуют idempotency или deduplication.

### Что такое DLQ?

**DLQ (Dead-Letter Queue)** изолирует сообщения, которые постоянно завершаются ошибкой. Это не решение само по себе: нужны alerts, diagnosis, retention, correction и safe replay.

### Почему ordering требует scope?

Global ordering дорог и часто не нужен. Достаточно порядка в рамках account, conversation, entity или partition - но эта область должна быть явно обозначена.

### Как мобильный клиент отслеживает асинхронную операцию?

Сервер должен вернуть стабильный operation/job ID. Mobile process может исчезнуть после `pending`, поэтому статус нужно уметь восстановить позже через refresh, polling, realtime updates или push-triggered reconciliation.

## Reliability & Failure Handling

### Что такое partial failure?

Partial failure означает, что один dependency, request, region или component отказал, пока остальная система продолжает работать. Distributed system должна явно определять поведение в таких смешанных состояниях.

### Что на самом деле означает timeout?

Timeout означает, что caller перестал ждать. Это не доказывает, что remote operation завершилась ошибкой: сервер мог закончить её уже после timeout.

### Почему retries могут быть опасны?

Retries умножают нагрузку и могут повторять side effects. Если первый запрос успешно выполнился, но response потерялся, blind retry способен применить операцию дважды.

### Что такое exponential backoff?

Exponential backoff увеличивает задержку между повторными попытками. Он снижает давление на unhealthy dependency по сравнению с быстрыми фиксированными retries.

### Что такое jitter?

Jitter добавляет случайность к retry delay, чтобы множество клиентов не повторяли запрос одновременно. Это снижает риск synchronized retry storm.

### Что такое retry budget?

Retry budget ограничивает дополнительный retry traffic, который система готова создать. Он не даёт recovery logic стать вторым источником overload.

### Что такое retry ownership?

Retry ownership определяет, какой слой отвечает за повтор одной logical operation. UI callback, HTTP client, repository, gateway, service и background worker не должны независимо умножать один и тот же retry.

### Что такое idempotency?

Idempotent operation можно повторить, не применяя один business effect несколько раз. Это особенно важно, когда outcome предыдущего request неизвестен.

### Что такое idempotency key?

Idempotency key идентифицирует одну logical mutation при повторных requests. Service должен хранить key и result в определённых scope и retention; один header сам по себе не создаёт idempotency.

### Что такое circuit breaker?

Circuit breaker временно прекращает вызовы failing dependency после порога ошибок, ждёт cooldown и затем допускает ограниченные probes перед возвратом normal traffic.

### Что такое graceful degradation?

Graceful degradation сохраняет core behavior при отказе optional dependency. Fallback должен оставаться безопасным: stale recommendations могут быть допустимы, stale authorization decisions - нет.

### Чем liveness отличается от readiness?

Liveness отвечает, жив ли process настолько, что restart может помочь. Readiness - должен ли instance сейчас получать traffic. Dependency health полезно наблюдать отдельно, чтобы общий downstream outage не удалил из routing весь upstream tier.

### Что такое observability?

Observability использует logs, metrics, traces и domain signals, чтобы понять production behavior. Полезны latency percentiles, error rate, saturation, queue age, dependency health и user-visible outcomes.

## System Design Diagrams

### Зачем нужны system design diagrams?

Диаграмма должна отвечать на конкретный инженерный вопрос. Она показывает boundaries, ownership, data flow, ordering или failure paths без копирования всех implementation details.

### Что такое high-level architecture diagram?

High-level architecture diagram показывает основные компоненты системы и их зависимости. Она полезна для обсуждения boundaries, responsibilities, trust zones и возможных bottlenecks.

### Что такое component diagram?

Component diagram показывает крупные ответственности и связи между компонентами. Важно держать один уровень абстракции и не смешивать classes, cloud resources, tables и user journeys.

### Что такое sequence diagram?

Sequence diagram показывает порядок взаимодействий участников в одном сценарии. Особенно полезна для timeouts, retries, races, acknowledgements и partial failures.

### Зачем показывать failure branch в sequence diagram?

Happy path скрывает неопределённость. Timeout, lost response, retry или pending state помогают увидеть, когда система действительно знает outcome операции, а когда нет.

### Что такое data-flow diagram?

Data-flow diagram показывает, где данные возникают, двигаются, преобразуются и сохраняются. Она помогает анализировать sources of truth, replicas, privacy, retention и reconciliation.

### Что такое C4 model?

C4 model использует уровни приближения: System Context, Container, Component и Code. Для многих системных обсуждений достаточно Context и Container.

### Что такое System Context diagram?

System Context diagram показывает пользователей, проектируемую систему и внешние системы. Это самый широкий полезный boundary.

### Что такое Container diagram в C4?

Container diagram показывает запускаемые или развёртываемые части: mobile app, API, worker, database или web app. Здесь `Container` не обязательно означает Docker.

### Когда полезна state diagram?

State diagram полезна, когда корректность зависит от явных states и transitions, например для payment, upload или synchronization workflow.

### Когда class diagram менее полезна?

Class diagram хуже подходит, если вопрос о capacity, network flow, service boundaries или failure behavior. Нужно выбирать тот тип диаграммы, который отвечает на реальный вопрос.

### Что должны означать стрелки на диаграмме?

Стрелки должны ясно показывать direction и semantics. При необходимости подписывайте actions, protocols, events, mutations, acknowledgements или async boundaries.

### Что делает диаграмму хорошей?

Хорошая диаграмма имеет ясный scope, один уровень abstraction, осмысленные names, видимые durable state и boundaries и достаточно пояснений для принятия решения. Устаревшую диаграмму нужно обновить или удалить.

## Offline-First Mobile Application

### Что означает offline-first?

Offline-first приложение остаётся полезным при нестабильной связи. Пользователь читает ранее загруженные данные, делает локальные изменения и синхронизирует их позже без скрытой потери работы.

### Почему локальная база может быть source of truth для UI?

Один observable local source не заставляет UI переключаться между независимыми network и database states. Network sync обновляет local store, а UI продолжает наблюдать одну модель.

### Означает ли local source of truth, что сервер больше не authoritative?

Нет. Local database может быть source of truth для presentation, а backend остаётся authority для shared domain state, authorization и cross-device coordination.

### Что такое pending mutation?

Pending mutation - durable запись локального изменения, ещё не подтверждённого сервером. Она позволяет восстановить sync после process death или потери connectivity.

### Зачем mutation нужен стабильный operation ID?

Stable operation ID позволяет server распознать retry той же logical change. Это критично, когда client не знает, завершился ли предыдущий request.

### Почему pending mutations нужно хранить persistently?

In-memory queue исчезает при process death. Совместное сохранение visible change и mutation не даёт обновить local state без сохранения работы, необходимой для sync.

### Что такое optimistic update?

Optimistic update сразу меняет local UI до server confirmation. Это повышает responsiveness, но требует pending/failed state и recovery path при rejection.

### Что делать, если app умер во время `in_flight` mutation?

`in_flight` должен описывать attempt, а не вечную истину. После restart, timeout или expired lease незавершённая работа снова становится retryable или проходит reconciliation с тем же stable operation ID.

### Как должны работать retries в offline sync?

Transient failures оставляют mutation durable и повторяются позже с bounded attempts, backoff и jitter. Permanent validation/auth errors не должны повторяться бесконечно.

### Почему connectivity callback не доказывает доступность backend?

Устройство может иметь network route, но DNS, TLS, API, authentication или dependency всё ещё недоступны. Connectivity change может запустить попытку, но результат request остаётся authoritative.

### Что такое conflict в offline-first sync?

Conflict возникает, когда local и server versions изменились независимо. Правильное разрешение зависит от domain semantics, а не от одной универсальной политики.

### Какие conflict strategies бывают?

Частые варианты: server-wins, client-wins, last-write-wins, field-level merge и domain-specific resolution. Каждый вариант меняет риск потери local или remote intent.

### Что такое tombstone?

Tombstone сохраняет факт удаления entity, не стирая сразу всю информацию. Это позволяет синхронизировать deletion с server и replicas до cleanup.
