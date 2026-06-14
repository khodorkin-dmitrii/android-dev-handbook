# Google Filament

Google Filament - a real-time physically based rendering engine that simplifies creating high-quality 3D graphics on Android and other platforms.

## Filament basics

### What it is

Filament - a 3D rendering engine from Google for real-time rendering with support for PBR (physically based rendering), materials, lighting, cameras, scenes and different graphics backends.

It sits above OpenGL ES/Vulkan: the developer works not with raw draw calls and shaders for every object, but with engine abstractions - scene, entity, material, camera, light and renderable.

Filament is useful when high-quality 3D rendering is needed without writing a custom engine from scratch.

**In short:** Filament is a 3D engine on top of graphics APIs that provides a ready-made model for scenes, materials, cameras and lighting.

### How it is structured

Filament has several key entities:

- `Engine` - the central object that manages rendering resources;
- `Renderer` - renders a frame;
- `Scene` - contains objects and lights;
- `View` - connects scene, camera and viewport;
- `Camera` - defines the point of view;
- materials - describe the appearance of surfaces;
- renderables - geometry objects that can be drawn.

Usually, an app creates `Engine`, `SwapChain`, `Renderer`, `Scene`, `View` and `Camera`, then adds renderable entities and triggers rendering every frame.

Filament also has tooling for materials and assets, such as a material compiler and glTF support through companion libraries.

**In short:** Filament is built around engine, scene, view, camera, renderables, lights and materials.

### Relationship with OpenGL/Vulkan

Filament uses a graphics backend under the hood. Depending on platform and settings, this can be OpenGL ES, Vulkan, Metal or another backend.

For Android, this means Filament can use the GPU through a backend, but the app does not have to write OpenGL ES or Vulkan code directly.

This abstraction layer is useful: the rendering engine handles shader generation, material model, lighting, resource management and some platform-specific details.

But abstraction does not remove basic graphics constraints: GPU memory, texture size, frame budget, lighting cost, overdraw, asset complexity and lifecycle still matter.

**In short:** Filament works on top of OpenGL/Vulkan-like backends and hides most low-level graphics boilerplate.

## Scene model

### Cameras

Camera in Filament defines projection and view transform: where the observer is, where it looks and which projection is used.

Typical parameters:

- position and orientation;
- field of view;
- near/far clipping planes;
- aspect ratio;
- perspective or orthographic projection.

Camera does not draw by itself. It defines how a `View` sees a `Scene` during rendering.

**In short:** camera defines the point of view and projection through which a scene becomes an image.

### Scenes

Scene contains renderable objects and lights that participate in rendering.

Unlike simple Canvas drawing, a 3D scene usually stores a set of entities, transforms, materials, geometry and lighting setup. Each frame, the rendering engine calculates what is visible to the camera, which materials to apply and how lighting affects surfaces.

Scene can be simple - one 3D model viewer - or complex, with several objects, lights, skybox, indirect light and animation.

**In short:** scene is a container for the 3D world that the renderer displays through the selected camera and view.

### Materials

Material describes how a surface reacts to light and how it looks: base color, metallic, roughness, normal map, alpha, emissive and other parameters.

Filament uses a PBR approach, so materials are intended to behave in a physically plausible way. This helps produce a stable realistic look with different lighting setups.

Material can be parameterized: one compiled material definition can be used with different values/textures for different objects.

**Important:** 3D quality often depends not only on geometry, but also on materials, textures, lighting and color management.

**In short:** material defines the appearance of a surface and its interaction with lighting.

### Lighting

Lighting in Filament includes direct lights and image-based lighting.

Direct lights are directional, point, spot lights and other sources explicitly placed in a scene. Image-based lighting uses environment/skybox for more realistic reflected light.

For PBR rendering, lighting is critical: without a correct light setup, even good models and materials can look flat or unnatural.

Lighting affects performance. Many light sources, large shadow maps and complex materials increase GPU cost.

**In short:** lighting defines how materials are perceived in a scene and strongly affects 3D rendering quality.

### Typical use cases

Filament fits:

- 3D model viewer;
- product preview;
- AR-related rendering;
- interactive 3D objects;
- educational visualization;
- configurators;
- maps/scene visualization;
- rendering glTF assets.

It is usually excessive for regular business screens, simple charts and flat 2D graphics. For such tasks, Compose, View System or Canvas is usually enough.

**In short:** Filament is chosen when high-quality real-time 3D is needed without writing a custom OpenGL/Vulkan engine.
