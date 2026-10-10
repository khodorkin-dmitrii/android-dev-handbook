# Async Processing & Messaging

Synchronous request-response is appropriate when the caller needs an immediate result and the work is short enough for the request budget. Asynchronous processing decouples acceptance from completion: the system records intent, returns an accepted or pending state, and performs work later.

## Queues and workers

A queue buffers work between a **producer**, which submits messages, and a **consumer** or **worker**, which processes them. This can absorb bursts, control concurrency, and keep slow or expensive work outside an HTTP request.

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

The API creates a stable upload record and target, while media bytes go to durable object storage. Processing is queued only after the uploaded object is available; a worker must not assume that media exists merely because an upload record was created. Make the completion event recoverable: if the object is durable but queue publication fails, a reconciler or transactional handoff must enqueue it later. The client can receive a `pending` state and later poll, observe an event, or receive a notification. The trade-off is explicit eventual processing: acceptance no longer means the final result exists.

A mobile process may disappear after receiving `accepted` or `pending`. The server should return a stable operation or job identifier so the client can recover status later. Polling, realtime events, or push can prompt an update, but a push notification should normally trigger reconciliation or refresh rather than become the source of truth itself.

Queue depth, message age, worker capacity, and failure rate are important operational signals. Backpressure limits producers or worker concurrency when downstream systems cannot keep up.

## Pub/sub and event-driven communication

In publish/subscribe, a producer publishes an event without selecting one worker. Independent subscribers react to it, enabling fan-out:

```mermaid
flowchart TD
    O[Order Service] -->|order event| B[[Message Broker]]
    B --> E[Email]
    B --> A[Analytics]
    B --> I[Inventory]
```

This reduces direct coupling, but contracts still exist. Event schemas, ownership, versioning, privacy, ordering, and replay behavior need definition. A broker is infrastructure; event-driven design is the communication model.

## Delivery and processing semantics

Delivery can fail before or after processing, and acknowledgement can be lost. Common terms describe intended behavior:

- **At-most-once** may lose work but avoids broker-driven redelivery.
- **At-least-once** retries delivery, so consumers must expect duplicates.
- **Exactly-once** is meaningful only within a precisely stated boundary and set of guarantees. End-to-end side effects often still require idempotency or deduplication.

An idempotent consumer can process the same logical message more than once without applying the business effect twice. Stable message or operation identifiers help record completed work.

Ordering guarantees also need a scope. Global ordering is expensive and often unnecessary; ordering per account, conversation, or partition may be sufficient. Multiple workers and retries can otherwise reorder messages.

## Retries and dead letters

Retry transient failures with bounded attempts, backoff, and jitter. A **DLQ (Dead-Letter Queue)** isolates messages that repeatedly fail so they do not block healthy work. A DLQ is not a resolution by itself: teams need alerts, diagnosis, replay or correction procedures, and retention rules.

Queues do not guarantee that work happens exactly once. Durable enqueueing, consumer idempotency, observability, and recovery procedures together define reliability. Acknowledge the message after durably recording its business effect, within the broker's delivery contract.

## See also

- [System Design Fundamentals](fundamentals.md)
- [Scalability & Capacity](scalability-capacity.md)
- [Reliability & Failure Handling](reliability.md)
- [System Design Diagrams](diagrams.md)
