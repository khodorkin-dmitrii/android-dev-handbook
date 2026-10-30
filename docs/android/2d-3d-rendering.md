# 2D and 3D Rendering

Android graphics range from standard Compose or View UI to custom drawing, shaders and 3D engines. Choose the smallest tool that meets the visual and interaction requirements, then profile the result on target devices.

## Rendering choices

### CPU and GPU work

Most frames involve both processors. The CPU handles app logic, layout and drawing-command preparation; the GPU can rasterize and composite the result. `Canvas` is a drawing API, not a synonym for CPU rendering: a hardware-accelerated View or Compose canvas uses the GPU, while drawing into a software `Bitmap` uses a different path.

Slow main-thread layout, computation or drawing-code work suggests a CPU-side bottleneck. Expensive shaders, overdraw, large textures and complex 3D scenes may pressure the GPU. Uploads and synchronization can also stall frames. Use traces and frame profiling to locate the actual cost before changing APIs.

### When to use Canvas

Use [Android Canvas](canvas.md) for custom 2D drawing that belongs inside regular UI: charts, progress indicators, paths, signatures, waveforms or decorative shapes. In Compose, `Canvas` and drawing modifiers expose `DrawScope`; in the View system, custom drawing usually happens in `onDraw()`.

Keep drawing work small and avoid repeated allocations, bitmap decoding or heavy calculations on every frame. `invalidate()` requests redraw; call `requestLayout()` when size or layout requirements change. Canvas does not require a custom OpenGL ES renderer to benefit from hardware acceleration.

### When to use AGSL

[AGSL and `RuntimeShader`](agsl-runtime-shader.md) provide programmable pixel effects inside Android's UI rendering system. They suit gradients, distortion, transitions and local filters. `RuntimeShader` requires Android 13 (API 33), so plan a fallback for older supported devices. AGSL does not provide a geometry pipeline or a 3D scene.

### When to use OpenGL ES

[OpenGL ES](opengl-es.md) is useful when the app needs its own GPU pipeline for custom geometry, textures and shaders, such as a renderer, camera effect or specialized animated visualization. It requires management of buffers, shader programs, matrices and the rendering surface lifecycle. Prefer it when these controls justify the implementation cost.

### When to use Vulkan

[Vulkan](vulkan.md) offers more explicit control over resources, command submission and synchronization. It can reduce CPU driver overhead in a complex renderer, but raises development and device-compatibility costs. Benchmark the workload and check device features; a Vulkan backend alone does not guarantee smoother frames.

### When to use Filament

[Google Filament](google-filament.md) provides a real-time 3D scene model with cameras, renderables, PBR materials, lighting and glTF asset support. It fits model viewers, product previews, configurators and interactive 3D visualizations when building a renderer from scratch is unnecessary. It still requires surface and resource lifecycle handling, plus attention to asset size and frame time.

For ordinary screens and simple 2D animation, start with Compose, Views and their drawing APIs. Move to a lower-level API or a 3D engine when the required scene, effects or measured performance call for it.
