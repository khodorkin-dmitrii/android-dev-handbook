## Computer Science

### Name the principles of OOP

Encapsulation, inheritance, polymorphism, and abstraction. They help separate responsibilities, hide implementation details, and work with objects through common contracts.

**Encapsulation** means hiding internal state and implementation details behind a public API. For example, a field can be `private`, while access to it is controlled through methods or properties.

**Polymorphism** allows us to work with different implementations through a common type. For example, a `ViewModel` can depend on a `Repository` interface, while a concrete implementation is provided through DI.

**Inheritance** allows a new class to be created from an existing one and reuse its behavior. Deep inheritance hierarchies increase coupling, so composition is often preferred in application code.

**Abstraction** keeps the important properties and behavior visible while hiding unnecessary implementation details. In Kotlin and Java, it is usually expressed through interfaces, abstract classes, and public contracts.

### What are mutability and immutability?

A mutable object can be changed after creation, while an immutable object cannot. Immutability makes state management, concurrency, and declarative UI easier to reason about.

### What is SOLID?

SOLID is a set of five object-oriented design principles: SRP, OCP, LSP, ISP, and DIP. Their goal is to reduce coupling and make code easier to extend, test, and maintain.

**Single Responsibility Principle** means that a class should have one main responsibility and one reason to change. For example, a `ViewModel` should not handle networking, database access, formatting, and navigation at the same time.

**Open/Closed Principle** means that software entities should be open for extension but closed for constant modification. New behavior is better added through composition, strategies, and new implementations rather than growing `if` or `when` blocks.

**Liskov Substitution Principle** means that a subtype must be able to replace its base type without breaking its contract or expected behavior.

**Interface Segregation Principle** means that several small, focused interfaces are usually better than one large interface. A client should not depend on methods it does not use.

**Dependency Inversion Principle** means that high-level logic should not depend directly on low-level details. Both should depend on abstractions, for example a `ViewModel` depending on a `Repository` interface.

### What practices exist besides SOLID?

Examples include DRY, KISS, YAGNI, separation of concerns, composition over inheritance, immutability, dependency injection, code review, and automated testing. These are guidelines rather than absolute rules, and they should be applied based on context to reduce complexity and the cost of change.

### What is a code smell?

A code smell is a sign of a possible design problem, not necessarily a bug. Examples include a very large class, a long method, duplicated code, too many parameters, and strong coupling.

### What are the main rules for designing a code API?

An API should be minimal, clear, consistent, and difficult to misuse. It should hide implementation details, use clear names and types, preserve backward compatibility, and avoid exposing mutable state without a good reason.

### What is Big O?

Big O describes how an algorithm's execution time or memory usage grows as the input size increases. It is a scalability estimate, not an exact time in milliseconds.

### What is the complexity of binary search?

Binary search works in `O(log n)` because it removes half of the remaining search range on every step. It can only be used with sorted data.

### What is the average complexity of QuickSort?

On average, QuickSort works in `O(n log n)`, while the worst case is `O(n²)`. In practice, good implementations use safer pivot selection and hybrid approaches.

### ArrayList or LinkedList?

`ArrayList` provides `O(1)` indexed access and usually performs better in practice because of cache locality. `LinkedList` is useful less often: indexed lookup is `O(n)`, and fast insertion only helps when the target node is already known.

### What must be overridden when a class is used as a HashMap key?

`equals()` and `hashCode()` must be implemented correctly. If two objects are equal according to `equals()`, they must return the same hash code.

### What data structures do you know?

Common data structures include arrays, dynamic arrays, linked lists, stacks, queues, deques, hash tables, sets, trees, heaps, tries, and graphs. In an interview, it is important not only to list them but also to understand their use cases and the complexity of key operations.

### What is the worst-case insertion complexity in a binary search tree?

In an unbalanced binary search tree, insertion can degrade to `O(n)` if the tree becomes similar to a linked list. In a balanced tree, such as an AVL or red-black tree, insertion is `O(log n)`.

### What is the lookup complexity in a HashMap?

Average lookup is `O(1)` when hash codes are distributed well. In the worst case, many collisions can degrade it to `O(n)`, while modern Java implementations may use a treeified bucket and provide `O(log n)` lookup there.

### What happens if several threads modify a regular HashMap at the same time?

`HashMap` is not thread-safe: this can cause lost updates, visibility problems, and an inconsistent internal state. The solution is to confine access to one thread, protect operations with the same lock, or use a concurrent collection.

### How does ConcurrentHashMap work?

`ConcurrentHashMap` provides thread-safe access without one global lock for the whole map. Reads are mostly non-blocking, while updates use atomic operations and local synchronization for individual buckets; compound operations should use methods such as `putIfAbsent()`, `compute()`, or `merge()`.

### What are stack and heap?

The stack stores call frames, local variables, and references, while the heap stores objects. Each thread has its own stack, while the heap is shared and managed by the Garbage Collector.

### What is a memory leak?

A memory leak happens when an object is no longer needed but is still reachable through a chain of references, so the GC cannot remove it. Common Android causes include references to an `Activity`, listeners, callbacks, and long-lived singleton objects.

## Kotlin

### What is the difference between `val` and `var`?

A `val` reference cannot be reassigned after initialization, while a `var` can. However, `val` does not make the referenced object immutable: the contents of a mutable collection can still be changed.

### What are nullable types?

In Kotlin, nullability is part of the type system: `String` cannot be `null`, while `String?` can. This reduces the risk of `NullPointerException` and requires missing values to be handled explicitly.

### What is the difference between `==` and `===`?

`==` checks structural equality and calls `equals()`. `===` checks referential equality, meaning whether both references point to the same object.

### What is the difference between `as` and `as?`?

`as` performs a regular cast and throws `ClassCastException` when the type is incompatible. `as?` returns `null` instead of throwing an exception.

### What is a `data class`?

A `data class` is intended to hold data. Kotlin automatically generates `equals()`, `hashCode()`, `toString()`, `copy()`, and `componentN()` functions for properties from the primary constructor.

### What is the difference between a `sealed class` and an `enum class`?

An `enum class` represents a fixed set of constants of the same type. A `sealed class` or `sealed interface` represents a restricted hierarchy where each variant can hold its own data.

### What is the difference between `object` and `companion object`?

`object` declares a singleton. A `companion object` is an object associated with a class and is used for static-like members, factory methods, and constants.

### What does `emptyList()` return?

`emptyList()` returns an empty read-only `List<T>`. Elements cannot be added to it; use `mutableListOf()` when a mutable list is required.

### What is the difference between `List` and `MutableList`?

`List` exposes read-only operations, while `MutableList` allows changes. However, `List` does not guarantee true immutability of the underlying object; it only restricts the available API.

### What is an extension function?

An extension function adds convenient method-like syntax to an existing type without inheritance or changing the original class. Under the hood, it is a regular function and cannot access private members of the class.

### What is a higher-order function?

A higher-order function takes another function as a parameter or returns a function. Kotlin uses them heavily in collections, Flow, and DSLs.

### What is `inline` used for?

`inline` allows the compiler to insert the function body and lambda code directly at the call site, reducing the overhead of lambda objects. It is especially useful for small higher-order functions and `reified` generics.

### What is `reified` used for?

`reified` keeps generic type information available inside an `inline` function. This makes operations such as `T::class` and `is T` possible without passing a `Class` or `KClass` explicitly.

### Is Kotlin `Int` a primitive or an object?

At the language level, it is a regular Kotlin type. On the JVM, it is usually compiled to primitive `int`, while nullable and generic contexts require boxing into `Integer`.

### Which Kotlin type has no instances?

`Nothing` has no possible values and cannot be instantiated. It is used as the return type of functions that never complete normally, for example functions that always throw an exception.

### What does a sealed class become in JVM bytecode?

It becomes a base JVM class or interface plus separate subclasses. The Kotlin compiler enforces the hierarchy restrictions and exhaustive checks; modern JVM targets may also include sealed-type metadata.

## Android basics

### Name the four main Android application components

`Activity`, `Service`, `BroadcastReceiver`, and `ContentProvider`. They are declared in the manifest and can serve as application entry points.

### Which is initialized first: Application or ContentProvider?

The `Application` object is created first, then `ContentProvider` instances are initialized, and only after that `Application.onCreate()` is called. This is why libraries often use providers for early auto-initialization.

### What is the difference between an explicit and an implicit Intent?

An explicit Intent names the exact component to start. An implicit Intent describes an action, and Android selects a matching application or component through intent filters.

### What is a `Bundle`?

A `Bundle` is a container for passing small sets of mixed data between Android components and for saving state. It supports primitive types, `Parcelable`, `Serializable`, and several other supported types.

### What is the difference between `Parcelable` and `Serializable`?

`Parcelable` is optimized for Android IPC and is usually faster, but it requires a special implementation or `@Parcelize`. `Serializable` is simpler, but it uses reflection and has more overhead.

### What happens when the device rotates?

Rotation is a configuration change, and by default the current `Activity` is destroyed and recreated. A `ViewModel` survives this recreation, while small UI state can be preserved with `SavedStateHandle` or `onSaveInstanceState()`.

### Can `onDestroy()` be skipped?

Yes. The system may terminate the process without calling `onDestroy()`, so critical data must not rely on this callback being called.

### How does ViewModel survive device rotation?

A `ViewModel` is stored in a `ViewModelStore` associated with the logical screen owner rather than a specific `Activity` instance. After recreation, the new `Activity` receives the same `ViewModel` as long as the process has not been killed.

### How many Loopers can one thread have?

A thread can have at most one `Looper`, and it may have none. The main thread receives one automatically, while a background thread can use `Looper.prepare()` or `HandlerThread`.

### Which Activity lifecycle methods are called during device rotation?

With a normal configuration change, the old `Activity` goes through `onPause()` → `onStop()` → `onDestroy()`, and the new one goes through `onCreate()` → `onStart()` → `onResume()`. `onSaveInstanceState()` is also usually called before destruction.

### What is the difference between `invalidate()` and `requestLayout()`?

`invalidate()` requests a redraw and causes a new draw pass. `requestLayout()` starts a new measure and layout pass when size or positioning has changed.

### Which methods are overridden in a custom ViewGroup?

The main methods are `onMeasure()` for calculating sizes and `onLayout()` for positioning child views. `onDraw()` is needed only when the container draws its own content.

### How does RecyclerView work?

`RecyclerView` coordinates a `LayoutManager`, `Recycler`, `Adapter`, and `ViewHolder`. The `LayoutManager` decides which item positions are needed and where their views should be placed. It requests views through the `Recycler`, which reuses an existing `ViewHolder` when possible or asks the `Adapter` to create and bind one: `RecyclerView -> LayoutManager -> Recycler -> Adapter -> ViewHolder`.

### What is the difference between ViewBinding and DataBinding?

ViewBinding provides type-safe access to views with very little runtime complexity. DataBinding additionally supports expressions in XML, two-way binding, and BindingAdapters, but it makes builds more complex.

### Activity Context or Application Context?

Activity Context is required for UI, themes, dialogs, and operations tied to a screen lifecycle. Application Context lives as long as the process and is suitable for long-lived dependencies, but not for UI.

### What is an ANR?

ANR happens when the main thread does not respond to system or user events for too long. Common causes are blocking operations, heavy computations, and incorrect synchronization on the main thread.

### What is jank?

Jank is visible stutter caused by a frame missing its deadline. At 60 FPS, the budget for one frame is about 16.6 ms.

### What is overdraw?

Overdraw happens when the same pixels are drawn multiple times on top of each other. It is not always a problem, but unnecessary backgrounds and layers can create extra GPU work.

## Jetpack Compose

### What is Jetpack Compose?

Jetpack Compose is a declarative UI toolkit for Android. UI is described as a function of state, and Compose updates the affected parts when that state changes.

### Which basic Compose containers are used to arrange elements?

`Row` arranges elements horizontally, `Column` vertically, and `Box` allows elements to overlap. For large scrollable collections, Compose provides `LazyColumn`, `LazyRow`, and lazy grids.

### Which stability annotations exist in Compose?

The main annotations are `@Immutable` and `@Stable`. They are contracts with the Compose compiler: `@Immutable` promises immutable public state, while `@Stable` promises predictable and observable property changes.

### Are lambdas without captured variables stable in Compose?

Usually, a non-capturing lambda is reused and treated as a stable value. A lambda that captures mutable data or is recreated can change identity and prevent recomposition from being skipped.

### What are the rendering phases in Compose?

The main phases are composition, layout, and drawing. Composition defines the UI structure, layout measures and positions elements, and drawing renders their content.

### Which structure stores the Compose composition tree and state?

Internally, Compose uses the Slot Table. The Composer stores composition groups, `remember` values, and data required for future recompositions there.

### What is recomposition?

Recomposition is the repeated execution of composable functions that depend on changed state. It is a normal Compose mechanism; it becomes a problem only when it is too frequent or expensive.

### What is the difference between `remember` and `rememberSaveable`?

`remember` keeps a value across recompositions but does not survive recreation. `rememberSaveable` also stores supported state through the saved state mechanism.

### What is `mutableStateOf`?

`mutableStateOf` creates observable state tracked by Compose. When its value changes, dependent composable functions may be scheduled for recomposition.

### What is state hoisting?

State hoisting means moving state higher in the composable tree. A component receives a value and callbacks, which makes it more stateless, reusable, and testable.

### When should `LaunchedEffect` be used?

`LaunchedEffect` is used for coroutine side effects tied to the lifecycle of a composable and its key. When the key changes, the previous coroutine is cancelled and a new one starts.

### When should `rememberCoroutineScope` be used?

It is used to launch a coroutine in response to a UI event, such as a button click. Screen-level business logic is usually better placed in a `ViewModel`.

### How can unnecessary recompositions be reduced?

Organize state correctly, avoid passing unstable objects without a reason, use stable keys, and move heavy work out of composables. Optimization should start with measurement and finding a real bottleneck.

## Coroutines and Flow

### How do you use coroutines and Flow in an Android application?

I use coroutines for one-shot asynchronous work such as network requests, database operations, and parallel loading. I use Flow for streams of updates such as UI state, Room observation, search, real-time data, and combining several sources.

### What is a coroutine, and how is it different from a Thread?

A coroutine is a lightweight task that runs on top of threads and can suspend without blocking them. One thread can serve many coroutines over time.

### What does `suspend` mean?

`suspend` means that a function may pause and continue later without blocking the thread. It does not automatically move the work to a background thread.

### What is the difference between `launch` and `async`?

`launch` returns a `Job` and is used when no separate result is needed. `async` returns `Deferred<T>`, and its result is received with `await()`.

### What is structured concurrency?

Structured concurrency ties coroutines to a specific scope and lifecycle. A parent waits for its children and can cancel them as one group.

### What is the difference between `coroutineScope` and `supervisorScope`?

In `coroutineScope`, a failure in one child usually cancels the other children. In `supervisorScope`, child tasks are isolated and can handle failures independently.

### How does cancellation work?

Cancellation is cooperative: a coroutine reacts at suspension points or when it explicitly checks `isActive`. `CancellationException` normally should not be handled as a regular error.

### What are the main Dispatchers?

`Dispatchers.Main` is used for UI work, `IO` for blocking I/O, and `Default` for CPU-intensive work. `withContext()` changes the context inside a suspend function.

### Which synchronization tools are used with Kotlin Coroutines?

Common options are `Mutex` for protecting suspending code, atomic operations for simple shared state, and state confinement where one coroutine owns the state. `synchronized` is also possible, but suspend functions must not be called inside it.

### What is Flow?

Flow is an asynchronous stream of values from the coroutines ecosystem. A regular `Flow` is cold: every collector starts the upstream again.

### How is `Channel` different from `Flow`?

A regular `Flow` is usually a cold declarative stream started by each collector. `Channel` is a hot point-to-point communication primitive: it exists independently of receivers, and each sent element is consumed by only one of them.

### What is the difference between Flow and a suspend function?

A suspend function usually returns one result. Flow can emit many values over time and is suitable for observing changes.

### What is the difference between cold and hot Flow?

A cold Flow starts separately for every collector. A hot Flow exists independently of collectors; `StateFlow` and `SharedFlow` are hot flows.

### What is the difference between `collect` and `collectLatest`?

`collect` processes every value to completion. `collectLatest` cancels the previous processing when a new value arrives.

### When should `flatMapLatest` be used?

Use it when a new input value should switch to a new inner Flow and cancel the previous one. A common example is search by changing query or observing data for a selected ID.

### What is the difference between `combine` and `zip`?

`combine` emits when any source changes and uses the latest values from the others. `zip` combines values pair by pair and waits for a new item from every source.

### What is StateFlow?

`StateFlow` is a hot flow for holding state. It always has a current `value`, and a new collector immediately receives the latest value.

### What is SharedFlow?

`SharedFlow` is a configurable hot flow for broadcasting values. It is often used for events and effects, with configurable `replay` and buffering.

### StateFlow or SharedFlow?

`StateFlow` is suitable for state that must always have a current value and be available to new collectors. `SharedFlow` is more commonly used for events, signals, and one-off effects.

### What is lifecycle-aware collection?

It means collecting a Flow only while the screen is in an appropriate lifecycle state. In Compose, state is usually collected with `collectAsStateWithLifecycle()`, while the View system commonly uses `repeatOnLifecycle()`.

## Architecture

### What is ViewModel used for?

A `ViewModel` stores and coordinates screen state, survives configuration changes, and separates UI from data orchestration. It should not depend directly on a `View`, `Fragment`, or `Activity`.

### How should UI state be stored?

Usually as `StateFlow<UiState>`, where `UiState` is an immutable data class or a sealed hierarchy. The UI observes the state and renders it.

### How should state and effects be separated?

State describes what the screen currently shows, while effects are one-time actions such as navigation or a snackbar. State is usually stored in `StateFlow`, while effects are delivered through `SharedFlow`, `Channel`, or another explicit model.

### What is a single source of truth?

It is a principle where data or state has one primary owner. Other parts of the system receive it from that owner instead of keeping competing copies.

### Is a domain layer always required?

No. It is useful for complex business logic, reusable use cases, and separating rules from UI and data layers, but it can be unnecessary for simple CRUD flows.

### What is a Repository used for?

A Repository hides concrete data sources and exposes one contract to the UI or domain layer. It can coordinate network, database, cache, and mapping.

### How would you design loading data from an API and saving it to a local database?

A Repository coordinates remote and local data sources: it loads DTOs, maps them to entities, and saves them to Room in a transaction. The UI observes Room through Flow as the single source of truth; refresh policy, stale data, and error behavior must be defined separately.

### MVVM or MVI?

MVVM is usually simpler and works well for most screens. MVI is useful for complex state-driven UI where explicit actions, immutable state, and predictable transitions are important.

### Is a separate framework required for MVI?

No. An MVI-style approach can be implemented with a regular `ViewModel`, `StateFlow`, immutable `UiState`, and sealed actions or effects.

### What is Clean Architecture?

It is an approach that separates UI, business logic, and data access and points dependencies toward more stable abstractions. It should be applied pragmatically rather than adding layers without real value.

### What criteria should be used to split an application into modules?

Modules should be separated by functional responsibility, dependency direction, independent development, and reuse. Typical boundaries are features, design system, networking, storage, and shared contracts; each module should expose a clear public API.

### What is the difference between `api` and `implementation` in Gradle?

`implementation` keeps the dependency internal to the current module and does not add it to the consumers' compile classpath. `api` exposes it transitively, so it is used when types from that dependency appear in the module's public API.

### Why use a multi-module architecture?

It helps separate features, reduce coupling, improve ownership, and speed up incremental builds. However, splitting too early increases Gradle complexity and boilerplate.

### How should legacy code be handled?

First, capture the current behavior, then make small and safe changes. Incremental refactoring is usually safer than a full rewrite because it preserves hidden business rules and reduces risk.

## Dependency Injection

### Why is Dependency Injection needed?

DI passes dependencies into a class from the outside, reducing coupling and making testing easier. It also centralizes object creation and lifecycle management.

### What is the difference between DI and Service Locator?

With DI, dependencies are passed explicitly through a constructor or method. With Service Locator, a class asks a global container for dependencies itself, which makes them less visible.

### What is Hilt?

Hilt is a DI framework built on top of Dagger with ready-made Android lifecycle integration. It simplifies dependency graphs, injection into `Activity`, `Fragment`, and `ViewModel`, and scope management.

### What is the difference between `@Binds` and `@Provides`?

`@Binds` connects an interface to an implementation that can already be created by DI. `@Provides` is used when an object must be created manually, for example Retrofit, Room, or an external SDK.

### What is a scope in DI?

A scope defines how long one instance is reused inside the dependency graph. It should match the real lifecycle of the object rather than defaulting everything to `Singleton`.

### Why should not everything be a singleton?

A singleton increases an object's lifetime, can keep unnecessary state, and makes testing harder. Only truly application-wide stateless services or resources should usually be long-lived.

## Networking

### What is HTTP?

HTTP is an application-layer protocol for exchanging messages between a client and a server. A request contains a method, URL, headers, and sometimes a body, while a response contains a status code, headers, and a body.

### What is REST?

REST stands for Representational State Transfer. It is an architectural style for client-server communication based on resources and standard HTTP operations; REST APIs are usually stateless, and resource representations are commonly transferred as JSON.

### What is the difference between GET and POST?

GET is used to retrieve a resource and normally does not change server state. POST sends data in the request body and often creates a resource or starts an operation.

### What is the difference between 401 and 403?

`401 Unauthorized` usually means that authentication is missing or invalid. `403 Forbidden` means the user is recognized but does not have permission to perform the action.

### How can a network request be made without freezing the UI?

Use a non-blocking suspend API from a coroutine. Retrofit suspend functions do not perform network I/O on the main thread, while a blocking API should be called explicitly with `withContext(Dispatchers.IO)`.

### What is Retrofit?

Retrofit is a type-safe HTTP client for Android and the JVM. It converts an annotated interface into an API implementation and usually works on top of OkHttp.

### What is an OkHttp interceptor?

An interceptor can inspect and modify requests and responses, add headers, log traffic, refresh tokens, or retry requests. Heavy business logic should not be placed there.

### How should network errors be handled?

Technical errors should be mapped to clear domain or UI states such as no internet, unauthorized, validation error, or server error. Raw exceptions or HTTP codes should not be shown to users without context.

### What is GraphQL?

GraphQL is a query language and runtime for APIs where the client specifies exactly which fields it needs. It reduces overfetching but requires careful schema, caching, and error handling.

### What is gRPC?

gRPC is an RPC framework with a strict `.proto` contract and Protocol Buffers binary serialization. It supports unary and streaming calls and is useful for high-performance or real-time scenarios.

## Libraries and Build

### How and where are Android libraries published?

An Android library is built as an AAR and published to a Maven repository such as Maven Central, GitHub Packages, Nexus, or Artifactory. The Gradle `maven-publish` plugin is commonly used to upload the artifact, POM, sources, and optional documentation.

### How should a library be versioned?

Semantic Versioning is often used: `MAJOR` for breaking changes, `MINOR` for backward-compatible features, and `PATCH` for backward-compatible fixes. API dumps and binary compatibility validation are useful for a published API.

## Testing

### What are the main types of tests?

Unit tests check isolated logic, integration tests check several components working together, and UI tests check the interface and user actions on a device or emulator. End-to-end tests cover critical flows through the whole application and real or production-like external systems, so they are used selectively.

### How do you make sure a new feature is correct and reduce bugs?

Clarify acceptance criteria and edge cases, design the state and contracts, cover critical logic with tests, and use code review. Also verify errors, retries, repeated actions, lifecycle behavior, offline scenarios, and a safe rollout strategy.

### How do you go from a feature idea to implementation?

First, clarify the user goal, requirements, and constraints, then design the data flow, UI state, actions, and error handling. After that, choose a sufficient architecture, split the work into testable steps, write code and tests, verify scenarios, complete review, and monitor the result after release.

### What should be tested first?

Start with business logic, mapping, use cases, reducers, and ViewModel state transitions. Priority should be based on risk and value rather than trying to cover everything equally.

### Mocks or fakes?

Fakes often produce clearer and more stable tests because they provide simple working behavior. Mocks are useful when a specific interaction really needs to be verified.

### How should a ViewModel be tested?

Send input actions and verify observable state transitions and effects. Test behavior rather than private methods or implementation details.

### How should coroutines and Flow be tested?

Use `runTest`, test dispatchers, and virtual time. This keeps tests fast and deterministic without `Thread.sleep()`.

### Why are UI tests needed?

UI tests verify critical user flows and integration between components. They are more expensive and fragile than unit tests, so they are usually used selectively.
