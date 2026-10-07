# Legacy & Refactoring

Working with legacy Android code means preserving existing behavior while making changes safer. **Refactoring** changes internal structure without changing observable behavior; **migration** replaces a technology or API and requires checking its semantics as well as behavior.

## Legacy

### Legacy code in an Android project

Legacy code carries existing behavior and constraints that are difficult to change safely: unclear responsibilities, hidden dependencies, missing tests or unsupported libraries. Age alone does not make code legacy; XML layouts and RxJava are not automatically problems.

Typical warning signs include a large `Activity` / `Fragment` mixing rendering, business rules and data access, global mutable state, implicit lifecycle assumptions and tightly coupled dependencies.

Prioritize concrete pain points: recurring bugs, risky changes, poor testability or an unsupported dependency. Leave stable code alone when replacing it has no clear benefit.

**Characterization tests** capture what the current implementation actually does, including surprising edge cases. They protect behavior during restructuring; they do not prove that every existing behavior is correct. Fix discovered bugs separately with an explicit new expectation. A manual checklist can supplement tests but is less reliable for repeated regression checks.

Improve boundaries where useful: move data access behind a repository, keep screen state in a `ViewModel`, and make side effects explicit. Introduce use cases for complex or reused business logic, not as mandatory wrappers around every repository call.

### Incremental refactoring

Incremental refactoring improves one responsibility or boundary at a time through small, verifiable changes.

1. Choose a specific problem and define the expected benefit.
2. Capture normal, error and lifecycle behavior with focused tests.
3. Create a **seam**: a replaceable boundary, such as a constructor-injected dependency or an interface around a legacy API.
4. Extract or replace one piece behind that boundary while keeping callers stable.
5. Verify behavior, migrate callers gradually, then remove the obsolete implementation.

For example, wrap an existing Rx API behind a repository before changing screen state or rendering. An adapter lets new callers use a different contract while old callers continue working.

In Android, check rotation, navigation away/back, process recreation, deep links, offline/error states and duplicate requests or analytics events where relevant. A `ViewModel` survives configuration changes, but process recreation needs appropriate saved state or persistent data.

Keep bug fixes and structural changes separately reviewable. Measure the intended improvement, such as fewer crashes or simpler tests. For a risky feature migration, staged rollout and a temporary feature flag can help restore the old path; irreversible data changes require a separate recovery plan.

## Migration

### Migration from XML/RxJava to Compose/Flow

UI and reactive-stack migrations are independent. Stabilize state and event contracts first, then replace one implementation at a time.

**Views to Compose:**

- Introduce `ComposeView` inside an existing Fragment. Use `ViewCompositionStrategy.DisposeOnViewTreeLifecycleDestroyed` to tie its composition to the Fragment's view lifecycle.
- Reuse a legacy `View` through `AndroidView`; use `AndroidViewBinding` for an existing XML layout accessed through View Binding.
- Keep `ViewModel` + `UiState` independent of rendering. Collect state with `collectAsStateWithLifecycle()` in Compose or `repeatOnLifecycle()` using `viewLifecycleOwner` in a Fragment.
- Check state restoration, focus, accessibility, scrolling and navigation behavior. Changing the UI toolkit does not automatically preserve these.

**RxJava to coroutines/Flow:**

- A one-shot `Single<T>` usually maps to a suspend function returning `T`; `Completable` maps to one returning `Unit`. Use a matching bridge module: `kotlinx-coroutines-rx2` or `kotlinx-coroutines-rx3`.
- Adapt streams at layer boundaries, then check subscription lifetime, cold/hot behavior, buffering/backpressure, errors and execution context. `StateFlow` holds current state and conflates updates; it is not a drop-in replacement for every Rx stream or event channel.
- Lifecycle-aware collection stops and restarts subscriptions. Confirm whether upstream work should restart or remain shared.

Minimal RxJava 3 adapter; `LegacyApi` and `User` are application types:

```kotlin
import kotlinx.coroutines.rx3.await

class UserRepository(private val api: LegacyApi) {
    // LegacyApi.loadUser(id) returns Single<User>.
    suspend fun loadUser(id: String): User = api.loadUser(id).await()
}
```

`await()` suspends without blocking and disposes the subscription when the waiting coroutine is cancelled. Disposal only stops underlying work if the source supports it. The adapter does not move blocking subscription work to a background thread: preserve appropriate Rx scheduling or dispatch blocking work explicitly. Do not swallow coroutine cancellation as a normal error.

## References

- [Android domain layer](https://developer.android.com/topic/architecture/domain-layer)
- [Compose in Views](https://developer.android.com/develop/ui/compose/migrate/interoperability-apis/compose-in-views)
- [RxJava 3 coroutine bridges](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-rx3/)
- [RxJava await](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-rx3/kotlinx.coroutines.rx3/await.html)
