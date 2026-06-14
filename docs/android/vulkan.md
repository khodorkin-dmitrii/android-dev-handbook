# Vulkan

Vulkan - a low-level graphics and compute API created as a more explicit and modern alternative to OpenGL ES for direct GPU control.

## Vulkan basics

### Why it appeared

Vulkan appeared to give apps more control over GPU work, memory management, synchronization and multi-threaded command recording.

OpenGL ES is historically easier to use, but much of the work is hidden inside the driver: validation, state tracking, resource management and implicit synchronization. This is convenient, but can create unpredictable overhead.

Vulkan moves more responsibility to the app: the developer explicitly creates resources, command buffers, pipelines, synchronization primitives and manages memory.

**In short:** Vulkan appeared for more explicit, predictable and efficient GPU management, especially in complex rendering engines.

### Differences from OpenGL ES

OpenGL ES is a state-machine API with a lot of implicit behavior. Vulkan is an explicit API where almost everything is defined upfront and explicitly.

Key differences:

- Vulkan requires explicit memory management;
- synchronization is defined manually through fences, semaphores and barriers;
- pipelines describe rendering state upfront;
- command buffers can be recorded ahead of time and from different threads;
- the driver does less hidden work during draw.

OpenGL ES is easier to start with and is often enough for custom effects, camera filters and moderate rendering. Vulkan is more complex, but scales better for large engines, complex scenes and multi-threaded rendering.

**In short:** OpenGL ES is simpler and more implicit; Vulkan is more complex and explicit, but gives more control over performance.

### Pros and cons

Vulkan advantages:

- lower driver overhead in complex scenes;
- more predictable performance model;
- better multi-threading for preparing command buffers;
- explicit control over memory and synchronization;
- unified modern API model for graphics and compute.

Disadvantages:

- high entry barrier;
- much more boilerplate;
- harder debugging;
- easy to introduce bugs in synchronization or memory lifetime;
- does not always provide benefits for simple UI/2D tasks.

Most regular Android apps do not need Vulkan directly. It is often used through a game engine or rendering engine rather than written as raw Vulkan by hand.

**In short:** Vulkan is powerful, but expensive in complexity; it is justified where engine-level GPU control is needed.

### How often it is used in Android apps

In regular Android apps, Vulkan is rarely used directly. Most screens are built through View System, Compose, Canvas or media/camera APIs.

Vulkan is more common in:

- games;
- 3D engines;
- AR/VR;
- heavy visualization;
- CAD/product viewers;
- custom rendering engines;
- some camera/video/image processing pipelines.

In many production apps, Vulkan may be present indirectly: through Unity, Unreal, Filament, Sceneform-like wrappers, maps/visualization engines or vendor SDKs.

If the task is a regular business UI, chart or custom 2D component, Vulkan is almost always excessive.

**In short:** raw Vulkan in Android app code is rare; it is more often used by engines and SDKs that need complex GPU rendering.
