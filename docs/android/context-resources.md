# Context & Resources

`Context` and resources connect app code with the Android runtime: resources, system services, theme, configuration and component launching.

## Context

### Activity Context vs Application Context

`Context` - access to the Android app environment: resources, assets, system services, package info, launching `Activity` / `Service` / Broadcast and so on.

`Activity Context` is tied to the lifecycle of a specific `Activity` and knows about its theme, window and UI state. It is used for UI operations: inflating a themed layout, showing a dialog, starting an activity from a screen and accessing themed resources.

`Application Context` lives as long as the app process. It is used for long-lived objects: repositories, databases, `DataStore`, analytics and the dependency graph, when they do not need the UI/theme of a specific `Activity`.

The main pitfall: do not store `Activity Context` in a singleton/static object/long-lived component, otherwise you can leak the `Activity`. If a long-lived object needs `Context`, `applicationContext` is usually safer.

**In short:** `Activity Context` is UI/lifecycle/themed context, `Application Context` is process-level context; avoid storing `Activity Context` longer than the Activity lifecycle.

### ContextWrapper

`ContextWrapper` - a wrapper class around `Context` that delegates calls to a base `Context`, while allowing part of the behavior to be overridden.

Many Android classes are built around this idea: `ContextThemeWrapper` adds or changes a theme, `Activity` is also a `ContextThemeWrapper`, and `Application` and `Service` inherit from `ContextWrapper`.

`ContextWrapper` is useful when you need to create a `Context` with another theme/configuration or adapt `Context` API behavior without changing the original base context.

In practice, Android developers usually encounter it indirectly: themed inflater, dialog context, localized/configuration context and activity as context.

**In short:** `ContextWrapper` wraps another `Context` and delegates to it, while allowing specific behavior like theme or configuration to be overridden.

## Resources

### Resources / configuration / orientation

Resources - an API for accessing app resources: strings, drawables, colors, dimensions, layouts, plurals and other files from `res/`.

Configuration describes the current device and app configuration: orientation, locale, screen size, density, night mode, font scale and other parameters.

When configuration changes, for example on rotation, language change or dark mode, Android may recreate the `Activity` to apply the appropriate resources from qualifiers again: `layout-land`, `values-night`, `values-ru`, `drawable-xhdpi` and so on.

Orientation is a specific case of configuration. When switching between portrait and landscape, do not keep UI state only in the `View`; use `ViewModel`, `SavedStateHandle` / `onSaveInstanceState()` or persistent storage depending on the type of data.

Some changes can be handled manually through `android:configChanges`, but this shifts responsibility to the app and usually should not be the default solution for every screen.
