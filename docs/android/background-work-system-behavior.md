# Background Work & System Behavior

Android limits background execution to protect battery, privacy, and system health. An app process can be stopped at any time, so durable work should be handed to an appropriate system-aware API.

## Choose the API by task

| Need | Preferred API |
|---|---|
| Deferrable, reliable work | `WorkManager` |
| Immediate, user-visible ongoing work | Foreground service |
| User-facing action at an exact time | `AlarmManager` when exactness is justified |
| Server-triggered event | FCM, then schedule durable follow-up work if needed |

## Doze Mode

Doze restricts background CPU and network activity while the device is idle. The system defers regular jobs, synchronization, network access, and standard alarms, then periodically opens maintenance windows for batched work.

Doze does not guarantee execution in the next window. Avoid polling and assumptions about continuous background execution. Use `WorkManager` or `JobScheduler` for work that can wait, and reserve exact alarms for time-critical user-facing cases.

## WorkManager

`WorkManager` is the recommended Jetpack API for deferrable work that should eventually run after its constraints are met: synchronization, log uploads, cleanup, and retryable network operations.

It supports one-time and periodic work, constraints, unique work, chains, retries, backoff, and persistence across process death and device restart. It does not guarantee an exact start time. Periodic work is inexact and has a minimum interval.

Expedited work suits short, important tasks that should start quickly but remains subject to quotas. Long-running user-visible work requires foreground execution rather than a hidden continuous worker.

## Foreground services

A foreground service is for work the user is actively aware of, such as navigation, media playback, a call, location tracking, or communication with a connected device. It must display an ongoing notification.

A foreground service is not a separate thread: blocking work still belongs off the main thread. Modern Android restricts background starts and requires the appropriate service type and permissions. Run it only while the user-visible operation is active.

## Alarms, push, and restrictions

Use `AlarmManager` when the user expects action at a specific time, such as an alarm clock. Exact alarms consume more power and may require special access; periodic synchronization should normally use `WorkManager`.

FCM provides a short push-handling window, not unlimited background execution. Keep handling brief and schedule durable follow-up work when necessary.

Restrictions also affect services, implicit broadcasts, location, jobs, and network access. Design for delays, process death, duplicate attempts, and retries; make background operations idempotent when possible.

## Related topics

- [Android Components](components.md)
- [Activity, Fragment & Lifecycle](activity-fragment-lifecycle.md)
- [Coroutine Scopes & Cancellation](../coroutines-flow/scopes-cancellation.md)
