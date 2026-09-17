# ML Kit on Android

ML Kit provides high-level machine learning APIs designed for mobile applications. It is a good default when a ready-made API already solves the task: the application works with Android-friendly objects instead of managing tensors, model operators, and hardware delegates directly.

Most ML Kit processing runs on the device. This enables offline use, low latency, and camera-based real-time scenarios while allowing sensitive source data to remain local.

## Available capabilities

ML Kit includes APIs in several groups:

- vision: text recognition, barcode scanning, face detection, image labeling, object detection and tracking, pose detection, segmentation, and document scanning;
- natural language: language identification, translation, smart reply, and entity extraction;
- generative AI on supported devices: APIs such as summarization, proofreading, rewriting, image description, speech recognition, and prompting.

Availability, lifecycle status, language support, and device requirements differ between APIs. Check the documentation for the specific feature before committing to a product design.

## ML Kit or LiteRT?

Choose ML Kit when:

- a supported API matches the use case;
- you want a production-ready model and processing pipeline;
- the team should focus on feature behavior instead of model integration;
- Android-friendly result objects are sufficient.

Choose [LiteRT](litert.md) when:

- the application must run a custom `.tflite` model;
- preprocessing and postprocessing are part of a custom model contract;
- you need direct control over input and output tensors or acceleration;
- ML Kit's model, output, or supported use cases do not meet the requirements.

ML Kit can also support custom models for selected APIs. Evaluate that option before building the entire pipeline at a lower level.

## Dependency and model delivery

The exact artifact depends on the API. Some ML Kit features offer two delivery options:

- a **bundled model** is included in the application, is available immediately, and increases application size;
- a **Google Play services model** keeps the initial application smaller but may require a model download before the first successful use.

For example, Latin-script text recognition uses different artifacts for bundled and Play services delivery:

```kotlin
dependencies {
    // Bundled model
    implementation("com.google.mlkit:text-recognition:16.0.1")

    // Or a model delivered through Google Play services
    // implementation("com.google.android.gms:play-services-mlkit-text-recognition:19.0.1")
}
```

The versions above were current when this article was reviewed. Verify them in the official guide before adding the dependency. Do not add both variants for the same detector unless the feature explicitly requires them.

If the first-run flow cannot wait for a download, use a bundled model or arrange installation-time download where the API supports it. The product must still handle unavailable and failed states.

## Text recognition example

Create and reuse the recognizer instead of constructing it for every frame:

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

`await()` is supplied by `kotlinx-coroutines-play-services`. If that adapter is not used, bridge the returned `Task` through listeners while preserving cancellation and lifecycle behavior.

The data source should be scoped to an owner with an explicit lifetime, such as a screen-level component or dependency-injection scope. Release clients that expose `close()` when that owner is destroyed.

## CameraX integration

Camera analysis adds rotation, backpressure, and resource-lifetime concerns:

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

Important rules:

- close every `ImageProxy`, including error and early-return paths;
- pass the frame rotation reported by CameraX;
- use `ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST` for many real-time scenarios;
- avoid running several detector invocations concurrently unless the API and feature were designed for it;
- crop or reduce input resolution only after measuring the effect on accuracy.

## State and error handling

Model the feature as explicit states rather than a nullable result:

```kotlin
sealed interface RecognitionState {
    data object Idle : RecognitionState
    data object Preparing : RecognitionState
    data class Ready(val text: String) : RecognitionState
    data class Failed(val cause: Throwable) : RecognitionState
}
```

Differentiate between an empty but valid recognition result, a missing or downloading model, unsupported input, cancellation, and an actual processing failure. Avoid showing an error for every camera frame that contains no recognizable object.

## Performance and lifecycle

- Initialize and reuse detector clients.
- Run processing outside UI rendering code and never block the main thread while waiting for a result.
- Throttle continuous input and discard stale results when a newer frame supersedes them.
- Keep raw images out of long-lived state unless the feature requires them.
- Test cold start separately from steady-state latency because model initialization or download can dominate the first request.
- Measure on lower-end devices and with realistic camera resolutions.

## Privacy

On-device processing does not automatically make the entire feature private. The application may still upload source images, analytics, recognized text, or crash diagnostics. Document each data path and avoid recording user content in logs.

If a result is later sent to a backend or cloud model, explain that boundary in the product flow and apply the application's consent, retention, and security rules.

## Testing

Wrap the ML Kit client behind a small interface so ViewModels and use cases can be tested with deterministic fakes:

```kotlin
fun interface TextRecognizerGateway {
    suspend fun recognize(bitmap: Bitmap): String
}
```

Use integration tests with a curated image set for the real client. Include rotation, blur, low light, partial content, supported scripts, empty input, and the minimum image size relevant to the product. Avoid asserting an unstable full OCR string when checking a smaller invariant is sufficient.

## Common mistakes

- Recreating the detector for every frame.
- Forgetting to close `ImageProxy` or a closeable ML Kit client.
- Assuming the model is already downloaded.
- Processing every camera frame and building an unbounded queue.
- Updating UI with a stale result after the screen or input has changed.
- Treating confidence-based output as a guaranteed fact.
- Logging images or recognized user content.

## See also

- [AI on Android](overview.md)
- [ML Kit documentation](https://developers.google.com/ml-kit)
- [Text recognition on Android](https://developers.google.com/ml-kit/vision/text-recognition/v2/android)
- [CameraX image analysis](https://developer.android.com/media/camera/camerax/analyze)
