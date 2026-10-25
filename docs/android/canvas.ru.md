# Android Canvas

Android `Canvas` - API для двумерной отрисовки текста, линий, фигур и изображений. Он подходит для собственной графики во `View` или рисования в изменяемый `Bitmap`: например, графиков, звуковых волн, подписей и нестандартных элементов управления.

## Основы Canvas

### `Canvas` и цикл отрисовки

`Canvas` предоставляет команды вроде `drawLine()`, `drawCircle()` и `drawBitmap()`. `Paint` задаёт цвет, стиль, толщину линии и другие параметры. Canvas не хранит объекты сцены: при каждом вызове `onDraw(canvas)` собственная `View` описывает своё текущее изображение заново.

Когда меняется состояние, влияющее на рисунок видимой `View`, вызови `invalidate()` в UI-потоке. Он запланирует отрисовку, но не гарантирует конкретный кадр. Если изменение влияет на измеряемый размер или размещение `View`, вызови `requestLayout()`. Для изменения только цвета или другого параметра рисунка повторное измерение не нужно.

Фазы measure и layout определяют границы `View` до отрисовки. Операции Canvas внутри `View` часто аппаратно ускоряются, но `Canvas(bitmap)` для рисования вне экрана работает программно. Сам API не гарантирует использование GPU.

### `onDraw()` и `Paint`

Создавай переиспользуемые объекты вне `onDraw()`, а внутри оставляй отрисовку текущего состояния:

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

Задай этой `View` размер в разметке. Если нужен собственный размер при `wrap_content`, дополнительно реализуй `onMeasure()`. Для сложной геометрии удобно вычислять параметры, зависящие от размера, в `onSizeChanged()` и использовать их в `onDraw()`.

`Paint` также настраивает обводку, текст, прозрачность, шейдеры и сглаживание. Переиспользуй объект и меняй его свойства вместе с состоянием рисунка либо храни несколько заранее настроенных экземпляров.

### Bitmap и память

`Bitmap` хранит пиксели. Формат `ARGB_8888` использует четыре байта на пиксель, поэтому изображению 2 000 × 2 000 нужно примерно 16 МБ только для пиксельных данных. Декодируй изображение близко к размеру отображения и не удерживай большие bitmap без необходимости. Для списков с изображениями используй библиотеку загрузки, а не декодирование каждого элемента во время отрисовки.

Можно также рисовать вне экрана в изменяемый bitmap:

```kotlin
val bitmap = Bitmap.createBitmap(200, 200, Bitmap.Config.ARGB_8888)
val canvas = Canvas(bitmap)
val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply { color = Color.BLUE }
canvas.drawColor(Color.WHITE)
canvas.drawCircle(100f, 100f, 80f, paint)
```

### Производительность и смежные темы

- Не выполняй ввод-вывод, декодирование bitmap, тяжёлые вычисления и лишние выделения памяти внутри `onDraw()`.
- Переиспользуй `Paint`, контуры, разметку текста и геометрию, пока их входные данные не изменились.
- Избегай лишних перерисовок, повторных проходов layout, наложения слоёв и дорогих операций обрезки или теней; оптимизируй по результатам профилирования.
- Подготавливай тяжёлые данные вне пути отрисовки, а готовый результат рисуй в UI-потоке.

Для программируемых пиксельных эффектов внутри Android UI смотри [AGSL и `RuntimeShader`](agsl-runtime-shader.md). Для собственного 3D-рендеринга смотри [OpenGL ES](opengl-es.md) и [Google Filament](google-filament.md).
