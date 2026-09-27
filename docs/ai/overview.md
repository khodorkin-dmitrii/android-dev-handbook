# AI on Android

Android apps can use AI without training models inside the app. The main engineering decisions are what capability the product needs, where inference runs, and how much control the team needs over the model and data pipeline.

This domain focuses on integrating AI features into Android applications: solution selection, input and output processing, lifecycle, performance, privacy, safety and testing. Model training matters only where it changes the mobile contract.

## Main approaches

| Approach | Best suited for | Typical examples |
| --- | --- | --- |
| ML Kit | Ready-made on-device vision and language tasks | Text recognition, barcode scanning, face detection, translation |
| ML Kit GenAI APIs | Supported Gemini Nano tasks on compatible devices | Summarization, rewriting, image description, prompt-based generation |
| LiteRT | Running custom models with direct control over inference | Classification, segmentation, embeddings, audio models |
| MediaPipe | Cross-platform, real-time perception pipelines | Hand landmarks, pose tracking, live image or audio processing |
| Cloud or hybrid AI | Larger models, centralized updates and server orchestration | Chat, multimodal analysis, retrieval-augmented generation |

These approaches can be combined. For example, ML Kit can extract text locally and a cloud model can interpret it after the app has obtained appropriate consent to send the data.

## On-device, cloud and hybrid inference

On-device inference can provide low latency, offline operation and stronger privacy because input can remain on the device. It also avoids per-request server inference cost. Constraints include model or feature download size, memory and compute limits, device fragmentation, thermal throttling and slower model rollout.

Cloud inference provides access to larger models and centralized updates, but adds network latency, availability risk, backend cost, authentication and data-governance requirements. Never place an unrestricted provider secret in an APK; use a mobile-safe SDK with suitable abuse protection or route calls through a backend.

A hybrid design can keep private or latency-sensitive preprocessing on the device and use the cloud only for capabilities that need a larger model. Choose from product requirements and measured behavior, not from a blanket claim that one location is always faster or safer.

## Choosing the stack

Start with the highest-level API that meets the requirements:

1. Use **ML Kit** when a supported ready-made API solves the task.
2. Use **ML Kit GenAI APIs** when the supported Gemini Nano capability, languages and device matrix fit the product.
3. Use **MediaPipe** when the feature is a real-time perception pipeline and an appropriate solution exists.
4. Use **LiteRT** when you need a custom model or control over tensors, accelerators, preprocessing and postprocessing.
5. Use a **cloud or hybrid API** when model capability or centralized operation outweighs latency, offline, privacy and cost constraints.

Do not choose a lower-level runtime merely for flexibility. Owning the model contract, preprocessing, postprocessing, compatibility and performance validation creates long-term maintenance work.

## Application architecture

Keep UI code independent from the selected runtime:

```text
Camera / file / user input
          |
          v
Input validation and preprocessing
          |
          v
AI feature interface
          |
          +-- ML Kit implementation
          +-- LiteRT / MediaPipe implementation
          +-- Cloud implementation
          |
          v
Domain result
          |
          v
ViewModel and UI state
```

Expose domain types such as `RecognizedText`, `DetectedObject` or `Classification`, not tensors or SDK response objects. This makes deterministic processing easier to test and allows the implementation to change without rewriting the UI.

Inference must not block the main thread. Treat camera and audio streams as backpressure-sensitive sources: limit concurrent work, process only the data the feature can consume, and always release frames and other resources.

## Production concerns

### Availability and lifecycle

Check Android version, hardware capability, Google Play services or system-service requirements, supported languages, and whether a model must be downloaded. Represent unavailable, downloading, ready, busy and failed states when relevant.

On-device generative APIs have a narrower support matrix than ordinary ML Kit APIs. Their output may also vary between model versions. Current ML Kit GenAI APIs can enforce per-app resource quotas and restrict inference to the foreground, so availability must be checked at runtime rather than assumed from the OS version alone.

### Performance

Measure representative physical devices, not only an emulator or flagship phone. Track cold initialization, warm inference latency, memory and allocations, download size, battery and thermal behavior, and stream throughput. Select CPU, GPU or NPU acceleration only after measuring both latency and compatibility on the target device set.

### Privacy, security and safety

Document what data is processed, where inference occurs, whether input leaves the device and how long inputs and results are retained. Avoid logging images, audio, prompts, recognized text or tensors that may contain user data. Validate downloaded model integrity and version compatibility.

AI output is untrusted input to the rest of the app. Validate formats and ranges, apply product-specific safety rules, and require explicit confirmation before consequential actions. Always provide a fallback for unavailable models, low-confidence results and network failure.

### Testing and evaluation

Separate deterministic preprocessing and postprocessing from the runtime adapter. Unit-test transformations with fixed inputs and maintain a small, versioned evaluation dataset covering relevant languages, lighting, orientations, device classes and malformed input.

For classification or detection, evaluate task-specific metrics and confidence thresholds instead of expecting perfect output. For generative features, do not assert one exact sentence: validate constraints and use repeatable quality and safety evaluations. Record the model/API version with regression results because the same input can produce different output after an update.

## Related topics

- [ML Kit](ml-kit.md) - ready-made on-device APIs for common mobile use cases.
- [LiteRT](litert.md) - custom models and direct control of the inference pipeline.

Sources: [AI on Android](https://developer.android.com/ai), [ML Kit](https://developers.google.com/ml-kit), [ML Kit GenAI APIs](https://developers.google.com/ml-kit/genai), [LiteRT for Android](https://developers.google.com/edge/litert/android), [MediaPipe Solutions](https://developers.google.com/edge/mediapipe/solutions/guide).
