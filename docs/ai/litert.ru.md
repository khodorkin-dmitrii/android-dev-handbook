# LiteRT на Android

LiteRT - on-device runtime Google для выполнения machine learning models. Это современное название технологии, ранее известной как TensorFlow Lite, при этом `.tflite` остаётся форматом файла модели.

Используйте LiteRT, когда Android-приложение должно запускать собственную или стороннюю модель и команде нужен контроль над всем inference pipeline: доставкой модели, preprocessing, tensors, выполнением, postprocessing и производительностью.

## Когда подходит LiteRT

LiteRT подходит, если:

- частью продукта является custom `.tflite` model;
- готовый API [ML Kit](ml-kit.md) не покрывает задачу;
- inference должен работать offline или оставлять исходные данные на устройстве;
- требования к latency предполагают локальное выполнение;
- команда готова отвечать за совместимость модели и проверку на разных устройствах.

LiteRT не предназначен для обучения модели внутри Android-приложения. Обычно модель обучается или получается отдельно, при необходимости конвертируется и оптимизируется, а затем включается в приложение или доставляется на устройство для inference.

## Inference pipeline

Рабочий файл модели - только одна часть фичи:

```text
Входные данные приложения
            |
            v
Decode, resize, normalize, tokenize
            |
            v
     Input tensor или buffer
            |
            v
       Выполнение LiteRT
            |
            v
     Output tensor или buffer
            |
            v
Decode, threshold, сопоставление labels
            |
            v
       Доменный результат
```

Preprocessing и postprocessing входят в контракт модели. Неверный порядок каналов, dimensions, normalization, tokenization, quantization parameters или label mapping могут дать правдоподобный, но неправильный результат без исключения.

Храните описание контракта рядом с моделью: имена, shapes и data types tensors, диапазоны значений, color space, версию labels и правила интерпретации результата.

## Runtime API для Android

LiteRT предоставляет два основных направления Android API:

- **`CompiledModel` API** - современный high-performance API, упрощающий acceleration на CPU, GPU и NPU.
- **`Interpreter` API** - базовый API, сохранённый для обратной совместимости и существующих интеграций.

Для новой интеграции выбирайте `CompiledModel`, если его требования к устройствам и фиче совместимы с приложением. Не переносите стабильную реализацию с `Interpreter` только ради нового названия: сравните матрицу устройств, поддерживаемые operators и delegates, производительность, binary size и стоимость миграции.

API и поддерживаемые версии Android развиваются. Выбирайте версию runtime по актуальной compatibility table официальной документации, а не копируйте номер из старого примера.

## Зависимость и asset модели

Для современного runtime добавьте актуальный artifact LiteRT:

```kotlin
dependencies {
    implementation("com.google.ai.edge.litert:litert:2.2.0")
}
```

Эта версия была актуальна на момент ревью статьи. Перед подключением проверьте Android compatibility table, поскольку требования runtime и minimum SDK меняются.

Если модель должна поставляться вместе с приложением, поместите её в `src/main/assets/`:

```text
app/src/main/assets/models/image_classifier.tflite
```

Так модель сразу доступна offline, но увеличивает размер загрузки, а её обновление связано с release приложения. Remote delivery позволяет обновлять модель независимо, но требует integrity checks, versioning, rollback, управления хранилищем и состояний unavailable или downloading.

## Минимальный flow с `CompiledModel`

Современный API создаёт compiled model для выбранного accelerator, заранее выделяет buffers, выполняет inference и читает результат:

```kotlin
val compiledModel = CompiledModel.create(
    modelPath,
    CompiledModel.Options(Accelerator.CPU),
)

val inputBuffers = compiledModel.createInputBuffers()
val outputBuffers = compiledModel.createOutputBuffers()

inputBuffers[0].writeFloat(inputValues)
compiledModel.run(inputBuffers, outputBuffers)

val outputValues = outputBuffers[0].readFloat()
```

`modelPath` должен указывать на location, поддерживаемый выбранным API. Если API требует filesystem path, перед созданием модели скопируйте packaged asset в приватный файл приложения. Делайте это один раз для версии модели, а не перед каждым inference.

Пример показывает механику runtime, но не полную реализацию classifier. Настоящий код должен проверить shapes и types tensors, выполнить точный preprocessing contract, интерпретировать результат, освободить runtime resources в соответствии с lifecycle API и обработать ошибки инициализации.

## Инкапсуляция runtime

Типы LiteRT не должны попадать во ViewModel и UI:

```kotlin
interface ImageClassifier {
    suspend fun classify(bitmap: Bitmap): List<Classification>
}

data class Classification(
    val label: String,
    val confidence: Float,
)
```

Реализация может владеть compiled model, переиспользуемыми buffers, label mapping и preprocessing. Создавайте её в scope, допускающем фоновую работу, и используйте для многих запросов. Сериализуйте доступ, если выбранный runtime object и стратегия buffers явно не гарантируют безопасные параллельные вызовы.

## Preprocessing и postprocessing

Для модели, работающей с изображениями, preprocessing может включать:

- применение EXIF или camera rotation;
- crop в соответствии с требованиями продукта;
- resize тем же способом, который использовался при обучении;
- преобразование RGB channels в ожидаемые type и range;
- применение normalization или quantization parameters;
- запись значений в требуемом tensor order.

Postprocessing может включать softmax, non-maximum suppression, thresholding, label lookup, преобразование координат или ranking. Не добавляйте преобразование только потому, что оно часто встречается. Необходимость определяет контракт модели. Например, некоторые модели уже содержат операцию softmax.

Оставляйте эти преобразования детерминированными и тестируйте отдельно от runtime.

## Acceleration

Hardware acceleration не гарантирует ускорение любой модели на любом устройстве.

- CPU обладает широкой совместимостью и подходит как baseline.
- GPU может увеличить throughput совместимых workloads, но добавляет расходы на инициализацию и передачу данных.
- Доступность NPU и поддержка operators зависят от устройства и выбранного runtime path.

Измеряйте полную фичу вместе с preprocessing и postprocessing на репрезентативной матрице устройств. Проверяйте cold initialization, warm latency, sustained throughput, память, батарею и thermal behavior. Delegate может ускорять отдельный inference, но проигрывать для короткоживущей фичи из-за стоимости инициализации.

Задайте fallback на совместимый accelerator или сообщайте о недоступности фичи. Ошибка настройки acceleration не должна незаметно приводить к семантически другому результату.

## Quantization и размер модели

Quantization может уменьшить размер модели и использование памяти, а иногда ускорить выполнение, но способна повлиять на accuracy. Приложение должно использовать data type, scale и zero-point, ожидаемые quantized tensor.

Оценивайте размер, latency и качество на целевой задаче вместе. Меньшая модель полезна только в том случае, если результат всё ещё соответствует продуктовому порогу на репрезентативных данных.

## Threading, lifecycle и streams

- Инициализируйте runtime вне чувствительной к latency UI-работы.
- Не выполняйте synchronous inference на main thread.
- Переиспользуйте модель и buffers там, где это поддерживается, чтобы уменьшить allocations.
- Задайте владельцу runtime явный lifecycle и освобождайте native resources.
- Для camera и audio streams используйте ограниченный backpressure и отбрасывайте устаревший input.
- Не позволяйте устаревшему результату перезаписать state для более новых данных.
- Явно определите, сериализуются, отменяются или обрабатываются ограниченным worker pool входящие запросы.

Для разового действия пользователя показывайте подготовку отдельно, если инициализация модели заметна. Для непрерывного анализа по возможности прогрейте runtime до приёма кадров.

## Доставка и versioning модели

Рассматривайте модель и metadata как единый версионируемый набор. Полезный manifest содержит:

- версию и checksum модели;
- требуемую версию runtime;
- контракт input и output;
- версию labels или tokenizer;
- минимальную поддерживаемую версию приложения;
- quality metrics и rollout status.

Remote model загружайте в приватное хранилище приложения, проверяйте integrity до активации, записывайте атомарно, сохраняйте известную рабочую версию для rollback и активируйте только полностью проверенный bundle.

## Тестирование

Используйте несколько уровней тестов:

1. Unit tests для preprocessing и postprocessing с точными ожидаемыми значениями.
2. Smoke test, загружающий настоящую модель и проверяющий tensor metadata.
3. Golden tests с небольшим отобранным dataset и ожидаемыми labels или ограниченным диапазоном числового результата.
4. Performance tests на репрезентативных физических устройствах.
5. Regression checks при изменении модели, runtime, labels или preprocessing.

Floating-point output может немного отличаться на разных accelerators. Используйте подходящие tolerances вместо точного равенства, но явно зафиксируйте продуктовые acceptance criteria.

## Частые ошибки

- `.tflite` воспринимается как самодостаточный контракт продукта.
- Inference выполняется на main thread.
- Runtime пересоздаётся, а buffers выделяются для каждого запроса.
- Используется неверный resize, normalization, channel order или tokenizer.
- Предполагается, что GPU или NPU всегда быстрее.
- Модель обновляется без соответствующих labels или preprocessing.
- Accuracy проверяется только на нескольких выбранных разработчиком примерах.
- Игнорируются ошибки загрузки модели, нехватка места, rollback или integrity.

## См. также

- [AI на Android](overview.md)
- [LiteRT for Android](https://developers.google.com/edge/litert/android)
- [Конвертация моделей LiteRT](https://developers.google.com/edge/litert/conversion/overview)
- [Оптимизация моделей LiteRT](https://developers.google.com/edge/litert/quantization/model_optimization)
- [Рекомендации по производительности LiteRT](https://developers.google.com/edge/litert/performance/best_practices)
