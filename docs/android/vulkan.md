# Vulkan

Vulkan is an explicit, low-level API for graphics and compute. On Android, it is mainly relevant to games, rendering engines and demanding visualization rather than ordinary app screens.

## Vulkan basics

### Why it appeared

Vulkan gives an application more control over GPU resources, command submission and synchronization. Compared with OpenGL ES, it moves more work from the driver to the application. This can reduce CPU driver overhead and make complex rendering easier to scale across CPU threads, but also increases implementation and maintenance cost.

Lower overhead is a possibility, not an automatic frame-rate improvement: GPU workload, memory bandwidth and frame pacing still matter. Measure on target devices.

### Differences from OpenGL ES

[OpenGL ES](opengl-es.md) uses a stateful API with more work handled implicitly by the driver. Vulkan requires the application to define much of that work explicitly:

- allocate and bind memory for buffers and images, then manage resource lifetimes;
- create pipelines describing shader and fixed-function state;
- record commands into command buffers and submit them to queues;
- synchronize resource access and presentation with barriers, semaphores and fences where needed.

Different CPU threads can record separate command buffers, subject to Vulkan's threading rules. This does not mean one command buffer can be recorded concurrently by several threads. Shader modules are typically supplied as SPIR-V rather than GLSL source strings compiled by the driver at runtime.

OpenGL ES remains useful for smaller custom renderers. Vulkan is a better candidate when the engine needs its explicit control or a feature unavailable in OpenGL ES. Migration should be justified by profiling and device coverage, not by API choice alone.

### Trade-offs

Vulkan can reduce driver overhead, support parallel command preparation and expose modern graphics features. In return, setup is longer and mistakes in synchronization, memory lifetime or presentation can be difficult to debug. It is especially important to test across actual Android GPU drivers.

Android exposes Vulkan through the NDK starting at API level 24, but the OS version alone does not prove that a device supports the required Vulkan version or features. Check device capabilities at runtime and provide a supported rendering path for devices outside your target set. Declare a required Vulkan feature in the manifest only if the app cannot work without it.

### Where Android apps use it

Vulkan is common behind game and rendering engines and can serve custom 3D, AR/VR or compute-heavy visualization. A regular Compose or View screen generally does not need direct Vulkan code. An app may also use an engine or SDK with a Vulkan backend without calling Vulkan itself.

For choosing a higher-level 3D renderer, see [Google Filament](google-filament.md). For the wider Android rendering landscape, see [2D and 3D Rendering](2d-3d-rendering.md).
