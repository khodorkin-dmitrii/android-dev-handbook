# Google Filament

Google Filament - real-time physically based rendering engine, который упрощает создание качественной 3D-графики на Android и других платформах.

## Filament basics

### Что это такое

Filament - 3D rendering engine от Google для real-time rendering с поддержкой PBR (physically based rendering), материалов, освещения, камер, сцен и разных graphics backends.

Он находится выше уровня OpenGL ES/Vulkan: разработчик работает не с raw draw calls и shaders для каждого объекта, а с engine abstractions - scene, entity, material, camera, light, renderable.

Filament подходит для случаев, где нужен качественный 3D rendering без написания собственного engine с нуля.

**Коротко:** Filament - это 3D engine поверх graphics APIs, который даёт готовую модель сцен, материалов, камер и освещения.

### Как устроен

В Filament есть несколько ключевых сущностей:

- `Engine` - центральный объект, управляющий rendering resources;
- `Renderer` - выполняет rendering кадра;
- `Scene` - содержит объекты и lights;
- `View` - связывает scene, camera и viewport;
- `Camera` - определяет точку зрения;
- materials - описывают внешний вид surfaces;
- renderables - geometry objects, которые можно рисовать.

Обычно приложение создаёт `Engine`, `SwapChain`, `Renderer`, `Scene`, `View` и `Camera`, затем добавляет renderable entities и каждый frame вызывает rendering.

Filament также имеет tooling для материалов и assets, например material compiler и поддержку glTF через companion libraries.

**Коротко:** Filament строится вокруг engine, scene, view, camera, renderables, lights и materials.

### Связь с OpenGL/Vulkan

Filament использует graphics backend под капотом. В зависимости от платформы и настроек это может быть OpenGL ES, Vulkan, Metal или другой backend.

Для Android это означает, что Filament может использовать GPU через backend, но приложение не обязано напрямую писать OpenGL ES или Vulkan code.

Такой слой abstraction полезен: rendering engine берёт на себя shader generation, material model, lighting, resource management и часть platform-specific деталей.

Но abstraction не отменяет базовые ограничения graphics: GPU memory, texture size, frame budget, lighting cost, overdraw, asset complexity и lifecycle всё равно важны.

**Коротко:** Filament работает поверх OpenGL/Vulkan-like backends и скрывает большую часть low-level graphics boilerplate.

## Scene model

### Камеры

Camera в Filament задаёт projection и view transform: где находится наблюдатель, куда он смотрит и какая projection используется.

Типичные параметры:

- position и orientation;
- field of view;
- near/far clipping planes;
- aspect ratio;
- perspective или orthographic projection.

Камера не рисует сама по себе. Она определяет, как `View` увидит `Scene` при rendering.

**Коротко:** camera задаёт точку зрения и projection, через которые scene превращается в изображение.

### Сцены

Scene содержит renderable objects и lights, которые участвуют в rendering.

В отличие от простого Canvas drawing, 3D scene обычно хранит набор entities, transforms, materials, geometry и lighting setup. Rendering engine каждый frame рассчитывает, что видно камере, какие materials применить и как освещение влияет на surfaces.

Scene может быть простой - один 3D model viewer - или сложной, с несколькими объектами, lights, skybox, indirect light и animation.

**Коротко:** scene - контейнер 3D-мира, который renderer отображает через выбранную camera и view.

### Материалы

Material описывает, как поверхность реагирует на свет и как она выглядит: base color, metallic, roughness, normal map, alpha, emissive и другие параметры.

Filament использует PBR-подход, поэтому materials стремятся вести себя физически правдоподобно. Это помогает получать стабильный реалистичный вид при разном lighting setup.

Material может быть параметризован: один compiled material definition используется с разными values/textures для разных объектов.

**Важно:** качество 3D часто зависит не только от geometry, но и от materials, textures, lighting и color management.

**Коротко:** material задаёт внешний вид surface и её взаимодействие с освещением.

### Освещение

Lighting в Filament включает direct lights и image-based lighting.

Direct lights - directional, point, spot lights и другие источники, которые явно размещаются в scene. Image-based lighting использует environment/skybox для более реалистичного отражённого света.

Для PBR rendering освещение критично: без корректного light setup даже хорошие models и materials могут выглядеть плоско или неестественно.

Lighting влияет на performance. Много источников света, большие shadow maps и сложные materials увеличивают GPU cost.

**Коротко:** освещение определяет, как материалы воспринимаются в сцене, и сильно влияет на качество 3D rendering.

### Типичные сценарии использования

Filament подходит для:

- 3D model viewer;
- product preview;
- AR-related rendering;
- interactive 3D objects;
- educational visualization;
- configurators;
- maps/scene visualization;
- rendering glTF assets.

Он обычно избыточен для обычных business screens, простых charts и flat 2D graphics. Для таких задач чаще достаточно Compose, View System или Canvas.

**Коротко:** Filament выбирают, когда нужен качественный real-time 3D без написания собственного OpenGL/Vulkan engine.
