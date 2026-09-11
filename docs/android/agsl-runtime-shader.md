# AGSL and RuntimeShader

Android Graphics Shading Language (AGSL) defines programmable visual effects that Android integrates into its 2D graphics pipeline. Through `RuntimeShader`, AGSL code can be used for custom drawing, gradients, distortion, transitions and filtering already-rendered UI.

AGSL was introduced in Android 13, so `RuntimeShader` is available starting with API 33.

## What AGSL is

AGSL is a C-like shading language largely compatible with GLSL ES 1.0. Shader code runs for every fragment being drawn and returns its color.

```agsl
half4 main(float2 coordinate) {
    return half4(0.2, 0.5, 1.0, 1.0);
}
```

The `coordinate` parameter contains local coordinates in the `Canvas` or `RenderNode` coordinate space. Values are expressed in pixels by default, the origin is in the upper-left corner, `x` increases to the right and `y` increases downward.

Unlike a standalone OpenGL program, an AGSL effect does not control the entire graphics pipeline. Android combines it with geometry, clipping, anti-aliasing, blending and color management. In practice, `RuntimeShader` contributes a function to the final GPU fragment shader.

**In short:** AGSL provides per-fragment color control inside Android's existing rendering pipeline, but it is not a complete 2D or 3D engine.

## RuntimeShader and uniforms

`RuntimeShader` accepts AGSL source code as a string and compiles it when the object is created:

```kotlin
val shader = RuntimeShader(SHADER_SOURCE)
```

Input parameters are declared as `uniform` values. They let an app change the drawing area size, time, animation progress, colors, touch position or sensor values without changing and recompiling the shader source.

```agsl
uniform float2 resolution;
uniform float progress;
layout(color) uniform half4 startColor;
layout(color) uniform half4 endColor;
```

Values are passed through `RuntimeShader` methods:

```kotlin
shader.setFloatUniform("resolution", width, height)
shader.setFloatUniform("progress", progress)
shader.setColorUniform("startColor", startColor.toArgb())
shader.setColorUniform("endColor", endColor.toArgb())
```

Declare color inputs with `layout(color)` and set them through `setColorUniform()`. Android then converts the supplied color into the destination's working color space. When handling transparency manually, the value returned from `main()` must use premultiplied alpha: multiply RGB components by alpha, so no RGB component exceeds alpha.

AGSL also supports a `uniform shader`. The input shader can be evaluated with `eval(coordinate)`, for example to sample a bitmap, gradient or `RenderNode` content and then transform it:

```agsl
uniform shader content;

half4 main(float2 coordinate) {
    half4 color = content.eval(coordinate);
    return color.bgra;
}
```

Unlike typical GLSL texture sampling, a `BitmapShader` evaluated by AGSL uses pixel coordinates by default, from `(0, 0)` to `(width, height)`, rather than normalized coordinates from `0` to `1`.

**In short:** `RuntimeShader` holds compiled AGSL code, while uniforms pass mutable data to it from Kotlin.

## Using AGSL with Jetpack Compose

The examples below use these Compose and Android imports:

```kotlin
import android.graphics.RuntimeShader
import android.os.Build
import androidx.annotation.RequiresApi
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.ShaderBrush
import androidx.compose.ui.graphics.asComposeRenderEffect
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.graphics.toArgb
```

To generate an image in Compose, wrap a `RuntimeShader` in a `ShaderBrush` and use it in `Canvas` or another drawing API.

```kotlin
private const val SHADER_SOURCE = """
    uniform float2 resolution;
    uniform float progress;
    layout(color) uniform half4 startColor;
    layout(color) uniform half4 endColor;

    half4 main(float2 coordinate) {
        float2 uv = coordinate / resolution;
        float wave = 0.5 + 0.5 * sin((uv.x + progress) * 6.28318);
        return mix(startColor, endColor, half(wave));
    }
"""

@RequiresApi(Build.VERSION_CODES.TIRAMISU)
@Composable
fun AgslBackground(
    progress: Float,
    startColor: Color,
    endColor: Color,
    modifier: Modifier = Modifier
) {
    val shader = remember { RuntimeShader(SHADER_SOURCE) }
    val brush = remember(shader) { ShaderBrush(shader) }

    Canvas(modifier = modifier) {
        shader.setFloatUniform("resolution", size.width, size.height)
        shader.setFloatUniform("progress", progress)
        shader.setColorUniform("startColor", startColor.toArgb())
        shader.setColorUniform("endColor", endColor.toArgb())
        drawRect(brush = brush)
    }
}
```

`progress` can come from a Compose animation, touch input or `SensorManager`. During animation, update uniforms rather than creating a new shader source string or `RuntimeShader` for every frame.

When an effect must transform already-rendered composable content and its children, use `RenderEffect.createRuntimeShaderEffect()` and assign the result through `graphicsLayer`:

```kotlin
private const val CONTENT_SHADER_SOURCE = """
    uniform shader content;

    half4 main(float2 coordinate) {
        half4 color = content.eval(coordinate);
        return color.bgra;
    }
"""

@RequiresApi(Build.VERSION_CODES.TIRAMISU)
@Composable
fun AgslContentEffect(
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit
) {
    val shader = remember { RuntimeShader(CONTENT_SHADER_SOURCE) }
    val effect = remember(shader) {
        android.graphics.RenderEffect
            .createRuntimeShaderEffect(shader, "content")
            .asComposeRenderEffect()
    }

    Box(
        modifier = modifier.graphicsLayer {
            renderEffect = effect
        }
    ) {
        content()
    }
}
```

The AGSL source must declare the matching input as `uniform shader content`, and `eval(coordinate)` samples that input shader.

`ShaderBrush` is appropriate when the shader generates pixels for a drawing operation. `RenderEffect` is appropriate when the shader must read and transform already-rendered UI. The latter is usually more expensive, especially across a large area or complex content subtree.

**In short:** use `ShaderBrush` for custom drawing in Compose and `RenderEffect` for post-processing composable content.

## Version support and fallback

`RuntimeShader` and `RenderEffect.createRuntimeShaderEffect()` require Android 13, API 33. Check the platform version before creating or using either object.

```kotlin
@Composable
fun AdaptiveBackground(
    progress: Float,
    modifier: Modifier = Modifier
) {
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        AgslBackground(
            progress = progress,
            startColor = Color(0xFF3157D5),
            endColor = Color(0xFF8E5BD9),
            modifier = modifier
        )
    } else {
        Box(
            modifier = modifier.background(
                Brush.linearGradient(
                    listOf(Color(0xFF3157D5), Color(0xFF8E5BD9))
                )
            )
        )
    }
}
```

The fallback does not need to reproduce the shader effect exactly. It is usually enough to preserve the UI's function, text readability and visual hierarchy. A decorative effect can become a regular gradient, an alpha or scale animation, or be disabled entirely.

**In short:** treat AGSL as progressive enhancement when the app supports devices below API 33.

## AGSL, OpenGL ES and Filament

| Tool | Level | Good fit | Does not provide by itself |
|---|---|---|---|
| AGSL / `RuntimeShader` | Per-fragment effect inside Android 2D rendering | Custom gradients, distortion, color effects, transitions, UI post-processing | Scene, camera, meshes, vertex pipeline |
| OpenGL ES | Low-level graphics API | Custom 2D/3D renderer, textures, geometry, custom GPU pipeline | Ready-made scene and material abstractions |
| Filament | High-level real-time 3D engine | PBR materials, lighting, cameras, glTF models, 3D scenes | Simple integration of a per-pixel UI effect without a 3D scene |

AGSL is sometimes described as Android's equivalent of Metal shaders, but that comparison is incomplete. Metal is a broader graphics and compute API, while AGSL adds programmable per-fragment effects to Android's existing graphics pipeline.

AGSL can mathematically imitate perspective, refraction, waves or surface deformation by changing sampling coordinates. It is still a screen-space or 2D effect: it does not create actual meshes, a depth buffer, a camera or a lit 3D scene.

**In short:** choose AGSL for shader effects inside Android UI, OpenGL ES for a custom low-level renderer and Filament for a complete real-time 3D scene.

## Performance

Shader code runs for a large number of fragments, so even a small function can become expensive on a full-screen surface.

Practical guidelines:

- create and compile `RuntimeShader` once, then update uniforms;
- limit the effect to the smallest necessary area;
- avoid many shader evaluations, complex loops and heavy per-fragment math;
- remember that a `RenderEffect` over an entire subtree is usually more expensive than direct drawing with `ShaderBrush`;
- do not send sensor events to the UI faster than the display refresh rate;
- test the effect on real low-end and mid-range devices;
- measure frame time and jank with Android Studio Profiler, System Trace or Perfetto.

AGSL `for` loops must be bounded so the compiler can unroll them at compile time. For complex effects, carefully control the iteration count and repeated calls to `eval()`.

**In short:** AGSL cost depends on effect area, fragment count, computation complexity and input sample count, so measure it on target devices.

## When to use AGSL

AGSL is a good fit for:

- custom gradients and procedural backgrounds;
- blur-like, glass, ripple and distortion effects;
- touch- or sensor-driven visual responses;
- image color transformations;
- transitions and reveal effects;
- post-processing individual UI components.

Do not choose AGSL when standard Compose animations, `Brush`, `graphicsLayer`, `Canvas` or ordinary image processing solve the task more simply. For actual 3D geometry, cameras, depth and lighting, prefer OpenGL ES, Vulkan or Filament.

**In short:** AGSL is useful when a programmable per-fragment effect is genuinely needed but a complete graphics engine would be excessive.

## See also

- [Android Canvas](canvas.md)
- [OpenGL ES](opengl-es.md)
- [Google Filament](google-filament.md)
- [2D and 3D Rendering](2d-3d-rendering.md)
- [Compose Performance](../compose/performance.md)

## Official resources

- [Android Graphics Shading Language](https://developer.android.com/develop/ui/views/graphics/agsl)
- [Using AGSL in your Android app](https://developer.android.com/develop/ui/views/graphics/agsl/using-agsl)
- [AGSL Quick Reference](https://developer.android.com/develop/ui/views/graphics/agsl/agsl-quick-reference)
- [RuntimeShader API reference](https://developer.android.com/reference/android/graphics/RuntimeShader)
- [Brush: gradients and shaders in Compose](https://developer.android.com/develop/ui/compose/graphics/draw/brush)
