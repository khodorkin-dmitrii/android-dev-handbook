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

LiteRT runs models; it is not normally where an Android application trains them. A model is trained or obtained elsewhere, converted and optimized if necessary, then packaged or delivered to the device. For large language models that need tokenization, streaming generation, KV caching, and tool calling, evaluate LiteRT-LM instead of building those layers directly on the basic runtime.

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

Record the contract next to the model: tensor names, shapes, data types, value ranges, color space, label or tokenizer version, and output interpretation. Model metadata can describe some of this information, but it does not replace a versioned product contract and validation tests.

## Android runtime APIs

LiteRT provides two main Android runtime APIs:

- **`CompiledModel` API** is the modern API for high-performance inference and streamlined CPU, GPU, and NPU acceleration.
- **`Interpreter` API** is the basic API maintained for backward compatibility and existing integrations. It can also use the LiteRT runtime delivered through Google Play services.

Prefer `CompiledModel` for a new integration when its SDK, operator, and device requirements match the application. Do not migrate a stable `Interpreter` integration only for naming consistency: compare device coverage, supported operators, acceleration, binary size, measured performance, and migration cost.

Runtime capabilities and Android requirements evolve. Select a version from the current compatibility table rather than copying an old sample.

## Dependency and model delivery

For the modern runtime, add the current LiteRT artifact:

```kotlin
dependencies {
    implementation("com.google.ai.edge.litert:litert:2.2.0")
}
```

Version `2.2.0` was current when this article was reviewed. Verify the compatibility table before adopting it.

Store a packaged model under `src/main/assets/` when it should ship with the application:

```text
app/src/main/assets/models/image_classifier.tflite
```

Packaging provides immediate offline availability but increases download size and couples model updates to application releases. Remote delivery allows independent updates but needs integrity checks, versioning, rollback, storage management, and explicit downloading or unavailable states. Treat a remotely supplied model as executable product input: accept only trusted sources and activate it only after validation.

## Minimal `CompiledModel` flow

The modern API creates a compiled model for a selected accelerator, allocates buffers, runs inference, and reads the output:

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

Use an overload that accepts `AssetManager` for a packaged asset when supported by the selected version. If an API needs a filesystem path, copy the asset once per model version to an application-private file, not before every inference.

This example shows runtime mechanics, not a complete classifier. Production code must validate tensor shapes and types, implement the exact preprocessing contract, interpret output, close or release resources required by the selected API, and handle initialization failures. `run()` is synchronous in this flow, so call it away from the main thread.

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

The implementation owns the compiled model, reusable buffers, label mapping, and preprocessing. Create it in a background-capable scope and reuse it for many requests. Serialize access unless the runtime object and buffer strategy are explicitly safe for concurrent calls. Cancellation of the caller does not necessarily interrupt native inference already in progress, so discard a late result when its owner or input is no longer current.

## Preprocessing and postprocessing

For an image model, preprocessing may include:

- applying EXIF or camera rotation;
- cropping according to the product requirement;
- resizing with the same strategy used during training;
- converting RGB channels to the expected type and range;
- applying normalization or quantization parameters;
- writing values in the required tensor order.

Postprocessing may include softmax, non-maximum suppression, thresholding, label lookup, coordinate conversion, or ranking. Do not add a transformation merely because it is common. The model contract determines whether it is required; for example, some models already contain softmax.

Keep these transformations deterministic and test them independently from the runtime.

## Acceleration

Hardware acceleration is not automatically faster for every model or device.

- CPU has broad compatibility and is a useful baseline.
- GPU can improve throughput for compatible workloads but adds initialization and data-transfer overhead.
- NPU availability and operator support vary by device, model, and runtime version.

Benchmark the complete feature, including preprocessing and postprocessing, on a representative device matrix. Measure cold initialization, warm latency, sustained throughput, memory, battery use, and thermal behavior. An accelerator that improves one inference can still lose for a short-lived feature because initialization dominates total time.

Define an explicit fallback to a compatible accelerator or mark the feature unavailable. Verify output quality after fallback as well as successful execution; different backends can produce small numerical differences.

## Quantization and model size

Quantization can reduce model size and memory use and may improve execution speed, but it can affect accuracy. Full integer quantization normally needs a representative dataset during conversion. The application must write and read the data types, scale, and zero-point required by the quantized tensors.

Evaluate size, latency, memory, and task-specific quality together. A smaller model is useful only if its output still meets the product threshold on representative data and target accelerators.

## Threading, lifecycle, and streams

- Initialize the runtime away from latency-sensitive UI work.
- Never run synchronous inference on the main thread.
- Reuse the model and buffers where supported to reduce allocations.
- Give the runtime owner an explicit lifecycle and release native resources.
- For camera or audio streams, use bounded backpressure and drop obsolete inputs.
- Prevent stale inference results from overwriting state for newer input.
- Decide whether requests are serialized, ignored while busy, or processed by a bounded worker pool.

For a one-shot action, expose a preparation state if initialization is noticeable. For continuous analysis, warm the runtime before accepting frames when product requirements allow it.

## Model delivery and versioning

Treat the model and its metadata as one versioned unit. A useful manifest includes:

- model version and checksum;
- required runtime version;
- input and output contract;
- labels or tokenizer version;
- minimum supported application version;
- quality metrics and rollout status.

For remotely delivered models, download to application-private storage, verify integrity and compatibility before activation, write atomically, retain a known-good version for rollback, and activate only a complete validated bundle.

## Testing

Use several levels of tests:

1. Unit tests for preprocessing and postprocessing with exact expected values.
2. A smoke test that loads the real model and validates tensor metadata.
3. Golden tests with a curated dataset and expected labels or bounded numeric output.
4. Performance tests on representative physical devices and accelerators.
5. Regression checks whenever the model, runtime, labels, or preprocessing changes.

Floating-point output can vary slightly across accelerators. Use appropriate tolerances instead of exact equality while keeping product-level acceptance criteria explicit.

## Common mistakes

- Treating `.tflite` as a self-contained product contract.
- Performing inference on the main thread.
- Recreating the runtime and allocating buffers for every request.
- Applying the wrong resize, normalization, channel order, or tokenizer.
- Assuming GPU or NPU is always faster or fully compatible.
- Updating a model without its labels, tokenizer, or preprocessing.
- Testing quality on only a few developer-selected examples.
- Ignoring download failure, disk pressure, rollback, compatibility, or integrity.

## See also

- [AI on Android](overview.md)
- [ML Kit](ml-kit.md)
- [LiteRT for Android](https://developers.google.com/edge/litert/android)
- [LiteRT overview](https://developers.google.com/edge/litert/overview)
- [LiteRT model conversion](https://developers.google.com/edge/litert/models/convert)
- [Post-training integer quantization](https://developers.google.com/edge/litert/conversion/tensorflow/quantization/post_training_integer_quant)
