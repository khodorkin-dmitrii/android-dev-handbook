# GraphQL

GraphQL lets the client describe the required data shape through a query instead of choosing a fixed REST endpoint with a predefined response.

## GraphQL Basics

### What is GraphQL?

GraphQL is a query language and runtime for APIs where the client describes which data fields it needs, and the server returns a response with the same shape.

In Android, GraphQL is usually used through a client library such as Apollo Kotlin: the backend schema generates typed models and operations for queries/mutations/subscriptions.

Benefit: it can reduce overfetching and underfetching because the screen requests only the fields it needs. Trade-off: caching, error handling, schema versioning and observability are more complex than in simple REST.

**In short:** GraphQL lets the client request exactly the data shape it needs, usually through typed generated operations.

### Query / Mutation / Subscription

Query is used to read data, mutation changes data or starts a server-side action, and subscription provides realtime updates through a persistent connection.

In Android, queries usually look like one-shot fetch or observable cached data, mutations like a suspend operation with a result, and subscriptions like a stream of updates.

**Important:** mutation does not have to be idempotent, so retry should be done carefully, just like with `POST` in REST.

**In short:** query reads data, mutation changes data, subscription streams updates.

### GraphQL schema and typed models

GraphQL schema describes types, fields, arguments and operations available to the client. On Android, client tools can generate Kotlin models and type-safe API from the schema and `.graphql` files.

This reduces the risk of runtime errors caused by incorrect field names or types, but requires schema synchronization between backend and mobile project.

Do not expose generated network models directly to UI. It is better to map them into domain/UI models, especially when the schema is complex or unstable.

**In short:** schema is the API contract; generated models make GraphQL calls type-safe on Android.

### GraphQL vs REST

REST is usually built around resources and different endpoints: `/users`, `/orders`, `/products`. GraphQL usually has one endpoint, and the data shape is defined by the query.

REST is easier to understand, cache at HTTP level and debug with standard tools. GraphQL is more flexible for complex screens that need to collect data from several related entities without several round trips.

In GraphQL, errors can be partial: a response can contain both data and errors. Therefore the client should handle partial data, nullability and backend error extensions.

**In short:** REST exposes resources through endpoints, GraphQL exposes a schema and lets the client choose the response shape.

### Apollo Kotlin

Apollo Kotlin is a popular GraphQL client for Android/Kotlin. It generates Kotlin code from GraphQL schema and operations, executes queries/mutations/subscriptions and supports normalized cache.

Apollo client usually lives in the data layer, while repository calls generated operations and maps responses into domain/UI models.

Pitfalls: track schema nullability, partial errors, cache policy, schema updates, and make sure generated models do not leak into `ViewModel` / UI.

**In short:** Apollo Kotlin is a type-safe GraphQL client; repositories should hide generated API details from UI.
