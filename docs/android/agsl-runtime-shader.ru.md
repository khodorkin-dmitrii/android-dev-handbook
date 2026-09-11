# AGSL и RuntimeShader

Android Graphics Shading Language (AGSL) позволяет описывать программируемые визуальные эффекты, которые Android включает в свой 2D graphics pipeline. Через `RuntimeShader` такой код можно использовать для custom drawing, градиентов, искажений, переходов и фильтрации уже отрисованного UI.

AGSL появился в Android 13, поэтому `RuntimeShader` доступен начиная с API 33.

## Что такое AGSL

AGSL - C-подобный shading language, во многом совместимый с GLSL ES 1.0. Код шейдера выполняется для каждого рисуемого fragment и возвращает его цвет.

```agsl
half4 main(float2 coordinate) {
    return half4(0.2, 0.5, 1.0, 1.0);
}
```

Параметр `coordinate` содержит локальные координаты внутри `Canvas` или `RenderNode`. По умолчанию значения задаются в pixels, начало координат находится в левом верхнем углу, `x` растёт вправо, а `y` - вниз.

В отличие от отдельной OpenGL-программы, AGSL-эффект не управляет всем graphics pipeline. Android объединяет его с логикой geometry, clipping, anti-aliasing, blending и color management. `RuntimeShader` фактически добавляет функцию в итоговый GPU fragment shader.

**Коротко:** AGSL даёт per-fragment контроль над цветом внутри существующего Android rendering pipeline, но не является полноценным 2D/3D engine.

## RuntimeShader и uniforms

`RuntimeShader` принимает AGSL source code в виде строки и компилирует его при создании объекта:

```kotlin
val shader = RuntimeShader(SHADER_SOURCE)
```

Входные параметры объявляются через `uniform`. Они позволяют менять размер области, время, progress анимации, цвета, положение касания или значения датчиков без изменения и повторной компиляции shader source.

```agsl
uniform float2 resolution;
uniform float progress;
layout(color) uniform half4 startColor;
layout(color) uniform half4 endColor;
```

Значения передаются через методы `RuntimeShader`:

```kotlin
shader.setFloatUniform("resolution", width, height)
shader.setFloatUniform("progress", progress)
shader.setColorUniform("startColor", startColor.toArgb())
shader.setColorUniform("endColor", endColor.toArgb())
```

Для цветов стоит использовать `layout(color)` и `setColorUniform()`. Тогда Android преобразует переданный цвет в working color space назначения. При ручной работе с прозрачностью результат `main()` должен использовать premultiplied alpha: RGB-компоненты нужно умножить на alpha, поэтому ни одна из них не должна быть больше alpha.

AGSL также поддерживает `uniform shader`. Такой input можно вычислить через `eval(coordinate)`, например чтобы прочитать bitmap, gradient или содержимое `RenderNode` и затем изменить его:

```agsl
uniform shader content;

half4 main(float2 coordinate) {
    half4 color = content.eval(coordinate);
    return color.bgra;
}
```

В отличие от обычного GLSL texture sampling, координаты `BitmapShader` в AGSL по умолчанию задаются в pixels: от `(0, 0)` до `(width, height)`, а не в нормализованном диапазоне от `0` до `1`.

**Коротко:** `RuntimeShader` хранит скомпилированный AGSL-код, а uniforms передают в него изменяемые данные из Kotlin.

## Использование с Jetpack Compose

В примерах ниже используются следующие Compose и Android imports:

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

Для генерации изображения внутри Compose `RuntimeShader` можно обернуть в `ShaderBrush` и использовать в `Canvas` или других drawing APIs.

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

`progress` может поступать из Compose animation, touch input или `SensorManager`. Во время анимации нужно менять uniforms, а не создавать новую строку shader source или новый `RuntimeShader` для каждого frame.

Если эффект должен изменять уже отрисованное содержимое composable и его дочерних элементов, можно использовать `RenderEffect.createRuntimeShaderEffect()` и назначить результат через `graphicsLayer`:

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

В AGSL-коде должен быть объявлен соответствующий input `uniform shader content`, а `eval(coordinate)` читает этот input shader.

`ShaderBrush` подходит, когда shader сам генерирует pixels для drawing operation. `RenderEffect` нужен, когда shader должен читать и преобразовывать уже отрисованный UI. Второй вариант обычно дороже, особенно для большой области и сложного дерева содержимого.

**Коротко:** в Compose используй `ShaderBrush` для custom drawing и `RenderEffect` для post-processing содержимого composable.

## Поддержка версий и fallback

`RuntimeShader` и `RenderEffect.createRuntimeShaderEffect()` требуют Android 13, API 33. Проверка версии должна находиться до создания или использования этих объектов.

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

Fallback не обязан визуально повторять shader effect. Обычно достаточно сохранить функцию UI, читаемость текста и общий visual hierarchy. Декоративный эффект можно заменить обычным gradient, alpha/scale animation или полностью отключить.

**Коротко:** AGSL нужно считать progressive enhancement, если приложение поддерживает устройства ниже API 33.

## AGSL, OpenGL ES и Filament

| Инструмент | Уровень | Хорошо подходит для | Не предоставляет сам по себе |
|---|---|---|---|
| AGSL / `RuntimeShader` | Per-fragment effect внутри Android 2D rendering | Custom gradients, distortion, color effects, transitions, UI post-processing | Scene, camera, meshes, vertex pipeline |
| OpenGL ES | Low-level graphics API | Собственный 2D/3D renderer, textures, geometry, custom GPU pipeline | Готовую scene/material abstraction |
| Filament | High-level real-time 3D engine | PBR materials, lighting, cameras, glTF models, 3D scenes | Простую интеграцию per-pixel UI effect без 3D scene |

AGSL иногда называют Android-аналогом Metal shaders, но это неточное сравнение. Metal - более широкий graphics and compute API, тогда как AGSL добавляет programmable per-fragment effects в существующий Android graphics pipeline.

AGSL может математически имитировать perspective, refraction, waves или surface deformation, изменяя координаты sampling. Однако это всё ещё screen-space или 2D effect: он не создаёт настоящие meshes, depth buffer, camera или освещённую 3D scene.

**Коротко:** выбирай AGSL для shader effects внутри Android UI, OpenGL ES для собственного low-level renderer и Filament для полноценной real-time 3D scene.

## Производительность

Shader code выполняется для большого количества fragments, поэтому небольшая функция может стать дорогой на full-screen поверхности.

Практические правила:

- создавай и компилируй `RuntimeShader` один раз, затем обновляй uniforms;
- ограничивай effect минимально необходимой областью;
- избегай большого количества shader evaluations, сложных циклов и тяжёлой математики для каждого fragment;
- помни, что `RenderEffect` над целым subtree обычно дороже прямого drawing через `ShaderBrush`;
- не передавай sensor events в UI с частотой выше частоты обновления экрана;
- проверяй эффект на реальных low-end и mid-range устройствах;
- измеряй frame time и jank через Android Studio Profiler, System Trace или Perfetto.

Для AGSL `for` loops должны быть ограничены так, чтобы compiler мог развернуть их на этапе компиляции. Для сложных эффектов особенно важно контролировать количество итераций и повторных вызовов `eval()`.

**Коротко:** стоимость AGSL определяется размером области, количеством fragments, сложностью вычислений и числом input samples - её нужно измерять на целевых устройствах.

## Когда использовать AGSL

AGSL хорошо подходит для:

- custom gradients и procedural backgrounds;
- blur-like, glass, ripple и distortion effects;
- touch- или sensor-driven визуальных реакций;
- image color transformations;
- transitions и reveal effects;
- post-processing отдельных UI-компонентов.

AGSL не стоит выбирать, если задачу проще решить стандартными Compose animations, `Brush`, `graphicsLayer`, `Canvas` или обычным image processing. Для настоящей 3D geometry, camera, depth и lighting лучше использовать OpenGL ES, Vulkan или Filament.

**Коротко:** AGSL полезен, когда действительно нужен programmable per-fragment effect, но полный graphics engine был бы избыточен.

## Связанные темы

- [Android Canvas](canvas.md)
- [OpenGL ES](opengl-es.md)
- [Google Filament](google-filament.md)
- [2D и 3D Rendering](2d-3d-rendering.md)
- [Compose Performance](../compose/performance.md)

## Официальные материалы

- [Android Graphics Shading Language](https://developer.android.com/develop/ui/views/graphics/agsl)
- [Using AGSL in your Android app](https://developer.android.com/develop/ui/views/graphics/agsl/using-agsl)
- [AGSL Quick Reference](https://developer.android.com/develop/ui/views/graphics/agsl/agsl-quick-reference)
- [RuntimeShader API reference](https://developer.android.com/reference/android/graphics/RuntimeShader)
- [Brush: gradients and shaders in Compose](https://developer.android.com/develop/ui/compose/graphics/draw/brush)
