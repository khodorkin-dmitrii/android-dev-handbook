# Android

Этот раздел посвящён самой Android-платформе: точкам входа приложения, lifecycle и поведению процесса, основам UI, системным сервисам, хранению данных, фоновой работе, сборке, производительности, межпроцессному взаимодействию и графике.

Практичный порядок изучения: сначала компоненты и lifecycle, затем `Context`, ресурсы, UI, storage и background work. Темы сборки, производительности, IPC, системных сервисов и графики полезнее после основ платформы.

## Основы платформы и UI

- [Android Components](components.md) - точки входа приложения, intents, границы процесса и доступность компонентов извне.
- [Activity, Fragment & Lifecycle](activity-fragment-lifecycle.md) - переходы lifecycle, configuration changes, восстановление состояния и process death.
- [Context & Resources](context-resources.md) - время жизни context, ресурсы, configuration и локализация.
- [View System / XML UI](view-system-xml-ui.md) - measurement, layout, drawing, custom views, RecyclerView и View Binding.
- [Android System Services](android-system-services.md) - платформенные сервисы, получаемые через `Context`, и их lifecycle- и permission-ограничения.

## Данные, выполнение и системные границы

- [Storage](storage.md) - Room и SQLite, preferences, файлы, миграции и выбор хранилища.
- [Background Work & System Behavior](background-work-system-behavior.md) - WorkManager, foreground services, alarms, Doze и ограничения фоновой работы.
- [Binder IPC and AIDL](binder-ipc-aidl.md) - Binder, межпроцессные вызовы, AIDL-контракты, ограничения, lifecycle и безопасность.

## Сборка, производительность и память

- [Gradle & Build System](gradle-build-system.md) - Gradle, Android Gradle Plugin, варианты сборки, конфигурации зависимостей, кеширование и воспроизводимость.
- [Performance & Memory](performance-memory.md) - ANR, jank, allocations, утечки, профилирование, R8 и runtime-производительность.

## Графика и rendering

- [Android Canvas](canvas.md) - immediate-mode 2D drawing и custom rendering.
- [AGSL and RuntimeShader](agsl-runtime-shader.md) - Android Graphics Shading Language, shader effects и интеграция с Compose.
- [OpenGL ES](opengl-es.md) - программируемый GPU rendering на Android.
- [Vulkan](vulkan.md) - явные low-level API для графики и вычислений.
- [Google Filament](google-filament.md) - real-time physically based 3D rendering.
- [2D and 3D Rendering](2d-3d-rendering.md) - выбор API и архитектурные компромиссы rendering.
