# ML Kit on Android

ML Kit provides high-level machine learning APIs designed for mobile applications. It is a good default when a ready-made API already solves the task: the application works with Android-friendly objects instead of managing tensors, model operators, and hardware delegates directly.

ML Kit processing runs on the device. This enables offline use, low latency, and real-time camera scenarios while allowing sensitive input to remain local. Model delivery, supported devices, languages, and API stability still vary by feature.

## Available capabilities

ML Kit includes several groups of APIs:

- vision: text recognition, barcode scanning, face detection, image labeling, object detection and tracking, pose detection, segmentation, and document scanning;
- natural language: language identification, translation, smart reply, and entity extraction;
- generative AI: summarization, proofreading, rewriting, image description, speech recognition, and prompting on supported devices.

Traditional vision and natural-language APIs use task-specific models. ML Kit GenAI APIs are a separate family built on AICore and the device's shared Gemini Nano model. Their device and language coverage is narrower, so check availability at runtime and design a fallback before committing to a product flow.

## ML Kit or LiteRT?

Choose ML Kit when:

- a supported API matches the use case;
- you want a production-ready model and processing pipeline;
- the team should focus on feature behavior instead of model integration;
- Android-friendly result objects are sufficient.

Choose [LiteRT](litert.md) when:

- the application must run a custom `.tflite` model;
- preprocessing and postprocessing are part of a custom model contract;
- you need direct control over tensors or acceleration;
- ML Kit's model, output, or supported use cases do not meet the requirements.

Selected ML Kit APIs also accept custom models. Evaluate that option before implementing the entire pipeline at a lower level.

## Dependency and model delivery

The artifact and delivery options depend on the API. Some ML Kit features offer both:

- a **bundled model**, which is included in the application, works immediately, and increases application size;
- a **Google Play services model**, which keeps the application smaller but may need to download before the first successful request.

For example, Latin-script text recognition has separate artifacts:

```kotlin
dependencies {
    // Bundled model
    implementation("com.google.mlkit:text-recognition:16.0.1")

    // Or a model delivered through Google Play services
    // implementation("com.google.android.gms:play-services-mlkit-text-recognition:19.0.1")
}
```

These versions were current when this article was reviewed. Verify them in the feature's official guide. Do not add both variants for the same detector.

If the first-run flow cannot wait for a download, choose the bundled option or request installation-time delivery where the API supports it. Otherwise expose a preparing state and handle download failure. A Play services model can produce no result until its download completes.

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

`await()` is supplied by `kotlinx-coroutines-play-services`. Cancelling the awaiting coroutine does not necessarily cancel work already started by the underlying ML Kit task. Ignore late results after the owner or input has changed.

Scope the data source to an owner with an explicit lifetime, such as a screen-level component or dependency-injection scope. Close clients that expose `close()` when that owner is destroyed.

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
- use `ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST` for most real-time analysis;
- avoid overlapping detector calls unless the API and feature are designed for it;
- crop or reduce input resolution only after measuring the effect on accuracy.

## State and error handling

Represent the feature with explicit states rather than a nullable result:

```kotlin
sealed interface RecognitionState {
    data object Idle : RecognitionState
    data object Preparing : RecognitionState
    data class Ready(val text: String) : RecognitionState
    data class Failed(val cause: Throwable) : RecognitionState
}
```

Differentiate an empty but valid result, a missing or downloading model, unsupported input or device, cancellation, and an actual processing failure. Do not show an error for every camera frame that contains no recognizable object.

For GenAI APIs, runtime availability is part of the feature contract. Inference is allowed only while the app is the top foreground application, AICore enforces per-app quotas, and different Gemini Nano versions can produce different output. Handle unsupported devices, `BUSY`, battery quota, and background-use errors; evaluate quality across supported model versions.

## Performance and lifecycle

- Initialize and reuse detector clients.
- Run processing outside UI rendering code and never block the main thread while waiting for a result.
- Throttle continuous input and discard stale results when a newer frame supersedes them.
- Keep raw images out of long-lived state unless the feature requires them.
- Test cold start separately from steady-state latency because initialization or model download can dominate the first request.
- Measure on lower-end devices and with realistic camera resolutions.

## Privacy

On-device inference keeps API input and output local, but it does not automatically make the entire feature private. The application may still upload images, analytics, recognized text, or crash diagnostics. Document each data path and avoid recording user content in logs.

If a result is later sent to a backend or cloud model, explain that boundary in the product flow and apply the application's consent, retention, and security rules.

## Testing

Wrap the ML Kit client behind a small interface so ViewModels and use cases can use deterministic fakes:

```kotlin
fun interface TextRecognizerGateway {
    suspend fun recognize(bitmap: Bitmap): String
}
```

Use integration tests with a curated image set for the real client. Include rotation, blur, low light, partial content, supported scripts, empty input, and the minimum useful image size. Avoid asserting an unstable full OCR string when a smaller invariant is sufficient. For probabilistic or generative output, evaluate quality over a representative dataset instead of relying on one golden response.

## Common mistakes

- Recreating the detector for every frame.
- Forgetting to close `ImageProxy` or a closeable ML Kit client.
- Assuming a model or GenAI capability is available.
- Processing every camera frame and building an unbounded queue.
- Updating UI with a stale result after the screen or input has changed.
- Treating probabilistic output as a guaranteed fact.
- Logging images or recognized user content.

## See also

- [AI on Android](overview.md)
- [LiteRT](litert.md)
- [ML Kit documentation](https://developers.google.com/ml-kit)
- [ML Kit GenAI APIs](https://developers.google.com/ml-kit/genai)
- [Text recognition on Android](https://developers.google.com/ml-kit/vision/text-recognition/v2/android)
- [CameraX image analysis](https://developer.android.com/media/camera/camerax/analyze)
