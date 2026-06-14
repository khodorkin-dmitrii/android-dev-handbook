# Android Canvas

Android Canvas - a low-level 2D drawing API for drawing text, lines, shapes, bitmaps and custom graphics inside a `View` or bitmap-backed surfaces.

## Canvas basics

### What it is

`Canvas` - an object through which Android provides an API for drawing commands: `drawLine()`, `drawRect()`, `drawCircle()`, `drawText()`, `drawBitmap()` and other operations.

`Canvas` is usually used inside a custom `View` by overriding `onDraw(canvas: Canvas)`. The code describes what should be drawn in the current frame, and Android performs drawing as part of the rendering pipeline.

Canvas works well for custom 2D UI: charts, progress indicators, simple games, signatures, waveform, badges, decorative elements and custom controls.

**Important:** `Canvas` is an immediate-style API: you call drawing commands every time the `View` needs to be redrawn. It does not store "scene objects" by itself.

**In short:** Android Canvas is a 2D drawing API for custom rendering when standard `View`s or composables are not enough.

### How the rendering pipeline works

For a regular `View`, the pipeline starts with invalidation. When a `View` needs a visual update, `invalidate()` is called, and Android schedules a redraw for the next frame.

Then UI goes through the main phases: measure, layout and draw. Measure determines sizes, layout places elements, and draw performs rendering. For custom drawing, the key point is `onDraw()`.

On modern Android devices, many drawing operations are hardware-accelerated through the GPU, but the Canvas API remains a 2D abstraction. Some operations may be more expensive than others: complex paths, shadows, clipping, text layout, large bitmaps and frequent allocations.

If only appearance changed, `invalidate()` is usually enough. If size or layout-affecting state changed, `requestLayout()` is needed.

**In short:** Canvas drawing runs in the draw phase; `invalidate()` asks to redraw the `View`, while `requestLayout()` is needed only when size or placement changes.

### `onDraw()`

`onDraw()` - a custom `View` callback where drawing commands are executed.

```kotlin
class CircleView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.BLUE
        style = Paint.Style.FILL
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        val radius = min(width, height) / 2f
        canvas.drawCircle(width / 2f, height / 2f, radius, paint)
    }
}
```

`onDraw()` can be called often, so it must be fast. Do not create `Paint`, `Path`, `Rect`, formatter, bitmap or other objects inside `onDraw()` on every frame.

If drawing depends on `View` size, it is often convenient to prepare dimensions in `onSizeChanged()` and only draw in `onDraw()`.

**In short:** `onDraw()` should describe rendering of the current state and should not perform heavy data preparation.

### `Paint`

`Paint` describes how to draw: color, style, stroke width, text size, alpha, shader, typeface, anti-aliasing and other parameters.

The same `Canvas` command can look different depending on `Paint`. For example, `drawCircle()` can draw a filled circle, a stroke outline or a translucent shape.

```kotlin
private val strokePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
    color = Color.RED
    style = Paint.Style.STROKE
    strokeWidth = 6f
}
```

It is better to create `Paint` once and reuse it. If parameters need to change by state, mutate the existing object or keep several preconfigured instances.

**In short:** `Paint` is a set of drawing operation settings: color, style, stroke, text, alpha and anti-aliasing.

### `Bitmap`

`Bitmap` - a raster image in memory. In Canvas, it can be drawn through `drawBitmap()`, used as an offscreen buffer or used as the result of image generation.

Bitmap can take a lot of memory: size depends on width, height and pixel format. For example, `ARGB_8888` usually takes 4 bytes per pixel.

On Android, it is important to decode images to the required size, avoid keeping large bitmaps longer than necessary and account for lifecycle. In lists, prefer image loading libraries such as Coil/Glide instead of manually loading a bitmap in every item.

Canvas can also draw into a bitmap:

```kotlin
val bitmap = Bitmap.createBitmap(200, 200, Bitmap.Config.ARGB_8888)
val canvas = Canvas(bitmap)
canvas.drawColor(Color.WHITE)
canvas.drawCircle(100f, 100f, 80f, paint)
```

**In short:** `Bitmap` is pixel data in memory; handle it carefully because of memory cost.

### Performance

Main Canvas performance rules:

- do not create objects in `onDraw()`;
- do not perform I/O, bitmap decoding or complex calculations in the drawing path;
- cache `Paint`, `Path`, `Rect`, text layout and precomputed geometry;
- do not call `requestLayout()` when `invalidate()` is enough;
- minimize overdraw and complex clipping/shadow operations;
- prepare heavy data outside the main thread and draw an already prepared result.

If custom drawing becomes too complex and the screen needs many objects, animations or 3D, consider OpenGL ES, Filament or Compose Canvas/graphics APIs depending on the task.

**In short:** Canvas is fast for moderate 2D drawing, but it is easy to slow it down with allocations, heavy calculations and large bitmaps on the main thread.
