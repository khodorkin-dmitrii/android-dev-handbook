# Android Canvas

Android `Canvas` is a 2D drawing API for text, lines, shapes and bitmaps. Use it for custom graphics in a `View` or for drawing into a mutable `Bitmap`: charts, waveforms, signatures and custom controls are common examples.

## Canvas basics

### `Canvas` and the drawing lifecycle

`Canvas` supplies drawing commands such as `drawLine()`, `drawCircle()` and `drawBitmap()`. `Paint` supplies their color, style, stroke width and other settings. Canvas does not retain scene objects; a custom `View` describes its current appearance whenever `onDraw(canvas)` is called.

For a visible `View`, call `invalidate()` on the UI thread after drawing state changes. It schedules a future draw, but does not promise a particular frame. Call `requestLayout()` when a change affects the view's measured size or placement. Avoid requesting layout for a color or other draw-only change.

Measure and layout determine the view's bounds before drawing. Hardware acceleration often handles a `View`'s Canvas operations, but an offscreen `Canvas(bitmap)` is software-backed. The API alone does not guarantee GPU rendering.

### `onDraw()` and `Paint`

Create reusable drawing objects outside `onDraw()` and keep the callback focused on drawing the current state:

```kotlin
class CircleView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private val circlePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.BLUE
        style = Paint.Style.FILL
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        val centerX = (paddingLeft + width - paddingRight) / 2f
        val centerY = (paddingTop + height - paddingBottom) / 2f
        val radius = minOf(
            width - paddingLeft - paddingRight,
            height - paddingTop - paddingBottom
        ).coerceAtLeast(0) / 2f
        canvas.drawCircle(centerX, centerY, radius, circlePaint)
    }
}
```

Give this view a size in its layout. If it must support `wrap_content` with an intrinsic size, implement `onMeasure()` as well. For more complex geometry, calculate size-dependent values in `onSizeChanged()` and reuse them in `onDraw()`.

`Paint` can also configure strokes, text, alpha, shaders and anti-aliasing. Reuse an instance and update its properties when the drawing state changes, or keep a few preconfigured instances.

### Bitmaps and memory

A `Bitmap` stores pixels. `ARGB_8888` uses four bytes per pixel for its pixel data, so a 2,000 × 2,000 bitmap needs roughly 16 MB before other overhead. Decode images near the size they will be displayed and avoid retaining large bitmaps unnecessarily. For image-heavy lists, use an image loading library rather than decoding each item during drawing.

You can also draw offscreen into a mutable bitmap:

```kotlin
val bitmap = Bitmap.createBitmap(200, 200, Bitmap.Config.ARGB_8888)
val canvas = Canvas(bitmap)
val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply { color = Color.BLUE }
canvas.drawColor(Color.WHITE)
canvas.drawCircle(100f, 100f, 80f, paint)
```

### Performance and related topics

- Keep I/O, bitmap decoding, expensive calculations and avoidable allocations out of `onDraw()`.
- Reuse `Paint`, paths, text layout and geometry when their inputs have not changed.
- Avoid unnecessary invalidation, layout passes, overdraw and costly clipping or shadows; profile before optimizing.
- Prepare expensive data outside the drawing path, then draw the ready result on the UI thread.

For programmable pixel effects within Android UI, see [AGSL and `RuntimeShader`](agsl-runtime-shader.md). For a custom 3D rendering pipeline, see [OpenGL ES](opengl-es.md) and [Google Filament](google-filament.md).
