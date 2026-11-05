# KMP Adoption and Trade-offs

KMP is an architectural investment. Its value comes from sharing meaningful behavior while retaining necessary platform integration.

## Good-fit signals

KMP is worth evaluating when:

- business behavior must remain consistent across platforms;
- substantial data, domain, synchronization, or offline-first logic exists;
- teams can collaborate around Kotlin and native integration;
- platform products have compatible requirements;
- shared ownership, code review, tests, and CI can be established;
- a stable responsibility can be extracted incrementally.

The [sharing boundary](shared-platform-code.md) may be a small core, data and domain, presentation, UI, or a hybrid.

## Costs and risks

Adoption adds build configuration and CI complexity, a larger target test matrix, and library compatibility checks. Kotlin/Swift interoperability can make exported APIs, coroutines, errors, generics, and debugging across language boundaries less direct. Platform APIs, lifecycle, and native toolchains remain necessary; building and validating an iOS app requires macOS and Xcode.

Teams also need clear ownership of shared modules, platform adapters, reviews, releases, and upgrades. A shared module without shared responsibility can become a delivery bottleneck.

[Source-set design](project-structure.md) controls dependency availability but does not remove these integration costs. A shared [ViewModel or UI](architecture-ui.md) still needs platform lifecycle, navigation, accessibility, and system behavior.

## Incremental adoption

1. Choose one stable, testable responsibility and record the current duplication, defects, and delivery effort.
2. Extract a small shared module with explicit platform adapters.
3. Add common tests and build and integration checks for every required target in CI.
4. Pilot the module in both platform apps; check Swift-facing APIs and debugging effort in practice.
5. Compare the outcome with the baseline, including build time, integration work, and team ownership.
6. Expand, retain the limited scope, or roll back according to the result.

An isolated repository, validation rules, or synchronization policy can be a useful pilot. Share behavior with enough complexity to test the proposition; sharing only simple models may show too little value.

## When KMP may not pay off

KMP may be unjustified when little behavior can be shared, the platforms intentionally implement different products, or the application is too small or short-lived to recover setup cost. It is also risky when the team cannot own Kotlin and native integration, a critical dependency lacks required targets, or organizational boundaries prevent shared ownership.

## Decision checklist

- What stable behavior will be shared, and how much duplication does it remove?
- Which targets and libraries must be supported?
- Where will the platform boundary sit, including Swift-facing APIs?
- Who owns shared code and each adapter?
- How will every target be built, tested, and released?
- What baseline and pilot outcome will show fewer inconsistencies or lower delivery effort after integration cost?
- Can the pilot be kept small or rolled back if it does not pay off?

Choose KMP when measured product and maintenance value justifies technical and organizational cost. Shared-code percentage alone is a poor success metric.

## References

- [Kotlin Multiplatform documentation](https://kotlinlang.org/docs/multiplatform/)
- [Kotlin Multiplatform quickstart](https://kotlinlang.org/docs/multiplatform/quickstart.html)
- [Android KMP guidance](https://developer.android.com/kotlin/multiplatform)
