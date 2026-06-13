# Vulkan

Vulkan - низкоуровневый graphics и compute API, созданный как более explicit и modern альтернатива OpenGL ES для прямого контроля над GPU.

## Vulkan basics

### Зачем появился

Vulkan появился, чтобы дать приложениям больше контроля над GPU work, memory management, synchronization и multi-threaded command recording.

OpenGL ES исторически проще в использовании, но большая часть работы скрыта внутри driver: validation, state tracking, resource management и implicit synchronization. Это удобно, но может давать непредсказуемый overhead.

Vulkan переносит больше ответственности на приложение: разработчик явно создаёт resources, command buffers, pipelines, synchronization primitives и управляет memory.

**Коротко:** Vulkan появился для более явного, предсказуемого и эффективного управления GPU, особенно в сложных rendering engines.

### Отличия от OpenGL ES

OpenGL ES - state-machine API с большим количеством implicit behavior. Vulkan - explicit API, где почти всё задаётся заранее и явно.

Ключевые отличия:

- Vulkan требует явного memory management;
- synchronization задаётся вручную через fences, semaphores, barriers;
- pipelines заранее описывают rendering state;
- command buffers можно записывать заранее и из разных threads;
- driver делает меньше hidden work во время draw.

OpenGL ES проще начать использовать и часто достаточно для custom effects, camera filters и умеренного rendering. Vulkan сложнее, но лучше масштабируется для больших engines, сложных сцен и multi-threaded rendering.

**Коротко:** OpenGL ES проще и более implicit, Vulkan сложнее и explicit, но даёт больше контроля над performance.

### Преимущества и недостатки

Преимущества Vulkan:

- ниже driver overhead в сложных сценах;
- более предсказуемая performance model;
- better multi-threading для подготовки command buffers;
- явный control над memory и synchronization;
- единая modern API-модель для graphics и compute.

Недостатки:

- высокий порог входа;
- намного больше boilerplate;
- сложнее debugging;
- легко получить bugs в synchronization или memory lifetime;
- не всегда даёт выигрыш для простых UI/2D задач.

Для большинства обычных Android-приложений Vulkan напрямую не нужен. Часто его используют через game engine или rendering engine, а не пишут raw Vulkan вручную.

**Коротко:** Vulkan мощный, но дорогой по сложности; он оправдан там, где нужен engine-level контроль над GPU.

### Насколько часто используется в Android приложениях

В обычных Android-приложениях Vulkan используется редко напрямую. Большинство экранов строятся через View System, Compose, Canvas или media/camera APIs.

Vulkan чаще встречается в:

- играх;
- 3D engines;
- AR/VR;
- heavy visualization;
- CAD/product viewers;
- custom rendering engines;
- некоторых camera/video/image processing pipelines.

Во многих production-приложениях Vulkan может присутствовать косвенно: через Unity, Unreal, Filament, Sceneform-like wrappers, maps/visualization engines или vendor SDK.

Если задача - обычный business UI, chart или custom 2D component, Vulkan почти всегда избыточен.

**Коротко:** raw Vulkan в Android app code встречается редко; чаще его используют engines и SDK, которым нужен сложный GPU rendering.
