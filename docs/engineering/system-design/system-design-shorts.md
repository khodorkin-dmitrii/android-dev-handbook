---
hide:
  - navigation
---

## System Design Fundamentals

### What is system design?

System design describes how a complete product works across clients, APIs, services, storage, caches, queues, workers, and external systems. For a mobile engineer, the key shift is from code inside the app to the behavior of the whole distributed system.

### How is system design different from application architecture?

Application architecture organizes code inside one application. System design follows responsibilities and data across multiple components.

```text
Application architecture: UI -> ViewModel -> use case -> repository -> local/remote data
System design: Mobile client -> APIs -> services -> databases / caches / queues / workers
```

### What is a system boundary?

A system boundary defines what the design owns and what it treats as an external dependency. Clear boundaries make responsibilities, contracts, trust zones, and failure ownership explicit.

### What are functional requirements?

Functional requirements describe what users or other systems must be able to do, such as upload media, send a message, edit data offline, or receive notifications.

### What are non-functional requirements?

Non-functional requirements describe qualities and constraints such as latency, throughput, availability, durability, consistency, security, cost, and operability.

### Why should assumptions and constraints be explicit?

Traffic, data volume, regions, device connectivity, budget, platform limits, and regulatory rules can change the design. Hidden assumptions make an architecture look correct only until real conditions differ.

### What is a component responsibility?

A component responsibility is the specific job a component owns. Good boundaries reduce overlap and make it clearer which component owns data, validation, persistence, retries, or external communication.

### What is an interface or contract between components?

A contract defines how components interact and what each side can rely on. It may be an API, event schema, database boundary, or protocol and should include success, validation, compatibility, and failure semantics.

### What is data ownership?

Data ownership means identifying which component is authoritative for changing a piece of state. Other components may cache or replicate it, but they should not silently become competing authorities.

### What is a source of truth?

A source of truth is the primary owner from which a particular view of state is derived. The exact scope matters: a local database can be the source of truth for mobile UI presentation while the backend remains authoritative for shared domain state.

### What is latency?

Latency is the time one operation takes from the perspective being measured. Client-perceived latency may include radio wakeup, DNS/TLS, network transfer, server processing, retries, and local rendering.

### What is throughput?

Throughput is the amount of work completed per unit of time, for example requests per second, messages per second, or jobs processed per minute. High throughput does not guarantee low latency.

### What is the basic system design process?

Start with requirements, then constraints and assumptions, high-level architecture, data model and APIs, critical data flows, scaling strategy, failure handling, and trade-offs. The process is iterative because discoveries in one step can change earlier decisions.

## Scalability & Capacity

### What is scalability?

Scalability is the ability of a system to handle growth in users, traffic, data, or work without unacceptable loss of quality or cost efficiency.

### What is capacity planning?

Capacity planning estimates when a resource will reach a limit. Its purpose is to identify likely constraints early, not to predict every production number exactly.

### What is RPS?

**RPS (Requests Per Second)** is the number of requests received or processed per second. It is useful, but it does not describe payload size, work cost, concurrent connections, storage growth, or external quotas.

### Why is average RPS not enough?

Average traffic hides peaks, regional concentration, launches, retries, bursts, and expensive endpoints. Capacity should be estimated for peak critical paths, not only daily averages.

### What is concurrency?

Concurrency is the number of operations or connections in progress at the same time. A system can have moderate RPS but still be stressed by many long-lived or slow requests.

### What is vertical scaling?

Vertical scaling gives one node more CPU, memory, or I/O capacity. It is simple, but one machine has limits and remains a single failure domain unless redundancy is added separately.

### What is horizontal scaling?

Horizontal scaling adds more nodes. It can increase capacity and redundancy, but requires routing, coordination, deployment, observability, and state management across instances.

### What does stateless service mean?

A stateless service keeps durable request state outside the process, so requests can be routed to interchangeable instances. Temporary in-memory state may still exist, but correctness must not depend on one specific instance.

### What is a load balancer?

A load balancer distributes traffic across multiple instances. It can improve utilization and availability, but it does not remove downstream bottlenecks such as an overloaded database.

### What is a bottleneck?

A bottleneck is the resource that currently limits system performance or capacity. It may be CPU, database writes, a hot partition, a lock, a connection pool, an external quota, or a slow network path.

### What is a hotspot?

A hotspot is a disproportionately busy key, partition, tenant, region, or resource. Total system capacity can look healthy while one hotspot causes latency or failures.

### What is backpressure?

Backpressure is a mechanism that limits, delays, or rejects incoming work when downstream capacity is exhausted. It prevents unbounded queues and gives overloaded components a chance to recover.

### How can mobile clients create traffic spikes?

Polling intervals, reconnect storms after connectivity returns, push-triggered refreshes, app launches after notifications, retries, and long-lived realtime connections can create bursts that DAU and average RPS do not reveal.

## Data Storage & Consistency

### How should storage be selected?

Start from data ownership, access patterns, transactions, consistency needs, scale, failure behavior, and cost. “SQL vs NoSQL” is a requirements decision, not an ideology.

### When is relational storage attractive?

Relational storage is attractive when relationships, structured queries, constraints, and multi-record transactions matter. A relational database can also scale; it is not inherently a small-system choice.

### When can non-relational storage be useful?

Document, key-value, or wide-column storage can fit simple known access patterns, flexible schemas, specialized workloads, or designs where horizontal partitioning is central.

### What is an index?

An index is an additional data structure that speeds selected reads. It consumes storage and makes writes more expensive, so indexes should follow real query patterns.

### What is replication?

Replication maintains copies of data for redundancy, locality, or read capacity. Replicas can lag behind the primary, so copied data may be stale.

### What is a read replica?

A read replica serves reads from a replicated copy instead of the primary. It can reduce primary read load, but replication lag may violate immediate read-after-write expectations.

### What is partitioning or sharding?

Partitioning, or sharding, divides data across nodes, usually by a key. A poor partition key can create hot partitions, uneven storage, and expensive cross-partition operations.

### What is a transaction?

A transaction groups operations under defined atomicity and isolation guarantees. It is used to protect invariants that must change together.

### What is durability?

Durability asks whether acknowledged data survives failures such as process, node, or regional loss. The guarantee depends on logging, replica acknowledgements, and the failure model.

### What is strong consistency?

Strong consistency is an umbrella term for guarantees that prevent clients from observing arbitrarily stale state. When precision matters, name the exact guarantee, such as linearizable reads, read-after-write, or session-level consistency.

### What is eventual consistency?

Eventual consistency allows replicas to temporarily differ but requires them to converge when updates stop and delivery succeeds. It does not mean random or undefined data.

### What is read-after-write consistency?

Read-after-write consistency means a client can observe its completed write in subsequent reads according to the stated scope. This is often important for user-visible updates such as profile changes.

### What does CAP theorem actually say?

**CAP** stands for Consistency, Availability, and Partition tolerance. During a network partition, an affected operation must trade consistency against availability; CAP is not a generic rule to “choose any two” for the whole system.

## Caching & Data Freshness

### What is a cache?

A cache stores a reusable copy of data closer to the consumer or in a faster medium. It reduces latency or source load, but creates freshness, invalidation, eviction, and failure questions.

### What is a cache hit?

A cache hit happens when the requested value is found and can be served from the cache. A cache miss falls through to the underlying source of truth.

### What is cache-aside?

In cache-aside, the application explicitly checks the cache and loads the source of truth on a miss.

```text
Client -> Service -> Cache
                    | miss
                    v
                 Database
                    |
                    +-> populate cache
```

### What is TTL?

**TTL (Time To Live)** limits how long a cached entry may be reused. Shorter TTLs usually improve freshness but increase cache misses and source load.

### What is cache invalidation?

Cache invalidation removes or expires cached data when the authoritative value changes. The difficult part is handling races, failed invalidations, and multiple related keys.

### What is eviction?

Eviction removes entries because they expire or the cache reaches a resource limit. Eviction policy affects hit rate, memory usage, and which data stays hot.

### What is cache warming?

Cache warming preloads likely-needed entries before demand arrives. It can reduce cold-start misses, but broad warming can waste resources or overload dependencies.

### What is stale-while-revalidate?

Stale-while-revalidate serves a bounded stale value immediately and refreshes it in the background. It trades some freshness for lower latency and better availability.

### What is negative caching?

Negative caching stores a known negative result, such as “resource not found,” for a short period. Transient network, server, or authorization failures should not be cached blindly because that can hide recovery.

### What is a cache stampede?

A cache stampede, or thundering herd, happens when many callers reload the same popular value at once after expiration. Request coalescing, jittered TTLs, bounded stale serving, or controlled warming can reduce it.

### What can happen when a cache fails?

If a cache becomes unavailable, traffic may suddenly fall through to the database or another source. Capacity planning must include this degraded mode.

### What is a client-side cache?

A client-side cache keeps data on the device to reduce latency and network usage and can support offline behavior. It is still a replicated view and needs explicit refresh, staleness, storage, and cleanup rules.

### What does freshness mean for mobile UI?

Freshness is a product contract, not just a timestamp. The UI may need to show when data is stale, when local writes are pending, and when the latest server state is not yet known.

## Async Processing & Messaging

### What is asynchronous processing?

Asynchronous processing separates acceptance from completion. The system records intent, returns a pending or accepted state, and performs the work later.

### Why move work out of the request-response path?

Slow or expensive work can exceed request budgets and consume server resources. Moving it to background workers can improve responsiveness and absorb bursts.

### What is a queue?

A queue buffers work between producers and consumers. It helps control concurrency and lets workers process jobs at a rate downstream systems can sustain.

### What is a producer?

A producer creates and submits a message or job to a queue or broker. It should define the payload contract and what durable acceptance means.

### What is a consumer or worker?

A consumer or worker receives queued work and performs the processing. It must handle retries, duplicates, failures, and observability according to the delivery model.

### What is pub/sub?

Publish/subscribe lets a producer publish an event without selecting one specific consumer. Independent subscribers can react to the same event, enabling fan-out.

### What is fan-out?

Fan-out means one event causes work in multiple independent consumers, for example analytics, notifications, and indexing reacting to the same domain event.

### What is at-most-once delivery?

At-most-once delivery avoids broker-driven redelivery but may lose work if a message or acknowledgement fails.

### What is at-least-once delivery?

At-least-once delivery retries messages, so consumers must expect duplicates. Idempotency or deduplication is usually required for side effects.

### What does exactly-once mean?

Exactly-once is meaningful only within a precisely defined boundary and set of guarantees. End-to-end business side effects often still require idempotency or deduplication.

### What is a DLQ?

**DLQ (Dead-Letter Queue)** isolates messages that repeatedly fail. It is not a solution by itself; teams still need alerts, diagnosis, retention, correction, and safe replay procedures.

### Why does ordering need a scope?

Global ordering is expensive and often unnecessary. Ordering per account, conversation, entity, or partition may be enough and should be stated explicitly.

### How should a mobile client track asynchronous work?

The server should return a stable operation or job ID. A mobile process may disappear after receiving `pending`, so the client must be able to recover status later through refresh, polling, realtime updates, or push-triggered reconciliation.

## Reliability & Failure Handling

### What is a partial failure?

A partial failure means one dependency, request, region, or component fails while the rest of the system continues. Distributed systems must define behavior for these mixed states.

### What does a timeout mean?

A timeout means the caller stopped waiting. It does not prove that the remote operation failed; the server may have completed it after the caller gave up.

### Why can retries be dangerous?

Retries multiply load and may repeat side effects. If the first request succeeded but its response was lost, a blind retry can apply the operation twice.

### What is exponential backoff?

Exponential backoff increases the delay between retry attempts. It reduces pressure on an unhealthy dependency compared with rapid fixed retries.

### What is jitter?

Jitter adds randomness to retry delays so many clients do not retry at the same instant. This helps avoid synchronized retry storms.

### What is a retry budget?

A retry budget limits how much additional retry traffic a system is willing to create. It prevents recovery logic from becoming a second source of overload.

### What is retry ownership?

Retry ownership defines which layer is responsible for retrying one logical operation. UI callbacks, HTTP clients, repositories, gateways, services, and background workers should not independently multiply the same retry.

### What is idempotency?

An idempotent operation can be repeated without applying the same business effect multiple times. Idempotency is especially important when the outcome of a previous request is uncertain.

### What is an idempotency key?

An idempotency key identifies one logical mutation across repeated requests. The service must persist the key and result within a defined scope and retention period; the header alone does not create idempotency.

### What is a circuit breaker?

A circuit breaker temporarily stops calls to a failing dependency after a threshold, waits for a cooldown, and then allows limited probes before normal traffic resumes.

### What is graceful degradation?

Graceful degradation keeps core behavior available when an optional dependency fails. A fallback must remain safe: stale recommendations may be acceptable, stale authorization decisions may not be.

### What are liveness and readiness?

Liveness asks whether a process is alive enough that restarting it may help. Readiness asks whether an instance should currently receive traffic. Dependency health can be observed separately so one shared outage does not automatically remove every upstream instance.

### What is observability?

Observability uses logs, metrics, traces, and domain signals to explain what happened in production. Useful signals include latency percentiles, error rate, saturation, queue age, dependency health, and user-visible outcomes.

## System Design Diagrams

### Why use system design diagrams?

A diagram should answer a specific engineering question. It should expose boundaries, ownership, data flow, ordering, or failure paths without reproducing every implementation detail.

### What is a high-level architecture diagram?

A high-level architecture diagram shows the main system components and their dependencies. It is useful for discussing boundaries, responsibilities, trust zones, and likely bottlenecks.

### What is a component diagram?

A component diagram focuses on major responsibilities and relationships between components. It should stay at one abstraction level instead of mixing classes, cloud resources, tables, and user journeys.

### What is a sequence diagram?

A sequence diagram shows the order of interactions between participants for one scenario. It is especially useful for timeouts, retries, races, acknowledgements, and partial failures.

### Why are failure branches useful in sequence diagrams?

A happy-path sequence can hide uncertainty. Showing a timeout, lost response, retry, or pending state makes it clear when the system knows an operation succeeded and when it does not.

### What is a data-flow diagram?

A data-flow diagram shows where data originates, moves, transforms, and persists. It helps reason about sources of truth, replicas, privacy, retention, and reconciliation.

### What is the C4 model?

The C4 model uses zoom levels: System Context, Container, Component, and Code. For many system discussions, Context and Container views are enough.

### What is a System Context diagram?

A System Context diagram shows users, the system being designed, and external systems. It defines the broadest useful boundary.

### What is a Container diagram in C4?

A Container diagram shows runnable or deployable parts such as a mobile app, API, worker, database, or web app. “Container” here does not necessarily mean Docker.

### When is a state diagram useful?

A state diagram is useful when correctness depends on explicit states and transitions, for example payment, upload, or synchronization workflows.

### When is a class diagram less useful?

A class diagram is less useful when the question is system capacity, network flow, service boundaries, or failure behavior. Use the diagram type that answers the actual question.

### What should arrows on a diagram mean?

Arrows should make direction and semantics clear. Label them when needed with actions, protocols, events, mutations, acknowledgements, or async boundaries.

### What makes a diagram good?

A good diagram has a clear scope, consistent abstraction level, meaningful names, visible durable state and boundaries, and enough explanation to support a decision. Outdated diagrams should be updated or removed.

## Offline-First Mobile Application

### What does offline-first mean?

An offline-first application remains useful with intermittent connectivity. Users can read previously loaded data, make local changes, and synchronize later without silently losing work.

### Why can the local database be the UI source of truth?

Using one observable local source prevents the UI from switching between unrelated network and database states. Network synchronization updates the local store, and the UI keeps observing the same model.

### Does local source of truth mean the server is not authoritative?

No. The local database can be the source of truth for presentation while the backend remains authoritative for shared domain state, authorization, and cross-device coordination.

### What is a pending mutation?

A pending mutation is a durable record of a local change that has not yet been confirmed by the server. It allows the app to recover synchronization after process death or connectivity loss.

### Why does a mutation need a stable operation ID?

A stable operation ID lets the server recognize retries of the same logical change. It is essential when the client cannot know whether an earlier request completed.

### Why should pending mutations be persisted?

An in-memory queue disappears when the process dies. Persisting the visible change and its mutation together prevents local state from being updated without preserving the work required to synchronize it.

### What is an optimistic update?

An optimistic update changes local UI immediately before server confirmation. It improves responsiveness but requires pending/failed state and a recovery path if the server rejects the change.

### What happens if the app dies while a mutation is in flight?

`in_flight` should represent an attempt, not permanent truth. After restart, timeout, or an expired lease, unfinished work must become retryable or be reconciled using the same stable operation ID.

### How should retries work in offline sync?

Keep failed transient mutations durable and retry later with bounded attempts, backoff, and jitter. Permanent validation or authorization errors should not retry forever.

### Why are connectivity callbacks not proof of backend reachability?

A device can have a network route while DNS, TLS, the API, authentication, or a dependency is still unavailable. Connectivity changes can trigger an attempt, but the request result remains authoritative.

### What is a conflict in offline-first sync?

A conflict happens when local and server versions change independently. The correct resolution depends on domain semantics rather than one universal policy.

### What conflict strategies are common?

Common strategies include server-wins, client-wins, last-write-wins, field-level merge, and domain-specific resolution. Each trades simplicity against risk of losing user or remote intent.

### What is a tombstone?

A tombstone records that an entity was deleted without immediately erasing all evidence of the deletion. It allows the delete to synchronize across server and replicas before cleanup.
