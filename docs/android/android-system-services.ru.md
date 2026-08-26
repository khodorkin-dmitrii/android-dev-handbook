# Основные системные службы Android

Системные службы Android координируют поведение всей платформы: запуск компонентов, процессы, установленные packages, окна и ввод. Приложения обычно обращаются к ним через публичные framework API, например `ActivityManager`, `PackageManager` и `WindowManager`; многие такие вызовы Binder переносит через границу процессов.

## Что такое системная служба

Framework или system service владеет платформенным состоянием и политиками, общими для многих приложений. Это не то же самое, что `Service` приложения - Android-компонент с callbacks вроде `onStartCommand()` и `onBind()`. App `Service` не получает отдельный процесс или background thread автоматически.

Многие Java framework services инициализируются в процессе `SystemServer` или тесно с ним связаны, но это верно не для всех Android services. Важные native-компоненты платформы могут работать в отдельных процессах. Один из примеров - SurfaceFlinger, который композитит графические surfaces для вывода на дисплей.

Упрощенный контекст запуска выглядит так:

```text
init -> Zygote -> SystemServer -> framework services
```

`init` запускает Zygote, а Zygote создает `SystemServer`. Затем `SystemServer` запускает framework services по этапам с учетом зависимостей. Это лишь общий ориентир, а не полное описание загрузки Android.

## Основные службы

### Activity Manager Service - AMS

Activity Manager Service (AMS) координирует процессы приложений и отслеживает их важность для пользователя. От process importance зависит, какие cached processes система может завершить при нехватке памяти. AMS также координирует выполнение application `Service` и broadcasts, участвует в обработке crashes и ANR и взаимодействует с package, task, window и другими framework services.

В современном Android AMS не отвечает единолично за все, что связано с activities и tasks. Process-level и component-level работу он координирует с Activity Task Manager Service, а app process получает lifecycle transactions через framework-обвязку, после чего выполняются callbacks `Activity`. Это различие полезно при чтении логов: переход activity может включать ATMS, AMS, процесс приложения и WMS, а не один manager, напрямую вызывающий все callbacks.

### Activity Task Manager Service - ATMS

Activity Task Manager Service (ATMS) отвечает за значительную часть современного управления activities и tasks. Он координирует запуск activity, состояние tasks и back stack, переходы между состояниями activity, размещение на дисплеях и организацию tasks, включая multi-window сценарии.

ATMS тесно взаимодействует с AMS, когда для запуска требуется app process или меняется его важность. Он также работает с WMS, поскольку activity и ее task связаны с окнами, дисплеями и transitions. Task - это ориентированный на пользовательский сценарий стек activities, а не просто "один task на приложение": flags, launch modes, document behavior и multi-window создают более сложные варианты.

### Package Manager Service - PMS

Package Manager Service (PMS) поддерживает представление платформы об установленных packages и их состоянии. При загрузке и изменении packages код управления пакетами сканирует и сохраняет сведения о packages, manifests, components и связанных metadata. Он поддерживает запросы packages и components, intent resolution, enabled или disabled state и относящиеся к permissions сведения о package.

PMS играет центральную роль в ответах на вопросы вроде "какая activity может обработать этот intent?" или "какие metadata относятся к этому component?" Но он не принимает все runtime-решения по безопасности в одиночку. Проверки permissions распределены между framework service, предоставляющим операцию, компонентами permission management, app-ops и другими слоями платформы.

### Window Manager Service - WMS

Window Manager Service (WMS) управляет иерархией и политикой окон: bounds, z-order, focus, организацией дисплеев, окнами приложений и системы, insets, transitions и другим window-level состоянием. Он координируется с ATMS для окон activities и tasks и предоставляет сведения об окнах и focus, нужные для маршрутизации input.

WMS не рисует views приложения и не композитит итоговые pixels. Приложение рендерит buffers в `Surface`. WMS управляет размещением и metadata, а отдельный native-процесс SurfaceFlinger объединяет видимые графические surfaces, при необходимости с помощью Hardware Composer, и выводит результат на дисплей.

### Input Manager Service - IMS

Input Manager Service (IMS) вместе с native input components координирует чтение и доставку событий от touchscreen, клавиатуры и других устройств ввода. Для выбора получателя input dispatch использует актуальные сведения об окнах, дисплеях, touch target и focus, которые поддерживаются во взаимодействии с WMS.

Выбранные события по input channel направляются к нужному окну приложения, где app framework передает их через view hierarchy или Compose input system. Поэтому источник проблемы с вводом может находиться раньше click handler: неправильное focused window, блокирующий overlay, устаревшее окно или неотвечающий main thread могут помешать ожидаемому UI target получить или обработать событие.

## Запуск приложения как совместная работа служб

После нажатия на иконку в launcher участвующие службы можно представить в виде упрощенной последовательности:

1. Launcher запрашивает запуск activity через публичный framework API.
2. Система обращается к package-management state, чтобы разрешить или проверить target component и получить его metadata.
3. ATMS координирует запуск activity, выбор task и переход back stack.
4. AMS обеспечивает наличие подходящего процесса приложения и учитывает его process state.
5. Если нужен новый процесс, платформа просит подходящий Zygote создать или специализировать его. Современные устройства могут использовать заранее созданный USAP pool, поэтому свежий fork в этот момент требуется не всегда.
6. Framework планирует создание компонента и lifecycle work в процессе приложения, а WMS подготавливает соответствующее окно и transition и управляет ими.
7. Приложение рендерит UI buffers в свой surface.
8. SurfaceFlinger композитит видимые surfaces для дисплея.
9. IMS направляет последующий input с учетом текущих focused window и touch target.

Это удобная модель, а не единая строго линейная цепочка вызовов. Часть работы выполняется параллельно, explicit launch почти не требует intent resolution, существующие процессы и activities могут переиспользоваться, а реализация меняется между версиями Android. Важна граница ответственности: packages, tasks, processes, windows, композицию и input координируют разные компоненты.

## Зачем это разработчику приложений

Понимание этих границ помогает превратить системный симптом в более точный вопрос для диагностики:

- Неожиданное переиспользование activity, поведение Back или размещение в multi-window часто стоит начинать проверять с task state ATMS, launch modes и intent flags.
- Пересоздание экрана после возврата в приложение может быть следствием управляемого AMS завершения процесса, а не штатного пути через `Activity.onDestroy()`.
- При расследовании ANR нужно сопоставлять отзывчивость main thread с координацией timeouts в AMS/ATMS и ожиданием приложения со стороны WMS или IMS.
- Отсутствующий intent target или disabled component указывает на PMS resolution, manifest metadata, package visibility или permissions.
- Dialog, overlay или клавиатура, изменившие focus, могут объяснить поведение окна и input еще до выполнения gesture-кода приложения.

`dumpsys` показывает снимки этого состояния. `dumpsys activity` помогает изучать процессы и component records; в актуальных версиях сведения об activities и tasks также могут выводиться через связанные activity/task dumps. `dumpsys package` показывает данные packages, components и resolution. `dumpsys window` полезен для дисплеев, окон и focus, а `dumpsys input` - для устройств и состояния dispatch. Формат вывода зависит от версии, поэтому его лучше использовать для проверки конкретной гипотезы, а не считать расположение полей стабильным API.

## См. также

- [Binder IPC и AIDL](binder-ipc-aidl.md)
- [Activity, Fragment & Lifecycle](activity-fragment-lifecycle.md)
- [Android Components](components.md)
- [Performance & Memory - ANR](performance-memory.md#anr)

## Дополнительные материалы

- [SystemServer source - Android Open Source Project](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-16.0.0_r3/services/java/com/android/server/SystemServer.java)
- [ActivityTaskManagerService source - Android Open Source Project](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-16.0.0_r3/services/core/java/com/android/server/wm/ActivityTaskManagerService.java)
- [SurfaceFlinger and WindowManager - Android Open Source Project](https://source.android.com/docs/core/graphics/surfaceflinger-windowmanager)
- [About the Zygote processes - Android Open Source Project](https://source.android.com/docs/core/runtime/zygote)
- [Processes and app lifecycle - Android Developers](https://developer.android.com/guide/components/activities/process-lifecycle)

