# QA-Friendly Debug Builds

A mobile application should not be a black box for QA. A useful internal build exposes enough state to reproduce and classify a defect without requiring source access or Android Studio.

## What an internal build should expose

High-value diagnostics include:

* active environment, API host, app version, build number, and commit SHA;
* account/session state without credentials;
* feature flags and experiment assignments;
* local database and cache summaries;
* recent request history, application logs, and last normalized errors;
* push token registration status, not unrestricted token display;
* background-work and sync status;
* permissions and relevant device metadata;
* a diagnostic ID that links mobile, backend, and test evidence.

Prefer summaries and safe actions over unrestricted database/file browsers. The purpose is investigation, not bypassing application boundaries.

## Diagnostic bundle

```text
diagnostic-report/
├── app-metadata.json
├── device-metadata.json
├── feature-flags.json
├── recent-logs.txt
├── network-summary.json
├── local-state-summary.json
└── screenshot-or-screen-recording
```

Generate the bundle from immutable snapshots where possible. Include timestamps, schema version, app version, and a report ID. Bound log count and file size. Apply redaction before writing any file, then review the final archive against an allowlist.

Never include passwords, auth tokens, payment data, unrestricted production records, or full payloads by default. Exports need explicit user action, short retention, secure sharing, and clear ownership after they leave the device.

## Useful debug actions

* reset onboarding or clear local cache;
* expire the current session safely;
* force offline mode;
* simulate server error, empty state, or degraded response;
* trigger sync or approved background work;
* copy a diagnostic ID;
* open a specific internal screen;
* refresh feature flags;
* reproduce a predefined application state.

Actions should use the same application services as real flows where possible. Directly editing storage can create impossible states and misleading defect reports. Label simulated state visibly and make reset behavior predictable.

## Architecture and security

Put diagnostic contracts in application-owned interfaces and implementations in debug/internal source sets:

```text
QA / Debug UI
      ↓
Diagnostic queries and controlled commands
      ↓
Repositories, work manager, feature flags, logger, network summaries
```

Powerful internal builds still need access control, environment restrictions, signed distribution, remote revocation where required, and auditing for dangerous operations. Production-like data deserves production-like handling even when the APK is not public.

Review diagnostic capabilities with QA, mobile, backend, security, and privacy stakeholders. The best internal build exposes evidence that shortens a real investigation, not every value the app can technically read.

## See also

* [In-App Debug Menus](in-app-debug-menus.md)
* [Network Inspection](network-inspection.md)
* [Logging and Diagnostic Data](logging-diagnostics.md)
* [Background Work & System Behavior](../android/background-work-system-behavior.md)
* [Testing Strategy](../testing/strategy.md)

