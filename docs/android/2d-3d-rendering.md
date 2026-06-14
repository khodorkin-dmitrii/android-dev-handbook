# 2D and 3D Rendering

Rendering in Android can be done at different levels: regular UI through View/Compose, custom 2D through Canvas, low-level GPU through OpenGL ES/Vulkan or high-level 3D through Filament.

## Rendering choices

### CPU rendering vs GPU rendering

CPU rendering means that the main work of preparing an image is performed on the CPU: layout calculations, geometry, bitmap generation, text shaping, paths and other operations.

GPU rendering means that most drawing work is performed by the GPU: rasterization, shaders, textures, blending, 3D transforms, lighting and post-processing.

In real Android UI, both are almost always involved: CPU prepares commands/data, GPU draws pixels. The question is where the bottleneck is.

CPU bottleneck often looks like long layout/calculation/bind operations on the main thread. GPU bottleneck is often related to overdraw, complex shaders, large textures, a large number of fragments or heavy 3D effects.

**In short:** CPU prepares data and commands, GPU draws pixels efficiently; performance depends on which part of the pipeline is overloaded.

### When to use Canvas

Canvas is worth using when custom 2D graphics are needed inside Android UI:

- charts and simple graphs;
- custom progress indicators;
- drawing/signature view;
- waveform/audio visualization;
- simple game-like 2D;
- custom badges, shapes, paths;
- lightweight decorative elements.

Canvas integrates well with View System and is simpler than OpenGL ES. It fits when the scene is small, rendering is 2D and per-pixel control does not require a complex GPU pipeline.

If drawing happens often, watch `onDraw()` performance: do not allocate, do not decode bitmap, do not run heavy calculations and do not call unnecessary `requestLayout()`.

**In short:** Canvas is a good choice for custom 2D drawing when integration with regular Android UI is needed and a full 3D engine is not.

### When to use OpenGL

OpenGL ES is worth using when direct GPU rendering is needed and Canvas capabilities are no longer enough.

Typical cases:

- custom 2D/3D engine;
- camera filters;
- video effects;
- particle systems;
- high-frequency animated graphics;
- rendering a large number of objects;
- custom shaders;
- simple 3D graphics without a heavy engine.

OpenGL ES requires understanding buffers, shaders, textures, matrices, surface lifecycle and GPU state. It gives more control, but sharply increases code complexity.

If the goal is a production-quality 3D scene with materials, lights, cameras and glTF assets, it is often more reasonable to use an engine like Filament instead of writing everything in raw OpenGL ES.

**In short:** OpenGL ES is used when lower-level GPU control, shaders and rendering pipeline are needed, and the team is ready to manage graphics details manually.

### When to use Filament

Filament is worth using when a high-quality 3D scene is needed, not just low-level GPU access.

Typical cases:

- 3D product viewer;
- object configurator;
- glTF model rendering;
- AR preview;
- scenes with materials and lighting;
- interactive 3D visualizations.

Filament provides ready-made abstractions: scene, camera, materials, lights, renderables and a backend on top of OpenGL/Vulkan. This is faster and safer than writing a custom 3D renderer from scratch.

But Filament is excessive for simple UI, 2D charts, small custom drawing or regular animation. Canvas, Compose or View System will be simpler there.

**In short:** Filament is chosen for real-time 3D with materials, cameras, scene and lighting when raw OpenGL is too low-level.
