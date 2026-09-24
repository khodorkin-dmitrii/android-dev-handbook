# Context & Resources

`Context` provides access to app and Android services. Resources let the system select strings, layouts, and other values for the current configuration.

## Context

### Activity Context vs Application Context

`Context` provides APIs for resources, assets, system services, app files, and starting components. Choose a context whose lifetime and UI configuration match the operation.

An `Activity` context carries the activity's theme and window configuration. Use it when inflating themed views, showing dialogs, or accessing resources for that screen. A Compose UI usually obtains the current context with `LocalContext.current`, but resources should normally be read with `stringResource()` and similar Compose APIs when they need to update with configuration changes.

The application context is tied to the app process rather than a screen. It suits a long-lived database, DataStore, or repository that needs app-level services or files. It does not necessarily have the theme or window-specific configuration required by UI. Pass it only when a dependency needs a context; prefer narrower dependencies where possible.

Holding an `Activity`, `View`, or themed context in a longer-lived singleton can retain the destroyed screen. Use `applicationContext` for genuinely process-scoped work, and avoid caching configuration-dependent strings or drawables in long-lived objects: their values can become stale after a locale, theme, or display change.

### ContextWrapper

`ContextWrapper` delegates `Context` operations to a base context and lets subclasses override selected behavior. `ContextThemeWrapper` adds a theme for UI work; `Activity` inherits from it. A wrapper does not automatically make a short-lived base context safe to retain: its lifetime is still relevant.

When you need resources for a specific configuration, `createConfigurationContext()` provides a context with that configuration. For an app language setting, prefer the platform or AppCompat per-app language APIs over keeping a manually modified global `Resources` object.

## Resources

### Resources / configuration / orientation

Resources include strings, plurals, dimensions, colors, drawables, and layouts. Android selects alternatives using qualifiers such as `values-ru`, `values-night`, and `layout-land`; provide sensible defaults where appropriate. Use `getString()` or `getQuantityString()` in Android code and `stringResource()` or `pluralStringResource()` in Compose UI instead of hard-coding user-facing text.

`Configuration` describes attributes such as locale, screen size, density, orientation, night mode, and font scale. Rotation is one possible configuration change; resizing a window can also change the resources selected. Android often recreates an activity so its UI can use the new configuration. Keep business and screen data in an appropriate state holder, and save restorable UI state with `rememberSaveable`, `SavedStateHandle`, or saved instance state as needed. Persistent storage is for data that must survive app restarts, not routine rotation.

`android:configChanges` makes the activity handle specified changes through `onConfigurationChanged()` instead of the usual recreation path. The app must then update affected views and configuration-dependent resources itself. It does not remove the need to handle recreation from other causes, including process death. See [Android's configuration-change guide](https://developer.android.com/guide/topics/resources/runtime-changes) for the current behavior and [app resources](https://developer.android.com/guide/topics/resources/providing-resources) for qualifier matching.
