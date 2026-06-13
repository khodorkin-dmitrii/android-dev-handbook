# Android Canvas

Android Canvas - низкоуровневый 2D drawing API для рисования текста, линий, фигур, bitmap и custom graphics внутри `View` или bitmap-backed surfaces.

## Canvas basics

### Что это такое

`Canvas` - объект, через который Android даёт API для drawing commands: `drawLine()`, `drawRect()`, `drawCircle()`, `drawText()`, `drawBitmap()` и другие операции.

Обычно `Canvas` используют внутри custom `View`, переопределяя `onDraw(canvas: Canvas)`. Код описывает, что нужно нарисовать в текущем frame, а Android выполняет drawing в рамках rendering pipeline.

Canvas хорошо подходит для custom 2D UI: charts, progress indicators, simple games, signatures, waveform, badges, декоративные элементы, custom controls.

**Важно:** `Canvas` - это immediate-style API: ты вызываешь команды рисования каждый раз, когда `View` нужно перерисовать. Он не хранит "объекты сцены" сам по себе.

**Коротко:** Android Canvas - это 2D drawing API для custom rendering, когда стандартных `View` или composable недостаточно.

### Как работает rendering pipeline

Для обычной `View` pipeline начинается с invalidation. Когда `View` нужно обновить визуально, вызывают `invalidate()`, и Android планирует redraw в ближайшем frame.

Дальше UI проходит основные фазы: measure, layout и draw. Measure определяет размеры, layout размещает элементы, draw вызывает отрисовку. Для custom drawing ключевая точка - `onDraw()`.

На современных Android-устройствах многие drawing operations аппаратно ускоряются через GPU, но Canvas API всё равно остаётся 2D abstraction. Некоторые операции могут быть дороже других: сложные paths, shadows, clipping, text layout, large bitmaps и частые allocations.

Если изменился только внешний вид, обычно достаточно `invalidate()`. Если изменился размер или layout-affecting state, нужен `requestLayout()`.

**Коротко:** Canvas drawing выполняется в draw phase; `invalidate()` просит перерисовать `View`, а `requestLayout()` нужен только при изменении размеров или размещения.

### `onDraw()`

`onDraw()` - callback custom `View`, в котором выполняются drawing commands.

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

`onDraw()` может вызываться часто, поэтому он должен быть быстрым. Не стоит создавать `Paint`, `Path`, `Rect`, formatter, bitmap или другие объекты внутри `onDraw()` на каждый frame.

Если drawing зависит от размера `View`, часто удобно подготовить размеры в `onSizeChanged()`, а в `onDraw()` только рисовать.

**Коротко:** `onDraw()` должен описывать отрисовку текущего состояния и не выполнять тяжёлую подготовку данных.

### `Paint`

`Paint` описывает, как рисовать: цвет, стиль, stroke width, text size, alpha, shader, typeface, anti-aliasing и другие параметры.

Один и тот же `Canvas` command может выглядеть по-разному в зависимости от `Paint`. Например, `drawCircle()` может нарисовать заполненный круг, stroke outline или полупрозрачную фигуру.

```kotlin
private val strokePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
    color = Color.RED
    style = Paint.Style.STROKE
    strokeWidth = 6f
}
```

`Paint` лучше создавать один раз и переиспользовать. Если нужно менять параметры по state, меняй существующий объект или держи несколько заранее подготовленных instances.

**Коротко:** `Paint` - это набор настроек drawing operation: цвет, стиль, stroke, text, alpha и сглаживание.

### `Bitmap`

`Bitmap` - raster image в памяти. В Canvas его можно рисовать через `drawBitmap()`, использовать как offscreen buffer или результат генерации изображения.

Bitmap может занимать много памяти: размер зависит от width, height и pixel format. Например, `ARGB_8888` обычно занимает 4 байта на pixel.

Для Android важно декодировать изображения под нужный размер, не держать большие bitmap дольше необходимого и учитывать lifecycle. В списках лучше использовать image loading libraries вроде Coil/Glide, а не ручную загрузку bitmap в каждом item.

Canvas также может рисовать в bitmap:

```kotlin
val bitmap = Bitmap.createBitmap(200, 200, Bitmap.Config.ARGB_8888)
val canvas = Canvas(bitmap)
canvas.drawColor(Color.WHITE)
canvas.drawCircle(100f, 100f, 80f, paint)
```

**Коротко:** `Bitmap` - это пиксельные данные в памяти; с ним нужно аккуратно обращаться из-за memory cost.

### Производительность

Главные правила Canvas performance:

- не создавать объекты в `onDraw()`;
- не выполнять I/O, decode bitmap или сложные вычисления в drawing path;
- кэшировать `Paint`, `Path`, `Rect`, text layout и precomputed geometry;
- не вызывать `requestLayout()`, если достаточно `invalidate()`;
- минимизировать overdraw и сложные clipping/shadow operations;
- подготавливать heavy data вне main thread, а рисовать уже готовый результат.

Если custom drawing становится слишком сложным, а экран требует много объектов, анимаций или 3D, стоит рассмотреть OpenGL ES, Filament или Compose Canvas/graphics APIs в зависимости от задачи.

**Коротко:** Canvas быстрый для умеренного 2D drawing, но его легко замедлить allocations, heavy calculations и большими bitmap на main thread.
