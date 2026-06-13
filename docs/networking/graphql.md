# GraphQL

GraphQL даёт клиенту возможность описывать форму нужных данных через query, а не выбирать фиксированный REST endpoint с заранее заданным response.

## Основы GraphQL

### Что такое GraphQL?

GraphQL - query language и runtime для API, где client сам описывает, какие поля данных ему нужны, а server возвращает response той же формы.

В Android GraphQL чаще используют через client library вроде Apollo Kotlin: схема backend-а генерирует typed models и operations для queries/mutations/subscriptions.

Плюс: можно уменьшить overfetching и underfetching, потому что экран запрашивает только нужные поля. Минус: сложнее caching, error handling, versioning schema и observability, чем в простом REST.

**Коротко:** GraphQL lets the client request exactly the data shape it needs, usually through typed generated operations.

### Query / Mutation / Subscription

Query используется для чтения данных, mutation - для изменения данных или запуска server-side action, subscription - для realtime updates через persistent connection.

В Android queries обычно похожи на one-shot fetch или observable cached data, mutations - на suspend operation с результатом, subscriptions - на stream обновлений.

**Важно:** mutation не обязана быть idempotent, поэтому retry нужно делать осторожно, как и с `POST` в REST.

**Коротко:** query reads data, mutation changes data, subscription streams updates.

### GraphQL schema and typed models

GraphQL schema описывает types, fields, arguments и operations, которые доступны клиенту. На Android client tools могут генерировать Kotlin models и type-safe API по schema и `.graphql` files.

Это снижает риск runtime ошибок из-за неправильных field names или типов, но требует синхронизации schema между backend и mobile project.

Важно не тащить generated network models прямо в UI. Лучше маппить их в domain/UI models, особенно если schema сложная или нестабильная.

**Коротко:** schema is the API contract; generated models make GraphQL calls type-safe on Android.

### GraphQL vs REST

REST обычно строится вокруг resources и разных endpoints: `/users`, `/orders`, `/products`. GraphQL чаще имеет один endpoint, а форма данных задаётся query.

REST проще понимать, кешировать на HTTP-level и дебажить стандартными tools. GraphQL гибче для сложных экранов, где нужно собрать данные из нескольких связанных сущностей без нескольких round trips.

В GraphQL ошибки могут быть частичными: response может содержать и data, и errors. Поэтому client должен уметь обрабатывать partial data, nullability и backend error extensions.

**Коротко:** REST exposes resources through endpoints, GraphQL exposes a schema and lets the client choose the response shape.

### Apollo Kotlin

Apollo Kotlin - популярный GraphQL client для Android/Kotlin. Он генерирует Kotlin-код из GraphQL schema и operations, выполняет queries/mutations/subscriptions и поддерживает normalized cache.

Обычно Apollo client живёт в data layer, а repository вызывает generated operations и маппит response в domain/UI models.

Pitfalls: следить за nullability из schema, partial errors, cache policy, schema updates и тем, чтобы generated models не протекали во `ViewModel` / UI.

**Коротко:** Apollo Kotlin is a type-safe GraphQL client; repositories should hide generated API details from UI.
