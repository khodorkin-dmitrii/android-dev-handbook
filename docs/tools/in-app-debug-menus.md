# In-App Debug Menus

An internal debug menu makes application state inspectable when QA, support, or remote developers cannot attach Android Studio. Keep its actions tied to specific investigation tasks.

## Useful capabilities

A focused menu can expose:

* environment, app version, build variant, and commit SHA;
* feature flags and account or session status without secrets;
* recent logs and request metadata, with sensitive values redacted;
* summaries of local storage or database state;
* cache reset and predefined application states;
* error, offline, empty-state, and sync simulation;
* shortcuts to internal screens;
* device metadata and an explicit diagnostic export, optionally with a screenshot or recording.

Group actions by problem and confirm destructive operations. Label simulated conditions and provide a predictable reset; otherwise a test may start from an unknown state.

```text
Debug UI
   ↓
Debug commands and queries
   ↓
Application services, repositories, feature flags, diagnostics
```

The UI should call explicit commands rather than mutate databases or bypass application services directly.

## Implementation approaches

### Custom debug menu

A custom screen gives full control over Compose UI, navigation, access checks, and redaction. It suits project-specific operations backed by stable app-owned interfaces.

The trade-off is maintenance. Assign ownership of actions, define confirmations and reset behavior, and test important commands against the same services used by normal flows.

### Beagle

[Beagle](https://github.com/pandulapeter/beagle) is a configurable Android debug-menu library with logging, OkHttp inspection, metadata, screen capture, and bug-report features. Its published UI modules use Activity/View-based integrations such as a drawer, dialog, and bottom sheet. A Compose app can host or launch that UI, but should assess the integration rather than assume native Compose support.

Beagle provides no-op artifacts for release variants. Check the actual packaged release artifact as well as lifecycle behavior, theme requirements, dependencies, and diagnostic-data handling before adoption.

### Hyperion

[Hyperion for Android](https://github.com/willowtreeapps/Hyperion-Android) is a plugin drawer that can open with a shake gesture. Its plugins cover build metadata, files, preferences, SQLite, recordings, and View inspection. The repository was archived in July 2026; treat it as a reference for the drawer pattern rather than a maintained choice for a new Compose project.

## Build boundaries and security

Put privileged implementations in an internal build-variant source set or module. Exclude them from release packages where possible; a hidden entry button or runtime flag is insufficient. Use a release no-op implementation only when shared code needs the API, and verify the resulting artifact.

Internal builds still need controlled distribution, access checks, safe environment switching, redacted diagnostics, and an audit trail for dangerous actions. Limit access to production data. See [QA-Friendly Debug Builds](qa-debug-builds.md) for export safeguards.

## See also

* [QA-Friendly Debug Builds](qa-debug-builds.md)
* [Logging and Diagnostic Data](logging-diagnostics.md)
* [Network Inspection](network-inspection.md)
* [Gradle & Build System](../android/gradle-build-system.md)
