# KMP Adoption and Trade-offs

KMP is an architectural investment, not a default requirement. Its value comes from sharing meaningful behavior while retaining necessary platform integration.

## Good-fit signals

KMP is worth evaluating when:

- business behavior must remain consistent across platforms;
- substantial data, domain, synchronization, or offline-first logic exists;
- teams can collaborate around Kotlin and native integration;
- platform products have compatible requirements;
- shared ownership, code review, tests, and CI can be established;
- a stable responsibility can be extracted incrementally.

The appropriate [sharing boundary](shared-platform-code.md) may be a small core, data and domain, presentation, UI, or a hybrid.

## Costs and risks

Adoption adds build configuration and CI complexity, a larger target test matrix, and library compatibility checks. Kotlin/Swift interoperability can make exported APIs, coroutines, errors, generics, and debugging across language boundaries less direct. Platform APIs, lifecycle, and native toolchains remain necessary; Apple builds and final Apple-platform validation require macOS and Xcode.

The organizational cost is equally important. Teams need clear ownership of shared modules, platform adapters, reviews, releases, and upgrade coordination. A shared module without shared responsibility can become a delivery bottleneck.

[Source-set design](project-structure.md) controls dependency availability but does not remove these integration costs. Likewise, a shared [ViewModel or UI](architecture-ui.md) does not remove platform lifecycle, navigation, accessibility, or system behavior.

## Incremental adoption

1. Identify a stable, testable responsibility.
2. Extract a small shared module.
3. Establish explicit platform adapters.
4. Add shared tests and target-aware CI.
5. Measure maintenance cost and integration friction.
6. Expand only when demonstrated value exceeds the new complexity.

A rewrite is rarely the safest default. Networking models, validation, formatting, or an isolated repository are often better experiments than migrating an entire application.

## When KMP may not pay off

KMP may be unjustified when little behavior can be shared, the platforms intentionally implement different products, or the application is too small or short-lived to recover setup cost. It is also risky when the team cannot own Kotlin and native integration, a critical dependency lacks required targets, or organizational boundaries make shared ownership impractical.

## Decision checklist

- What stable behavior will be shared?
- Which targets and libraries must be supported?
- Where will the platform boundary sit?
- Who owns shared code and each adapter?
- How will every target be built, tested, and released?
- What metric will show lower duplication, fewer inconsistencies, or faster delivery?
- Is there an incremental exit path if the experiment does not pay off?

Choose KMP when the expected product and maintenance value exceeds its technical and organizational cost, not to maximize shared-code percentage.

## References

- [Kotlin Multiplatform documentation](https://kotlinlang.org/docs/multiplatform/)
- [Android KMP guidance](https://developer.android.com/kotlin/multiplatform)
