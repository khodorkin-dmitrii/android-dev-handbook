# QA-Friendly Debug Builds

A mobile app should give QA enough evidence to reproduce and classify a defect without source access or Android Studio. Keep diagnostics focused on questions that arise in real investigations.

## What an internal build should expose

Useful diagnostics include:

* environment, API host, app version, build number, and commit SHA;
* account and session status without credentials or tokens;
* feature flags and experiment assignments;
* local database and cache summaries;
* recent request metadata, application logs, and normalized errors;
* push registration status without displaying the token;
* background work and sync status;
* permissions and relevant device metadata;
* a diagnostic ID linking app, backend, and test evidence.

Prefer summaries and controlled actions to unrestricted database or file browsers.

## Diagnostic bundle

```text
diagnostic-report/
├── app-metadata.json
├── device-metadata.json
├── feature-flags.json
├── recent-logs.txt
├── network-summary.json
├── local-state-summary.json
└── optional-screenshot-or-screen-recording
```

Capture a consistent snapshot where possible. Include timestamps, schema version, app version, and report ID. Bound log count, age, and archive size. Generate each file from an allowlist of fields; redact sensitive values before writing and inspect the final archive, including optional media.

Exclude passwords, auth tokens, payment data, unrestricted production records, and full request or response bodies by default. Require an explicit export action, define retention and access for the shared bundle, and make clear who can receive it. A screenshot may reveal more than the text report.

## Useful debug actions

* reset onboarding or clear local cache;
* expire the current session through the normal sign-out path;
* force offline mode;
* simulate a server error, empty state, or degraded response;
* trigger sync or approved background work;
* copy a diagnostic ID;
* open an internal screen;
* refresh feature flags;
* reproduce a predefined application state.

Use the same application services as real flows where possible. Direct storage edits can create impossible states. Label simulated conditions visibly, provide a reliable reset, and record which controls were active when a defect was captured.

## Architecture and security

Keep diagnostic contracts in app-owned interfaces and their implementations in internal build-variant source sets:

```text
QA / Debug UI
      ↓
Diagnostic queries and controlled commands
      ↓
Repositories, WorkManager, feature flags, logger, network summaries
```

Keep privileged controls out of the release artifact: verify the packaged variant, not just a runtime flag or hidden menu. Internal builds still need controlled distribution, environment restrictions, and access checks for sensitive operations. Audit dangerous actions and provide revocation where the distribution model requires it. Treat production data with the same care in an internal APK as in a public release.

Review the available evidence and actions with QA, mobile, backend, security, and privacy teams. Expose what shortens a real investigation.

## See also

* [In-App Debug Menus](in-app-debug-menus.md)
* [Network Inspection](network-inspection.md)
* [Logging and Diagnostic Data](logging-diagnostics.md)
* [Background Work & System Behavior](../android/background-work-system-behavior.md)
* [Testing Strategy](../testing/strategy.md)
