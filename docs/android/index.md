# Android

This section covers the Android platform itself: application entry points, lifecycle and process behavior, UI foundations, system services, storage, background execution, build tooling, performance, inter-process communication, and graphics.

For a practical learning path, start with components and lifecycle, then continue with `Context`, resources, UI, storage, and background work. Build, performance, IPC, system services, and graphics topics are most useful after the platform fundamentals.

## Platform and UI fundamentals

- [Android Components](components.md) - application entry points, intents, process boundaries, and component exposure.
- [Activity, Fragment & Lifecycle](activity-fragment-lifecycle.md) - lifecycle transitions, configuration changes, state restoration, and process death.
- [Context & Resources](context-resources.md) - context lifetimes, resources, configuration, and localization.
- [View System / XML UI](view-system-xml-ui.md) - measurement, layout, drawing, custom views, RecyclerView, and View Binding.
- [Android System Services](android-system-services.md) - platform services obtained through `Context` and their lifecycle and permission constraints.

## Data, execution, and system boundaries

- [Storage](storage.md) - Room and SQLite, preferences, files, migrations, and storage selection.
- [Background Work & System Behavior](background-work-system-behavior.md) - WorkManager, foreground services, alarms, Doze, and background restrictions.
- [Binder IPC and AIDL](binder-ipc-aidl.md) - Binder, cross-process calls, AIDL contracts, limits, lifecycle, and security.

## Build, performance, and memory

- [Gradle & Build System](gradle-build-system.md) - Gradle, Android Gradle Plugin, variants, dependency configurations, caching, and reproducibility.
- [Performance & Memory](performance-memory.md) - ANRs, jank, allocations, leaks, profiling, R8, and runtime performance.

## Graphics and rendering

- [Android Canvas](canvas.md) - immediate-mode 2D drawing and custom rendering.
- [AGSL and RuntimeShader](agsl-runtime-shader.md) - Android Graphics Shading Language, shader effects, and Compose integration.
- [OpenGL ES](opengl-es.md) - programmable GPU rendering on Android.
- [Vulkan](vulkan.md) - explicit low-level graphics and compute APIs.
- [Google Filament](google-filament.md) - real-time physically based 3D rendering.
- [2D and 3D Rendering](2d-3d-rendering.md) - API selection and rendering architecture trade-offs.
