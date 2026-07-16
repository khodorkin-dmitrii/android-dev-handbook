# In-App Debug Menus

An internal debug menu turns a complex application into an inspectable system. It is especially valuable when QA, support, or remote developers cannot attach Android Studio.

## Useful capabilities

A focused menu can expose:

* environment, version, build variant, and commit SHA;
* feature flags and account/session state;
* recent logs and network requests;
* safe summaries of local storage or database state;
* cache/session reset and predefined application states;
* error, offline, empty-state, and sync simulation;
* internal screen shortcuts;
* device/application metadata, screenshots, screen recording, and diagnostic export.

Actions should be grouped by problem and have clear confirmation for destructive operations. An unstructured drawer with dozens of buttons quickly becomes another unreliable subsystem.

```text
Debug UI
   ↓
Debug Actions / Commands
   ↓
Application services, repositories, feature flags and diagnostics
```

The UI should call explicit debug commands. It should not reach arbitrarily into repositories or mutate databases directly.

## Implementation approaches

### Custom debug menu

A custom screen gives full control over Compose UI, navigation, the design system, authorization, and redaction. It fits project-specific operations and can expose only stable application-owned interfaces.

The cost is development and maintenance. Define module ownership, an action registry, destructive-action confirmation, and tests so the menu does not become a random collection of shortcuts.

### Beagle

Beagle is an actively maintained customizable debug-menu library with configurable modules, logging, OkHttp inspection, metadata, screen capture, and bug-report actions. Its official UI integrations are Activity/Fragment/View based, including drawer, dialog, and bottom-sheet variants. A Compose application can host or launch it, but this is not the same as a native Compose-first UI contract.

Beagle offers no-op artifacts for production variants. Still evaluate its lifecycle hooks, theme requirements, dependency surface, data handling, and fit with the app architecture before adoption.

### Hyperion

Hyperion is a historically important plugin drawer that can open through a shake gesture and expose build data, files, preferences, SQLite, recordings, and other plugins.

Treat it as legacy/reference for new projects:

* it is primarily associated with the View-based Android era;
* its release and integration model is older;
* built-in UI inspection is not Compose-aware;
* its main value today is demonstrating the debug-drawer concept.

## Build boundaries and security

Prefer a dedicated debug/internal source set or module. Production artifacts should exclude debug implementations where appropriate, not merely hide the entry button. Use release no-op implementations only when a shared API is necessary.

Internal builds still need authentication, safe environment switching, redaction, auditability for destructive actions, and protection from unrestricted production data. A powerful menu is an operational capability, not a reason to weaken security.

## See also

* [QA-Friendly Debug Builds](qa-debug-builds.md)
* [Logging and Diagnostic Data](logging-diagnostics.md)
* [Network Inspection](network-inspection.md)
* [Gradle & Build System](../android/gradle-build-system.md)

