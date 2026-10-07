# Data Storage & Consistency

Storage selection starts with data ownership, access patterns, and guarantees. “SQL versus NoSQL” is not an ideology: each option trades query flexibility, transactions, consistency, scalability, operational complexity, and cost differently.

## Source of truth and access patterns

Choose the primary source of truth before adding replicas, indexes, or caches. Define which component accepts authoritative writes, what must be durable before success is returned, and which reads may observe a copy.

Relational storage is often attractive when:

- relationships and structured queries matter;
- multi-record transactions matter;
- constraints must protect invariants;
- the schema and query model benefit from SQL.

Document, key-value, or wide-column storage may be attractive when:

- access patterns are simple and known;
- horizontal partitioning is central to the workload;
- schema flexibility is useful;
- a specialized workload or very large scale justifies the trade-offs.

Relational databases can scale, and non-relational databases can still have consistency and operational limits. Evaluate a concrete engine and workload rather than relying on category slogans.

## Indexes, replication, and partitioning

An index speeds selected reads by maintaining an additional structure. It consumes storage and makes writes more expensive, so indexes should follow actual query patterns.

Replication maintains copies for redundancy, locality, or read capacity. A read replica can reduce primary read load, but replication lag means it may not immediately reflect a write. Partitioning or sharding divides data across nodes, commonly by a key. A poor key can produce hot partitions, uneven storage, and expensive cross-partition queries. Rebalancing and routing become part of the design.

Schema evolution must support data written by older software and, during rolling deployment, code of different versions. Favor backward-compatible transitions when possible: add, migrate, switch reads, then remove obsolete fields.

## Transactions, consistency, and durability

A transaction groups operations under defined atomicity and isolation guarantees. Use it to protect invariants that must change together, while recognizing that broad distributed transactions can reduce availability and throughput.

**Strong consistency** is an umbrella term in informal system-design discussion: it generally means clients do not observe arbitrarily stale state, but the exact guarantee should be stated when it matters, for example linearizable reads, read-after-write consistency, or session-level guarantees. **Eventual consistency** means replicas can temporarily differ but converge when updates stop and delivery succeeds. It is not random data: the allowed observations and convergence rules still need a contract.

Read-after-write consistency is often a user-facing requirement. After a profile update, the same user usually expects an immediate read to show the new value. Analytics counters may tolerate delayed convergence. Different operations in one system can make different consistency choices.

Durability asks whether acknowledged data survives process, node, or regional failures. The answer depends on when logs are flushed, how many replicas confirm a write, and which failures the design covers.

## CAP theorem in context

CAP refers to **Consistency, Availability, and Partition tolerance**. It is misleading to say that a system simply “chooses any two.” When a network partition prevents nodes from communicating, the system must decide, for an affected operation, whether to reject or delay work to preserve its consistency guarantee, or serve work with a risk of divergent state to preserve availability.

Partitions are not a normal tuning knob, and consistency is not one universal setting. Choices may differ by operation: an account balance, a profile view, and an analytics counter can require different behavior. State the failure scenario and the guarantee instead of labeling an entire system only “CP” or “AP.”

## See also

- [System Design Fundamentals](fundamentals.md)
- [Scalability & Capacity](scalability-capacity.md)
- [Caching & Data Freshness](caching.md)
- [Offline-First Mobile Application](offline-first-mobile.md)
- [Android Storage](../../android/storage.md)
