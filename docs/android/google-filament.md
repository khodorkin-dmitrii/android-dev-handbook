# Google Filament

Filament is a real-time physically based rendering (PBR) engine for Android and other platforms. It provides a scene, materials, lighting and asset pipeline above low-level graphics APIs. Use it when an app needs interactive 3D without building its own renderer.

## Filament basics

### What it is

With [OpenGL ES](opengl-es.md) or [Vulkan](vulkan.md), an app manages graphics state and draw commands directly. Filament instead exposes cameras, entities, renderables, lights and materials. The engine handles much of the shader, lighting and backend work, while the app still owns its scene content and resource lifecycle.

For a local UI shader effect without a 3D scene, [AGSL and `RuntimeShader`](agsl-runtime-shader.md) are usually a smaller choice.

### How it is structured

- `Engine` creates and owns Filament resources.
- `Scene` holds the entities included in a rendered scene, such as renderables and lights.
- `Camera` is a component attached to an entity; it defines view and projection transforms.
- `View` selects a `Scene` and `Camera` and configures the viewport and rendering options.
- `Renderer` submits a `View` for a frame.
- `SwapChain` connects rendering to a platform surface.

On Android, a typical setup creates an `Engine`, `Renderer`, `Scene`, `View`, `Camera` and a `SwapChain` for the current surface. A frame uses `beginFrame(swapChain)`, `render(view)` and `endFrame()`; skip rendering when `beginFrame()` returns `false`. Keep the `View` viewport in sync with the surface size.

The Android surface can be recreated independently of the activity. Recreate its `SwapChain` when the surface changes, stop scheduling frames when rendering is paused, and release Filament resources when their owner ends. Filament's Android `UiHelper` can assist with surface integration. Do not assume that a detached or destroyed surface remains a valid render target.

### Relationship with graphics APIs

Filament can use OpenGL ES or Vulkan as an Android backend. Choosing Filament does not require writing backend-specific draw calls for each object. It also does not remove GPU limits: texture memory, overdraw, asset complexity and frame time still need measurement on target devices.

## Scene model

### Cameras

A camera defines the observer's transform and projection. For perspective projection, field of view, aspect ratio and near/far clipping planes shape the visible volume. A camera does not render on its own; a `View` uses it to display a `Scene`. Update projection and viewport when the output size changes.

### Scenes

A `Scene` includes entities with renderable or light components. Transform components position objects; materials and geometry describe what a renderable looks like. A scene can contain one model or many objects, lights and an environment. Animation updates scene state, while the renderer draws frames from the selected view.

### Materials

Filament materials describe surface properties such as base color, metallic response, roughness, normal mapping, transparency and emission. A compiled material can have instances with different parameter values or textures. PBR gives materials a consistent lighting model, but visual quality still depends on suitable textures, lighting and color handling.

### Lighting

Filament supports direct lights and image-based lighting (IBL). An environment can contribute ambient illumination and reflections, which are particularly useful for PBR materials. Lights, shadows, reflections and material features have a rendering cost; tune them against the frame budget.

### Assets and use cases

Filament's `gltfio` library can load glTF 2.0 assets; its material tools compile Filament material definitions. This makes Filament suitable for model viewers, product previews, configurators and interactive 3D visualizations. Loading, decoding and releasing assets still need deliberate lifecycle and memory handling.

For regular app screens, charts and simple 2D drawing, Compose, Views or Canvas are usually sufficient. See [2D and 3D Rendering](2d-3d-rendering.md) for a broader comparison.
