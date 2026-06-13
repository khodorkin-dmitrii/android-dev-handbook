# 2D and 3D Rendering

Rendering в Android можно делать на разных уровнях: обычный UI через View/Compose, custom 2D через Canvas, low-level GPU через OpenGL ES/Vulkan или high-level 3D через Filament.

## Rendering choices

### CPU rendering vs GPU rendering

CPU rendering означает, что основная работа по подготовке изображения выполняется на CPU: расчёты layout, geometry, bitmap generation, text shaping, paths и другие операции.

GPU rendering означает, что большая часть drawing work выполняется GPU: rasterization, shaders, textures, blending, 3D transforms, lighting и post-processing.

В реальном Android UI почти всегда есть оба участника: CPU подготавливает commands/data, GPU рисует pixels. Вопрос в том, где находится bottleneck.

CPU bottleneck часто выглядит как долгие layout/calculation/bind operations на main thread. GPU bottleneck часто связан с overdraw, сложными shaders, большими textures, большим количеством fragments или тяжёлыми 3D effects.

**Коротко:** CPU готовит данные и команды, GPU эффективно рисует pixels; performance зависит от того, какая часть pipeline перегружена.

### Когда использовать Canvas

Canvas стоит использовать, когда нужна custom 2D-графика внутри Android UI:

- charts и simple graphs;
- custom progress indicators;
- drawing/signature view;
- waveform/audio visualization;
- simple game-like 2D;
- custom badges, shapes, paths;
- лёгкие декоративные элементы.

Canvas хорошо интегрируется с View System и проще, чем OpenGL ES. Он подходит, когда сцена небольшая, rendering 2D, а контроль над каждым pixel не требует complex GPU pipeline.

Если рисование происходит часто, важно следить за `onDraw()` performance: не делать allocations, не декодировать bitmap, не запускать heavy calculations и не вызывать лишний `requestLayout()`.

**Коротко:** Canvas - хороший выбор для custom 2D drawing, когда нужна интеграция с обычным Android UI и не нужен полноценный 3D engine.

### Когда использовать OpenGL

OpenGL ES стоит использовать, когда нужен прямой GPU rendering и возможностей Canvas уже недостаточно.

Типичные случаи:

- custom 2D/3D engine;
- camera filters;
- video effects;
- particle systems;
- high-frequency animated graphics;
- rendering большого числа объектов;
- custom shaders;
- простая 3D-графика без тяжёлого engine.

OpenGL ES требует понимания buffers, shaders, textures, matrices, lifecycle surface и GPU state. Он даёт больше контроля, но резко повышает сложность кода.

Если цель - production-quality 3D scene с materials, lights, cameras и glTF assets, часто разумнее использовать engine вроде Filament, а не писать всё на raw OpenGL ES.

**Коротко:** OpenGL ES используют, когда нужен lower-level GPU control, shaders и rendering pipeline, но команда готова управлять graphics details вручную.

### Когда использовать Filament

Filament стоит использовать, когда нужна качественная 3D-сцена, а не просто low-level доступ к GPU.

Типичные случаи:

- 3D product viewer;
- object configurator;
- glTF model rendering;
- AR preview;
- сцены с materials и lighting;
- interactive 3D visualizations.

Filament даёт готовые abstractions: scene, camera, materials, lights, renderables и backend поверх OpenGL/Vulkan. Это быстрее и безопаснее, чем писать собственный 3D renderer с нуля.

Но Filament избыточен для простого UI, 2D charts, небольшого custom drawing или обычной анимации. Там Canvas, Compose или View System будут проще.

**Коротко:** Filament выбирают для real-time 3D с материалами, камерами, сценой и освещением, когда raw OpenGL слишком низкоуровневый.
