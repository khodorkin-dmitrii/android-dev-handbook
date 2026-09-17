# LiteRT on Android

LiteRT is Google's on-device runtime for executing machine learning models. It is the current name for the technology previously known as TensorFlow Lite, and `.tflite` remains the model file format.

Use LiteRT when an Android application must run a custom or third-party model and the team needs control over the complete inference pipeline: model delivery, preprocessing, tensors, execution, postprocessing, and performance.

## When LiteRT is appropriate

LiteRT is a strong fit when:

- a custom `.tflite` model is part of the product;
- a ready-made [ML Kit](ml-kit.md) API does not cover the task;
- inference must work offline or keep source data on the device;
- latency requires local execution;
- the team can own model compatibility and device validation.

LiteRT is not a model-training framework inside the Android app. A model is normally trained or obtained elsewhere, converted and optimized if necessary, then packaged or delivered to the device for inference.

## The inference pipeline

A working model file is only one part of the feature:

```text
Application input
      |
      v
Decode, resize, normalize, tokenize
      |
      v
Input tensor or buffer
      |
      v
LiteRT execution
      |
      v
Output tensor or buffer
      |
      v
Decode, threshold, map labels
      |
      v
Domain result
```

Preprocessing and postprocessing are part of the model contract. Incorrect channel order, dimensions, normalization, tokenization, quantization parameters, or label mapping can produce plausible but wrong output without throwing an exception.

Record the contract next to the model: tensor names, shapes, data types, value ranges, color space, label version, and expected output interpretation.

## Android runtime APIs

LiteRT provides two Android runtime directions:

- **`CompiledModel` API** is the modern high-performance API and is designed to streamline acceleration across CPU, GPU, and NPU.
- **`Interpreter` API** is the basic API retained for backward compatibility and for existing integrations.

Prefer `CompiledModel` for a new integration when its device and feature requirements are compatible with the application. Do not migrate an established `Interpreter` integration only for naming consistency: compare supported devices, operators, delegates, performance, binary size, and migration cost.

The APIs and supported Android versions evolve. Select the runtime version from the current compatibility table in the official documentation instead of copying a version from an old sample.

## Dependency and model asset

For the modern runtime, add the current LiteRT artifact:

```kotlin
dependencies {
    implementation("com.google.ai.edge.litert:litert:2.2.0")
}
```

This version was current when the article was reviewed. Verify the Android compatibility table before adopting it because runtime and minimum SDK requirements evolve.

Store a packaged model under `src/main/assets/` when it should ship with the application:

```text
app/src/main/assets/models/image_classifier.tflite
```

Packaging provides immediate offline availability but increases download size and couples model updates to application releases. Remote delivery allows independent updates but needs integrity checks, versioning, rollback, storage management, and an unavailable or downloading state.

## Minimal `CompiledModel` flow

The modern API creates a compiled model for a selected accelerator, preallocates buffers, runs inference, and reads the output:

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

`modelPath` must refer to a location supported by the selected API. If an API requires a filesystem path, copy the packaged asset to an application-private file before creating the model. Do this once per model version, not before every inference.

The example shows the runtime mechanics, not a complete classifier. Real code must validate tensor shapes and types, implement the exact preprocessing contract, interpret output, release runtime resources according to the API lifecycle, and handle initialization failures.

## Encapsulating the runtime

Keep LiteRT types out of ViewModels and UI:

```kotlin
interface ImageClassifier {
    suspend fun classify(bitmap: Bitmap): List<Classification>
}

data class Classification(
    val label: String,
    val confidence: Float,
)
```

An implementation can own the compiled model, reusable buffers, label mapping, and preprocessing. Construct it in a background-capable scope and reuse it for many requests. Serialize access unless the selected runtime object and buffer strategy are explicitly safe for concurrent calls.

## Preprocessing and postprocessing

For an image model, preprocessing may include:

- applying EXIF or camera rotation;
- cropping according to the product requirement;
- resizing with the same strategy used during training;
- converting RGB channel values to the expected type and range;
- applying normalization or quantization parameters;
- writing values in the required tensor order.

Postprocessing may include softmax, non-maximum suppression, thresholding, label lookup, coordinate conversion, or ranking. Do not add a transformation merely because it is common. The model contract determines whether it is required. For example, some models already include a softmax operation.

Keep these transformations deterministic and test them independently from the runtime.

## Acceleration

Hardware acceleration is not automatically faster for every model or device.

- CPU has broad compatibility and is a useful baseline.
- GPU can improve throughput for compatible workloads but adds initialization and data-transfer overhead.
- NPU availability and operator support vary by device and runtime path.

Benchmark the complete feature, including preprocessing and postprocessing, on a representative device matrix. Measure cold initialization, warm latency, sustained throughput, memory, battery use, and thermal behavior. A delegate that improves a single inference can still be worse for a short-lived feature because initialization dominates total time.

Define a fallback to a compatible accelerator or report that the feature is unavailable. Never silently return a different semantic result when acceleration setup fails.

## Quantization and model size

Quantization can reduce model size and memory use and may improve execution speed, but it can also affect accuracy. The app must use the data type and scale or zero-point expected by the quantized tensor.

Evaluate size, latency, and task-specific quality together. A smaller model is useful only if its output still meets the product threshold on representative data.

## Threading, lifecycle, and streams

- Initialize the runtime away from latency-sensitive UI work.
- Never run synchronous inference on the main thread.
- Reuse the model and buffers where supported to reduce allocations.
- Give the runtime owner an explicit lifecycle and release native resources.
- For camera or audio streams, use bounded backpressure and drop obsolete inputs.
- Prevent stale inference results from overwriting state for newer input.
- Decide whether requests are serialized, cancelled, or processed by a bounded worker pool.

For a one-shot user action, report preparation separately if model initialization is noticeable. For continuous analysis, warm the runtime before accepting frames when product requirements allow it.

## Model delivery and versioning

Treat the model and its metadata as one versioned unit. A useful manifest includes:

- model version and checksum;
- required runtime version;
- input and output contract;
- labels or tokenizer version;
- minimum supported application version;
- quality metrics and rollout status.

For remotely delivered models, download to application-private storage, verify integrity before activation, write atomically, retain a known-good version for rollback, and activate only a fully validated bundle.

## Testing

Use several levels of tests:

1. Unit tests for preprocessing and postprocessing with exact expected values.
2. A smoke test that loads the real model and validates tensor metadata.
3. Golden tests with a small curated dataset and expected labels or bounded numeric output.
4. Performance tests on representative physical devices.
5. Regression checks when the model, runtime, labels, or preprocessing changes.

Floating-point output can vary slightly across accelerators. Use appropriate tolerances instead of exact equality, while keeping product-level acceptance criteria explicit.

## Common mistakes

- Treating `.tflite` as a self-describing product contract.
- Performing inference on the main thread.
- Recreating the runtime and allocating buffers for every request.
- Applying the wrong resize, normalization, channel order, or tokenizer.
- Assuming GPU or NPU is always faster.
- Updating a model without updating its labels or preprocessing.
- Testing accuracy on a few developer-selected examples only.
- Ignoring model download failure, disk pressure, rollback, or integrity.

## See also

- [AI on Android](overview.md)
- [LiteRT for Android](https://developers.google.com/edge/litert/android)
- [LiteRT model conversion](https://developers.google.com/edge/litert/conversion/overview)
- [LiteRT model optimization](https://developers.google.com/edge/litert/quantization/model_optimization)
- [LiteRT performance best practices](https://developers.google.com/edge/litert/performance/best_practices)
