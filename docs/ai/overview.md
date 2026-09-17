# AI on Android

Android applications can use artificial intelligence without training models inside the app. The main engineering decision is where inference runs and how much control the application needs over the model and data pipeline.

This domain focuses on integrating AI capabilities into Android applications. It covers model selection, input and output processing, lifecycle, performance, privacy, and testing. Model training is mentioned only where it affects mobile integration.

## Main approaches

| Approach | Best suited for | Model ownership | Typical examples |
| --- | --- | --- | --- |
| ML Kit | Common production-ready mobile tasks | Google or a supported custom model | OCR, barcode scanning, face detection, translation |
| LiteRT | Custom models and direct control over inference | Application team or model provider | Classification, segmentation, embeddings, audio models |
| MediaPipe | Real-time pipelines for image, audio, and streaming data | Google solution or custom pipeline | Hand landmarks, pose tracking, live video processing |
| On-device generative AI | Supported generative tasks without a network round trip | Platform-provided model or packaged model | Summarization, rewriting, image description |
| Cloud AI API | Large models, frequently updated models, or server-side orchestration | Cloud provider or backend team | Chat, multimodal analysis, retrieval-augmented generation |

These approaches can be combined. For example, ML Kit can extract text locally, while a cloud model interprets the result after the user has consented to sending it.

## On-device and cloud inference

On-device inference usually provides:

- low latency without a network round trip;
- offline operation;
- stronger privacy because raw input can remain on the device;
- predictable per-request infrastructure cost.

Its constraints include application or model download size, limited memory and compute resources, device fragmentation, thermal throttling, and slower model updates.

Cloud inference usually provides larger models and easier centralized updates, but introduces network latency, availability concerns, server cost, authentication, and data-governance requirements.

Choose based on product requirements rather than treating one option as universally better. A hybrid design can keep latency-sensitive or private preprocessing on the device and use the backend only for tasks that need a larger model.

## Choosing an Android AI stack

Start with the highest-level API that solves the task:

1. Use **ML Kit** when a supported ready-made API meets the product requirements.
2. Use **MediaPipe** when the feature is a real-time perception pipeline and a suitable solution already exists.
3. Use **LiteRT** when you need to run your own `.tflite` model or control tensors, delegates, and preprocessing.
4. Use an on-device generative API when the task and supported device matrix match its constraints.
5. Use a cloud API when model capability or centralized operation outweighs latency, offline, privacy, and cost concerns.

Do not choose LiteRT merely because it is lower-level. Owning the model contract, preprocessing, postprocessing, compatibility, and performance validation creates additional maintenance work.

## Typical application architecture

Keep UI code independent from a specific ML runtime:

```text
Camera / file / user input
          |
          v
Input preprocessing
          |
          v
AI feature interface
          |
          +-- ML Kit implementation
          +-- LiteRT implementation
          +-- Cloud implementation
          |
          v
Domain result
          |
          v
ViewModel and UI state
```

Expose domain-level results such as `RecognizedText`, `DetectedObject`, or `Classification`, not runtime-specific tensor types. This makes the feature easier to test and allows the implementation to change without rewriting the UI.

Inference must not block the main thread. Treat cameras and continuous streams as backpressure-sensitive sources: process only the frames the feature can consume, and always release frame resources.

## Production concerns

### Model and API availability

Check whether the API requires a specific Android version, device capability, Google Play services version, or a model download. The UI should represent unavailable, downloading, ready, and failed states where applicable.

### Performance

Measure representative devices, not only an emulator or a flagship phone. Track at least:

- cold initialization time;
- warm inference latency;
- memory usage and allocations;
- model or feature download size;
- battery consumption and thermal behavior;
- throughput for camera or audio streams.

### Privacy and security

Document what data is processed, where inference happens, whether inputs leave the device, and how long results are retained. Avoid logging images, audio, prompts, recognized text, or raw tensors containing user data. Treat downloaded models as application assets that still require integrity and version management.

### Testing

Separate deterministic preprocessing and postprocessing from the runtime adapter. Unit-test transformations with fixed inputs and use a small curated dataset for integration and regression tests. Validate behavior across lighting conditions, orientations, languages, device classes, and malformed input relevant to the feature.

ML output is probabilistic. Product logic should define confidence thresholds, empty results, fallback behavior, and whether a user can correct the result.

## Where to continue

- [ML Kit](ml-kit.md) - ready-made on-device APIs for common mobile use cases.
- [LiteRT](litert.md) - running custom models and managing the inference pipeline.

## See also

- [AI on Android](https://developer.android.com/ai)
- [ML Kit](https://developers.google.com/ml-kit)
- [LiteRT for Android](https://developers.google.com/edge/litert/android)
- [MediaPipe Solutions](https://ai.google.dev/edge/mediapipe/solutions/guide)
