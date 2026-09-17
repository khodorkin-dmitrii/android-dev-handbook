# ML Kit на Android

ML Kit предоставляет высокоуровневые machine learning API для мобильных приложений. Это хороший вариант по умолчанию, если готовый API уже решает задачу: приложение работает с привычными Android-объектами и не управляет напрямую tensors, операторами модели и hardware delegates.

Большинство операций ML Kit выполняется на устройстве. Это позволяет работать offline, уменьшает latency и поддерживает real-time сценарии с камерой, сохраняя чувствительные исходные данные локально.

## Доступные возможности

API ML Kit можно разделить на несколько групп:

- computer vision: распознавание текста, сканирование штрихкодов, распознавание лиц, image labeling, object detection и tracking, pose detection, segmentation и сканирование документов;
- natural language: определение языка, перевод, smart reply и entity extraction;
- generative AI на поддерживаемых устройствах: API для суммаризации, proofreading, rewriting, описания изображений, распознавания речи и prompting.

Доступность, lifecycle status, поддерживаемые языки и требования к устройству отличаются для каждого API. Перед проектированием фичи проверьте документацию конкретного решения.

## ML Kit или LiteRT?

Выбирайте ML Kit, если:

- поддерживаемый API соответствует задаче;
- нужна готовая production-модель и pipeline обработки;
- команда должна сосредоточиться на поведении фичи, а не интеграции модели;
- достаточно Android-friendly объектов результата.

Выбирайте [LiteRT](litert.md), если:

- приложение должно запускать собственную `.tflite`-модель;
- preprocessing и postprocessing входят в контракт custom model;
- нужен прямой контроль над входными и выходными tensors или acceleration;
- модель, результат или доступные сценарии ML Kit не соответствуют требованиям.

Некоторые API ML Kit поддерживают custom models. Стоит оценить этот вариант до реализации всего pipeline на более низком уровне.

## Зависимость и доставка модели

Конкретный artifact зависит от выбранного API. Для некоторых возможностей ML Kit есть два варианта доставки:

- **bundled model** входит в приложение, доступна сразу после установки и увеличивает его размер;
- **модель через Google Play services** уменьшает начальный размер приложения, но перед первым успешным использованием может потребовать загрузку.

Например, для распознавания текста на латинице используются разные artifacts:

```kotlin
dependencies {
    // Модель включена в приложение
    implementation("com.google.mlkit:text-recognition:16.0.1")

    // Или модель доставляется через Google Play services
    // implementation("com.google.android.gms:play-services-mlkit-text-recognition:19.0.1")
}
```

Указанные версии были актуальны на момент ревью статьи. Перед добавлением зависимости проверьте их в официальной документации. Не подключайте оба варианта одного detector, если это явно не требуется фиче.

Если первый запуск не может ждать загрузки, используйте bundled model или настройте загрузку во время установки там, где API это поддерживает. Product flow всё равно должен обрабатывать unavailable и failed states.

## Пример распознавания текста

Создавайте и переиспользуйте recognizer, а не конструируйте его для каждого кадра:

```kotlin
class TextRecognitionDataSource : Closeable {
    private val recognizer = TextRecognition.getClient(
        TextRecognizerOptions.DEFAULT_OPTIONS
    )

    suspend fun recognize(bitmap: Bitmap): String {
        val image = InputImage.fromBitmap(bitmap, 0)
        return recognizer.process(image).await().text
    }

    override fun close() {
        recognizer.close()
    }
}
```

`await()` предоставляет `kotlinx-coroutines-play-services`. Без этого adapter обработайте возвращаемый `Task` через listeners, сохранив корректное поведение cancellation и lifecycle.

Жизненный цикл data source должен быть задан явно, например scope экрана или dependency injection. Освобождайте clients с методом `close()` при уничтожении владельца.

## Интеграция с CameraX

При анализе кадров камеры нужно учитывать rotation, backpressure и время жизни ресурсов:

```kotlin
fun analyze(
    imageProxy: ImageProxy,
    recognizer: TextRecognizer,
    onResult: (String) -> Unit,
    onError: (Throwable) -> Unit,
) {
    val mediaImage = imageProxy.image
    if (mediaImage == null) {
        imageProxy.close()
        return
    }

    val image = InputImage.fromMediaImage(
        mediaImage,
        imageProxy.imageInfo.rotationDegrees,
    )

    recognizer.process(image)
        .addOnSuccessListener { result -> onResult(result.text) }
        .addOnFailureListener(onError)
        .addOnCompleteListener { imageProxy.close() }
}
```

Основные правила:

- закрывайте каждый `ImageProxy`, включая ошибки и ранний выход;
- передавайте rotation кадра, полученный от CameraX;
- для многих real-time сценариев используйте `ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST`;
- не запускайте несколько detector invocations параллельно, если API и сама фича на это не рассчитаны;
- уменьшайте разрешение или обрезайте вход только после оценки влияния на accuracy.

## Состояние и обработка ошибок

Представляйте фичу через явные состояния, а не nullable result:

```kotlin
sealed interface RecognitionState {
    data object Idle : RecognitionState
    data object Preparing : RecognitionState
    data class Ready(val text: String) : RecognitionState
    data class Failed(val cause: Throwable) : RecognitionState
}
```

Различайте пустой, но корректный результат, отсутствующую или загружаемую модель, неподдерживаемый ввод, cancellation и настоящую ошибку обработки. Отсутствие распознаваемого объекта в очередном кадре камеры не должно каждый раз показываться как ошибка.

## Производительность и lifecycle

- Инициализируйте detector clients один раз и переиспользуйте их.
- Выполняйте обработку вне UI rendering и не блокируйте main thread ожиданием результата.
- Ограничивайте частоту непрерывного ввода и отбрасывайте устаревший результат, если его уже заменил новый кадр.
- Не храните исходные изображения в долгоживущем state без необходимости.
- Измеряйте cold start отдельно от steady-state latency: инициализация или загрузка модели может определять время первого запроса.
- Проверяйте работу на менее производительных устройствах и с реалистичным разрешением камеры.

## Приватность

On-device processing не делает автоматически приватной всю фичу. Приложение всё ещё может отправлять изображения, analytics, распознанный текст или crash diagnostics. Зафиксируйте каждый путь данных и не записывайте пользовательский контент в логи.

Если результат затем отправляется на backend или в cloud model, явно обозначьте эту границу в product flow и примените правила приложения для consent, хранения и безопасности.

## Тестирование

Скройте ML Kit client за небольшим интерфейсом, чтобы ViewModel и use cases можно было тестировать с детерминированными fakes:

```kotlin
fun interface TextRecognizerGateway {
    suspend fun recognize(bitmap: Bitmap): String
}
```

Для настоящего client используйте integration tests с отобранным набором изображений. Включите rotation, размытие, слабое освещение, частично видимый контент, поддерживаемые системы письма, пустой ввод и минимальный размер изображения для продукта. Не проверяйте нестабильную полную строку OCR, если достаточно меньшего invariant.

## Частые ошибки

- Detector создаётся заново для каждого кадра.
- `ImageProxy` или closeable ML Kit client не закрывается.
- Код предполагает, что модель уже загружена.
- Каждый кадр камеры ставится в неограниченную очередь.
- UI получает устаревший результат после смены экрана или входных данных.
- Вероятностный результат воспринимается как гарантированный факт.
- Изображения или распознанный пользовательский контент попадают в логи.

## См. также

- [AI на Android](overview.md)
- [Документация ML Kit](https://developers.google.com/ml-kit)
- [Распознавание текста на Android](https://developers.google.com/ml-kit/vision/text-recognition/v2/android)
- [CameraX image analysis](https://developer.android.com/media/camera/camerax/analyze)
