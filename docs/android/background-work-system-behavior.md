# Background Work & System Behavior

Android restricts background work to save battery, protect the user and keep system behavior predictable.

## Background work

### Doze Mode

Doze Mode - an Android power-saving mode that restricts background activity when the device has been unused for a long time, is stationary and the screen is off.

In Doze, the system delays normal background jobs, network access, sync and alarms. Periodically, maintenance windows open where apps can perform part of the deferred work.

For tasks that must run reliably, prefer `WorkManager` / `JobScheduler` over a raw background thread. For exact timing, alarms exist, but they come with restrictions and should be used carefully.

**In short:** Doze protects battery by batching and delaying background work, so apps should use system-aware APIs instead of assuming background execution is always available.

### WorkManager

`WorkManager` - a Jetpack API for deferrable background work that should run reliably once constraints are met.

It fits tasks such as uploading logs, syncing data, cleanup and retryable network work. You can define constraints: network, charging, battery not low, storage not low.

`WorkManager` supports one-time and periodic work, chaining, retries, backoff policy and persistence after process or device restart.

**Important:** `WorkManager` is not intended for exact tasks like "run exactly at 12:00" and does not replace a foreground service for immediate user-visible work.

**In short:** `WorkManager` is the recommended API for reliable deferrable background work with constraints and retry support.

### Foreground Service

Foreground Service - a `Service` for work the user should know about right now. It must show a persistent notification.

Typical scenarios: navigation, media playback, active location tracking, ongoing call, connected device operation and long-running user-initiated task.

Foreground Service does not mean a separate thread: heavy work still needs to run outside the main thread.

Newer Android versions add extra restrictions: you must declare a foreground service type, request the corresponding permissions and account for restrictions on starting a foreground service from the background.

**In short:** foreground service is for immediate user-visible ongoing work, while `WorkManager` is better for deferrable reliable background tasks.

### Background restrictions

Android has gradually strengthened background restrictions to save battery and protect the user from hidden background activity.

Restrictions affect background services, implicit broadcasts, background location, exact alarms, foreground service launch, jobs, network access and battery optimizations.

A practical approach is to choose the API by task type. For deferred reliable work - `WorkManager`. For exact alarms - `AlarmManager`, accounting for permissions/restrictions. For active user-visible work - foreground service. For push-triggered events - FCM, also with restrictions.

Do not design an Android app as if it can run in the background indefinitely. The system may stop the process, defer work or restrict access to resources.
