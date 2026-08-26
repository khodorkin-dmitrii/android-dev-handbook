# Core Android System Services

Android system services coordinate platform-wide behavior such as component launches, processes, installed packages, windows and input. Applications usually reach them through public framework APIs such as `ActivityManager`, `PackageManager` and `WindowManager`; Binder carries many of those calls across process boundaries.

## What a system service is

A framework or system service owns platform-level state and policy shared by many applications. It is different from an application `Service`, which is an Android app component with callbacks such as `onStartCommand()` and `onBind()`. An app `Service` does not automatically get a separate process or background thread.

Many Java framework services are initialized in, or closely associated with, the `SystemServer` process. This is not true for every Android service. Important native platform components can live in separate processes; SurfaceFlinger, which composites graphical surfaces for display, is one example.

A compact startup context is:

```text
init -> Zygote -> SystemServer -> framework services
```

`init` starts Zygote, and Zygote creates `SystemServer`. `SystemServer` then starts framework services in dependency-aware phases. This is only orientation, not a complete Android boot sequence.

## Core services

### Activity Manager Service - AMS

Activity Manager Service (AMS) coordinates application processes and tracks how important they are to the user. That process importance influences which cached processes the system can reclaim under memory pressure. AMS also coordinates application `Service` and broadcast execution, participates in crash and ANR handling, and works with package, task, window and other framework services.

AMS is not the sole owner of every activity or task concern in modern Android. It coordinates process-level and component-level work with Activity Task Manager Service, and the application process receives lifecycle transactions through framework plumbing before its `Activity` callbacks run. This distinction matters when reading logs: an activity transition can involve ATMS, AMS, the app process and WMS rather than one manager directly invoking every callback.

### Activity Task Manager Service - ATMS

Activity Task Manager Service (ATMS) owns a substantial part of modern activity and task management. It coordinates activity launches, task and back-stack state, activity state transitions, display placement and task organization, including multi-window scenarios.

ATMS collaborates closely with AMS when a launch needs an application process or affects process importance. It also collaborates with WMS because an activity and its task have window, display and transition consequences. A task is a user-oriented stack of activities, not simply "one task per application"; flags, launch modes, document behavior and multi-window can produce more complex arrangements.

### Package Manager Service - PMS

Package Manager Service (PMS) maintains the platform's view of installed packages and their state. During boot and package changes, package-management code scans and records packages, manifests, components and related metadata. It supports package and component queries, intent resolution, enabled or disabled state, and permission-related package information.

PMS is central to answering questions such as "which activity can handle this intent?" or "what metadata belongs to this component?" It does not make every runtime security decision alone. Permission enforcement is distributed across the framework service that exposes an operation, permission-management components, app-ops and other platform layers.

### Window Manager Service - WMS

Window Manager Service (WMS) manages window hierarchy and policy: bounds, z-order, focus, display organization, app and system windows, insets, transitions and other window-level state. It coordinates with ATMS for activity and task windows and supplies window and focus information used by input routing.

WMS does not render an application's views and does not composite the final pixels. The application renders buffers into a `Surface`. WMS manages placement and metadata, while the separate native SurfaceFlinger process combines visible graphical surfaces, with help from Hardware Composer where appropriate, for presentation on the display.

### Input Manager Service - IMS

Input Manager Service (IMS), together with native input components, coordinates reading and dispatching events from touchscreens, keyboards and other input devices. To select a target, input dispatch uses current window, display, touch and focus information maintained in cooperation with WMS.

The chosen events travel through an input channel toward the appropriate application window, where the app framework dispatches them through the view hierarchy or Compose input system. This explains why an input symptom can originate outside a click handler: the wrong focused window, a blocking overlay, a stale window or an unresponsive main thread can prevent the expected UI target from receiving or processing events.

## Application launch as a cooperative flow

After the user taps a launcher icon, the participating services can be understood with this simplified sequence:

1. The launcher requests that an activity be started through a public framework API.
2. Package-management state is consulted to resolve or validate the target component and obtain its metadata.
3. ATMS coordinates the activity launch, task selection and back-stack transition.
4. AMS ensures that a suitable application process exists and accounts for its process state.
5. If a new process is needed, the platform asks the appropriate Zygote to create or specialize one. Modern devices may use a pre-forked USAP pool, so this is not always a fresh fork at that moment.
6. The framework schedules creation and lifecycle work in the application process, while WMS prepares and manages the corresponding window and transition.
7. The application renders UI buffers into its surface.
8. SurfaceFlinger composites visible surfaces for the display.
9. IMS routes subsequent input using the current focused-window and touch-target information.

This is a mental model, not a single strictly linear call chain. Some work overlaps, explicit launches need little intent resolution, existing processes and activities can be reused, and implementations evolve between Android releases. The useful point is the division of responsibilities: packages, tasks, processes, windows, composition and input are coordinated by distinct components.

## Why application developers should care

These boundaries turn platform-looking symptoms into more focused debugging questions:

- Unexpected activity reuse, Back behavior or multi-window placement often starts with ATMS task state, launch modes and intent flags.
- A screen recreated after returning to an app may reflect AMS-managed process reclamation, not an orderly `Activity.onDestroy()` path.
- ANR investigation connects main-thread responsiveness with AMS/ATMS timeout coordination and WMS or IMS waiting for the application.
- A missing intent target or disabled component points toward PMS resolution, manifest metadata, package visibility or permissions.
- A dialog, overlay or keyboard that changes focus can explain window and input behavior before application gesture code runs.

`dumpsys` exposes snapshots of this state. `dumpsys activity` helps inspect processes and component records; on current releases, activity/task information may also be surfaced through activity/task-related dumps. `dumpsys package` shows package, component and resolution data. `dumpsys window` helps with displays, windows and focus, while `dumpsys input` helps with devices and dispatch state. Output is version-dependent, so use it to test a concrete hypothesis rather than treating one field layout as a stable API.

## See also

- [Binder IPC and AIDL](binder-ipc-aidl.md)
- [Activity, Fragment & Lifecycle](activity-fragment-lifecycle.md)
- [Android Components](components.md)
- [Performance & Memory - ANR](performance-memory.md#anr)

## Further reading

- [SystemServer source - Android Open Source Project](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-16.0.0_r3/services/java/com/android/server/SystemServer.java)
- [ActivityTaskManagerService source - Android Open Source Project](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-16.0.0_r3/services/core/java/com/android/server/wm/ActivityTaskManagerService.java)
- [SurfaceFlinger and WindowManager - Android Open Source Project](https://source.android.com/docs/core/graphics/surfaceflinger-windowmanager)
- [About the Zygote processes - Android Open Source Project](https://source.android.com/docs/core/runtime/zygote)
- [Processes and app lifecycle - Android Developers](https://developer.android.com/guide/components/activities/process-lifecycle)

