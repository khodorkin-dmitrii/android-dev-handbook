# OpenGL ES

OpenGL ES - низкоуровневый graphics API для GPU rendering на embedded/mobile устройствах. В Android он используется для 2D/3D rendering, игр, visual effects, camera filters и custom graphics engines.

## Основы OpenGL ES

### Базовая архитектура

OpenGL ES работает как state machine: приложение на CPU настраивает graphics state, buffers, shaders, textures и draw calls, а GPU выполняет rendering.

В Android OpenGL ES обычно используют через `GLSurfaceView`, `TextureView`, `SurfaceView` или собственную работу с EGL. `GLSurfaceView.Renderer` даёт callbacks вроде `onSurfaceCreated()`, `onSurfaceChanged()` и `onDrawFrame()`.

Минимальный rendering loop обычно делает три вещи: создаёт GPU resources, обновляет state сцены и вызывает draw calls каждый frame.

**Важно:** OpenGL ES даёт много контроля, но требует вручную управлять buffers, shaders, textures, matrices, lifecycle surface и ошибками GPU state.

**Коротко:** OpenGL ES - API для прямой работы с GPU pipeline, где приложение само описывает geometry, shaders, textures и draw calls.

### Vertex Buffer

Vertex Buffer - область GPU memory, где хранятся vertex data: позиции, texture coordinates, normals, colors и другие attributes.

Вместо того чтобы отправлять vertices на GPU каждый frame из CPU memory, данные загружают в buffer и переиспользуют в draw calls.

Пример данных для простого треугольника:

```kotlin
val vertices = floatArrayOf(
    0.0f,  0.5f, 0.0f,
   -0.5f, -0.5f, 0.0f,
    0.5f, -0.5f, 0.0f
)
```

В реальном OpenGL ES коде эти данные кладут в `FloatBuffer`, создают buffer object через `glGenBuffers()`, загружают через `glBufferData()` и описывают layout attributes через `glVertexAttribPointer()`.

**Коротко:** Vertex Buffer хранит geometry data на GPU и позволяет эффективно переиспользовать vertices при rendering.

### Vertex Shader

Vertex Shader - программа, которая выполняется для каждого vertex. Обычно она преобразует координаты из model space в clip space и передаёт данные дальше в pipeline.

Типичные задачи vertex shader:

- применить model/view/projection matrices;
- передать texture coordinates во fragment shader;
- подготовить normals или colors;
- выполнить простые vertex transformations.

Пример упрощённого shader:

```glsl
attribute vec4 aPosition;
uniform mat4 uMvpMatrix;

void main() {
    gl_Position = uMvpMatrix * aPosition;
}
```

**Коротко:** Vertex Shader отвечает за обработку vertices и их позицию в graphics pipeline.

### Fragment Shader

Fragment Shader - программа, которая вычисляет цвет каждого fragment, который потенциально станет pixel на экране.

Он может использовать constant color, texture sampling, lighting calculations, alpha, fog, post-processing и другие effects.

Пример:

```glsl
precision mediump float;
uniform vec4 uColor;

void main() {
    gl_FragColor = uColor;
}
```

Fragment shader часто является дорогой частью pipeline, потому что выполняется для большого количества fragments. Сложные lighting/effects, texture lookups и overdraw могут заметно влиять на performance.

**Коротко:** Fragment Shader вычисляет итоговый цвет fragments и часто определяет визуальный стиль объекта.

### Texture

Texture - изображение или набор данных, загруженный в GPU memory и доступный shader-ам для sampling.

Textures используют для изображений на поверхностях, material maps, sprites, fonts, UI atlases, camera frames, normal maps и post-processing.

В Android важно учитывать размеры texture, format, mipmaps, filtering и lifecycle. Слишком большие textures расходуют GPU memory, а частая загрузка textures может вызывать stutter.

Типичные настройки:

- min/mag filtering: nearest или linear;
- wrap mode: clamp или repeat;
- mipmaps для уменьшения aliasing на удалённых объектах.

**Коротко:** Texture - GPU resource с изображением или данными, которые shader может читать при rendering.

### Coordinate Systems

В graphics pipeline обычно есть несколько coordinate systems:

- model/local space - координаты внутри объекта;
- world space - координаты объекта в сцене;
- view/camera space - координаты относительно камеры;
- clip space - результат projection transform;
- normalized device coordinates - координаты после perspective divide;
- screen/window space - координаты пикселей на экране.

Переходы между ними обычно задаются matrices: model, view и projection. Вместе их часто называют MVP matrix.

```text
model coordinates -> world -> view -> clip -> screen
```

На Android дополнительно нужно помнить про разные системы координат для touch input, bitmap, texture coordinates и screen orientation.

**Коротко:** coordinate systems помогают отделить geometry объекта, положение в мире, камеру и финальное положение на экране.

### Rendering Pipeline

Упрощённый OpenGL ES pipeline:

1. CPU подготавливает data, state и draw call.
2. Vertex Shader обрабатывает vertices.
3. Primitive assembly собирает triangles/lines/points.
4. Rasterization превращает primitives во fragments.
5. Fragment Shader вычисляет цвет fragments.
6. Depth/stencil/blending tests решают, попадёт ли fragment в framebuffer.
7. Framebuffer выводится на экран.

Performance зависит от количества draw calls, vertices, fragment cost, overdraw, texture bandwidth, state changes и синхронизации CPU/GPU.

**Коротко:** OpenGL ES pipeline превращает vertex data и shader programs в pixels на экране через последовательность GPU stages.
