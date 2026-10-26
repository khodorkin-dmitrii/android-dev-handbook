# OpenGL ES

OpenGL ES is a graphics API for 2D and 3D rendering on mobile devices. Android apps use it for games, camera effects and custom rendering when they need control over geometry, shaders and textures.

## OpenGL ES basics

### Basic architecture

OpenGL ES is a stateful API: CPU code configures buffers, shaders, textures and draw calls; the graphics driver and GPU process the commands. EGL connects an OpenGL ES context to a rendering surface.

`GLSurfaceView` manages a rendering thread and EGL setup for common cases. Its `Renderer` receives `onSurfaceCreated()`, `onSurfaceChanged()` and `onDrawFrame()` callbacks. Use `setEGLContextClientVersion(2)` for the OpenGL ES 2.0 shader syntax shown below. `SurfaceView`, `TextureView` or direct EGL handling offer different integration options but require more lifecycle work.

Create GL resources when the context is available, update scene state, then issue draw calls. A lost EGL context invalidates resources such as textures and buffers; recreate them in `onSurfaceCreated()`. Handle view pause/resume and avoid touching GL state from an arbitrary UI thread.

### Vertex buffer

A vertex buffer object (VBO) stores vertex attributes such as positions, texture coordinates, normals and colors in GL-managed storage. It avoids resending unchanged arrays with every draw call; the API does not guarantee a particular physical memory location.

Triangle positions before upload:

```kotlin
val vertices = floatArrayOf(
     0.0f,  0.5f, 0.0f,
    -0.5f, -0.5f, 0.0f,
     0.5f, -0.5f, 0.0f
)
```

With a VBO, create it with `glGenBuffers()`, bind it, upload data with `glBufferData()`, and set attribute layout with `glVertexAttribPointer()`. Passing a direct `FloatBuffer` to the Android GLES API is another path; a VBO is not mandatory for every draw.

### Vertex shader

The vertex shader runs for each vertex. It transforms positions, commonly from model space to clip space, and passes attributes to later stages. This OpenGL ES 2.0 example uses a model-view-projection (MVP) matrix:

```glsl
attribute vec4 aPosition;
uniform mat4 uMvpMatrix;

void main() {
    gl_Position = uMvpMatrix * aPosition;
}
```

### Fragment shader

The fragment shader computes color for generated fragments. A fragment may still be discarded by depth or stencil testing before it contributes to the framebuffer.

```glsl
precision mediump float;
uniform vec4 uColor;

void main() {
    gl_FragColor = uColor;
}
```

Complex shading, texture sampling and overdraw can make fragment work expensive. Measure on target devices before optimizing.

### Texture

A texture is GL-managed image or data storage sampled by shaders. Typical uses include sprites, material maps, fonts, camera frames and post-processing. Choose dimensions and formats with memory and upload costs in mind. Minification and magnification filters control sampling; mipmaps can improve minified textures but require additional storage and suitable filtering.

### Coordinate systems

Rendering commonly moves positions through model/local, world, view/camera and clip space. After the perspective divide, normalized device coordinates map through the viewport to window coordinates:

```text
model -> world -> view -> clip -> normalized device -> window
```

Model, view and projection matrices describe the main transforms. Touch, bitmap and texture coordinates may use different origins, so convert between them explicitly.

### Rendering pipeline

In a simplified OpenGL ES draw: the CPU prepares state and submits a draw call; vertex shading and primitive assembly process geometry; rasterization produces fragments; fragment shading computes values; per-fragment tests and blending determine framebuffer updates; the rendered surface is presented. The exact ordering of some fragment operations can vary.

Look at draw calls, vertices, fragment cost, overdraw, texture bandwidth and CPU/GPU synchronization when investigating performance. For UI-local shader effects that do not need custom geometry, see [AGSL and `RuntimeShader`](agsl-runtime-shader.md).
