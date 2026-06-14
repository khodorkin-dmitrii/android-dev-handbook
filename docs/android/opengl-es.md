# OpenGL ES

OpenGL ES - a low-level graphics API for GPU rendering on embedded/mobile devices. On Android, it is used for 2D/3D rendering, games, visual effects, camera filters and custom graphics engines.

## OpenGL ES basics

### Basic architecture

OpenGL ES works as a state machine: the app on the CPU configures graphics state, buffers, shaders, textures and draw calls, while the GPU performs rendering.

On Android, OpenGL ES is usually used through `GLSurfaceView`, `TextureView`, `SurfaceView` or custom EGL handling. `GLSurfaceView.Renderer` provides callbacks such as `onSurfaceCreated()`, `onSurfaceChanged()` and `onDrawFrame()`.

A minimal rendering loop usually does three things: creates GPU resources, updates scene state and calls draw calls every frame.

**Important:** OpenGL ES gives a lot of control, but requires manual management of buffers, shaders, textures, matrices, surface lifecycle and GPU state errors.

**In short:** OpenGL ES is an API for direct work with the GPU pipeline, where the app describes geometry, shaders, textures and draw calls itself.

### Vertex Buffer

Vertex Buffer - an area of GPU memory where vertex data is stored: positions, texture coordinates, normals, colors and other attributes.

Instead of sending vertices to the GPU from CPU memory every frame, data is uploaded to a buffer and reused in draw calls.

Example data for a simple triangle:

```kotlin
val vertices = floatArrayOf(
    0.0f,  0.5f, 0.0f,
   -0.5f, -0.5f, 0.0f,
    0.5f, -0.5f, 0.0f
)
```

In real OpenGL ES code, this data is placed into a `FloatBuffer`, a buffer object is created with `glGenBuffers()`, data is uploaded through `glBufferData()`, and layout attributes are described with `glVertexAttribPointer()`.

**In short:** Vertex Buffer stores geometry data on the GPU and allows vertices to be reused efficiently during rendering.

### Vertex Shader

Vertex Shader - a program that runs for each vertex. Usually, it transforms coordinates from model space to clip space and passes data further through the pipeline.

Typical vertex shader tasks:

- apply model/view/projection matrices;
- pass texture coordinates to the fragment shader;
- prepare normals or colors;
- perform simple vertex transformations.

Example of a simplified shader:

```glsl
attribute vec4 aPosition;
uniform mat4 uMvpMatrix;

void main() {
    gl_Position = uMvpMatrix * aPosition;
}
```

**In short:** Vertex Shader is responsible for processing vertices and their position in the graphics pipeline.

### Fragment Shader

Fragment Shader - a program that calculates the color of each fragment that may become a pixel on the screen.

It can use constant color, texture sampling, lighting calculations, alpha, fog, post-processing and other effects.

Example:

```glsl
precision mediump float;
uniform vec4 uColor;

void main() {
    gl_FragColor = uColor;
}
```

Fragment shader is often an expensive part of the pipeline because it runs for a large number of fragments. Complex lighting/effects, texture lookups and overdraw can significantly affect performance.

**In short:** Fragment Shader calculates the final color of fragments and often defines the visual style of an object.

### Texture

Texture - an image or data set loaded into GPU memory and available to shaders for sampling.

Textures are used for images on surfaces, material maps, sprites, fonts, UI atlases, camera frames, normal maps and post-processing.

On Android, texture size, format, mipmaps, filtering and lifecycle matter. Textures that are too large consume GPU memory, and frequent texture uploads can cause stutter.

Typical settings:

- min/mag filtering: nearest or linear;
- wrap mode: clamp or repeat;
- mipmaps to reduce aliasing on distant objects.

**In short:** Texture is a GPU resource with an image or data that a shader can read during rendering.

### Coordinate Systems

The graphics pipeline usually has several coordinate systems:

- model/local space - coordinates inside the object;
- world space - object coordinates in the scene;
- view/camera space - coordinates relative to the camera;
- clip space - the result of the projection transform;
- normalized device coordinates - coordinates after perspective divide;
- screen/window space - pixel coordinates on the screen.

Transitions between them are usually defined by matrices: model, view and projection. Together they are often called the MVP matrix.

```text
model coordinates -> world -> view -> clip -> screen
```

On Android, additionally remember different coordinate systems for touch input, bitmap, texture coordinates and screen orientation.

**In short:** coordinate systems help separate object geometry, world position, camera and final screen position.

### Rendering Pipeline

Simplified OpenGL ES pipeline:

1. CPU prepares data, state and draw call.
2. Vertex Shader processes vertices.
3. Primitive assembly builds triangles/lines/points.
4. Rasterization turns primitives into fragments.
5. Fragment Shader calculates fragment color.
6. Depth/stencil/blending tests decide whether the fragment reaches the framebuffer.
7. Framebuffer is presented on the screen.

Performance depends on draw call count, vertices, fragment cost, overdraw, texture bandwidth, state changes and CPU/GPU synchronization.

**In short:** OpenGL ES pipeline turns vertex data and shader programs into pixels on the screen through a sequence of GPU stages.
