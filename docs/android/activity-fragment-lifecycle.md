# Activity, Fragment & Lifecycle

Lifecycle в Android описывает, как компоненты создаются, становятся видимыми, уходят в фон, уничтожаются и восстанавливают состояние.

## Activity и Fragment

### Activity lifecycle

![Activity lifecycle](../assets/images/android/activity-lifecycle.png)

`Activity` lifecycle описывает, как экран проходит состояния создания, видимости, взаимодействия с пользователем, ухода в фон и уничтожения.

Базовая последовательность callbacks: `onCreate()` -> `onStart()` -> `onResume()` -> `onPause()` -> `onStop()` -> `onDestroy()`. Между `onStop()` и `onStart()` при возврате может быть вызван `onRestart()`.

`onCreate()` вызывается при первом создании `Activity`: здесь обычно настраивают UI, dependency entry points, `ViewModel` и стартовую инициализацию. `onStart()` означает, что `Activity` становится видимой. `onResume()` означает, что `Activity` находится на переднем плане и пользователь может с ней взаимодействовать.

`onPause()` вызывается, когда `Activity` теряет фокус, но может оставаться частично видимой. `onStop()` вызывается, когда `Activity` больше не видна. `onDestroy()` вызывается перед финальным уничтожением `Activity`, но не должен быть единственным местом для сохранения важных данных.

При configuration change старая `Activity` уничтожается и создаётся новая. Поэтому UI state нужно хранить в `ViewModel`, `savedInstanceState` / `SavedStateHandle` или persistent storage в зависимости от типа данных.

### Fragment lifecycle

![Fragment lifecycle callbacks](../assets/images/android/fragment_lifecycle_1.png)

![Fragment and view lifecycle](../assets/images/android/fragment_lifecycle_2.png)

`Fragment` имеет собственный lifecycle и отдельно lifecycle своей `View`. Это важно: `Fragment` object может ещё существовать, но его `View` уже может быть уничтожена.

Типичная последовательность callbacks: `onAttach()` -> `onCreate()` -> `onCreateView()` -> `onViewCreated()` -> `onStart()` -> `onResume()` -> `onPause()` -> `onStop()` -> `onDestroyView()` -> `onDestroy()` -> `onDetach()`.

Главное правило: подписки и работа с UI, которые завязаны на `View`, должны жить от `viewLifecycleOwner`, а не от самого `Fragment`. Иначе легко получить memory leak или callback в уничтоженную `View`.

`onDestroyView()` - место, где очищают `ViewBinding` и UI references. `onDestroy()` относится к `Fragment` как объекту, а не обязательно к его `View`.

### Application lifecycle

`Application` создаётся один раз на процесс приложения и обычно используется для инициализации глобальных зависимостей, DI, logging, analytics или AndroidX Startup-related инфраструктуры.

Основные callbacks: `onCreate()`, `onConfigurationChanged()`, `onLowMemory()`, `onTrimMemory()`. Метод `onTerminate()` почти не используется в реальном Android runtime и вызывается в основном в эмуляторе или тестовой среде.

`onCreate()` вызывается при старте процесса до запуска первых `Activity` / `Service` / `Receiver`, но `ContentProvider` может быть создан очень рано, ещё до `Application.onCreate()`. Поэтому часть библиотек исторически использовала provider-based auto init.

`onTrimMemory(level)` сообщает приложению, что системе нужно освободить память. Например, `TRIM_MEMORY_UI_HIDDEN` означает, что UI ушёл в фон и можно освободить UI-related ресурсы.

### Что из `onStop()` или `onDestroy()` может не вызваться?

Если процесс приложения убит системой в фоне, `Activity` может не получить обычный полный набор финальных callbacks. В частности, `onDestroy()` не гарантирован как место для сохранения критически важных данных.

Надёжная логика сохранения должна происходить раньше: в lifecycle-aware state holder, repository, database/cache или через `onSaveInstanceState()` для небольшого transient UI state.

`onStop()` обычно вызывается, когда `Activity` полностью перестаёт быть видимой, но при жёстком завершении процесса нельзя строить архитектуру так, будто любой callback обязательно успеет выполниться.

**Главная мысль:** lifecycle callbacks помогают освобождать ресурсы и синхронизировать UI, но process death - отдельный сценарий, поэтому критические данные нельзя сохранять только в `onDestroy()`.

## Configuration changes

### Поворот экрана. Screen rotation

Screen rotation обычно приводит к configuration change: текущая `Activity` уничтожается и создаётся заново под новую конфигурацию.

Типичная последовательность для старой `Activity`: `onPause()` -> `onStop()` -> `onSaveInstanceState()` -> `onDestroy()`. Затем создаётся новая `Activity`: `onCreate()` -> `onStart()` -> `onRestoreInstanceState()` -> `onResume()`.

`ViewModel` переживает обычный configuration change, потому что привязан к `ViewModelStoreOwner`, а не к конкретному instance `Activity`. Но `ViewModel` не переживает process death: для восстановления после убийства процесса нужны `savedInstanceState`, `SavedStateHandle`, database/cache или другой persistent storage.

`onSaveInstanceState()` подходит для небольшого UI state, например selected tab, scroll position или text input. Не стоит складывать туда большие объекты, bitmap или данные, которые можно заново загрузить.

`android:configChanges` может запретить пересоздание `Activity` для выбранных изменений конфигурации, но тогда ответственность за ручную обработку изменений переходит на приложение. Это инструмент для специальных случаев, а не универсальный способ "починить" rotation.

### Как `ViewModel` переживает поворот экрана?

`ViewModel` переживает поворот экрана, потому что она хранится не внутри конкретного instance `Activity` / `Fragment`, а во `ViewModelStore`, связанном с `ViewModelStoreOwner`.

При rotation старая `Activity` уничтожается, создаётся новая, но если это обычный configuration change, система сохраняет `ViewModelStore` и новая `Activity` получает тот же instance `ViewModel` через `ViewModelProvider`.

`ViewModel` подходит для screen state, загруженных данных и ongoing UI logic, которые не нужно терять при пересоздании UI. Но `ViewModel` не является persistent storage и не переживает process death.

Для восстановления после process death нужны `SavedStateHandle`, `onSaveInstanceState()`, database, `DataStore`, cache или повторная загрузка данных из repository.

**Коротко:** `ViewModel` survives configuration changes because it is scoped to `ViewModelStoreOwner`, not to a single `Activity` instance, but it does not survive process death.

## Activity launch

### Launch Modes for Activity

Launch mode определяет, как `Activity` создаётся и переиспользуется в task/back stack. Обычно он указывается в `AndroidManifest.xml` через `android:launchMode`.

`standard` - default mode: каждый запуск создаёт новый instance `Activity` и кладёт его в back stack. В одном task может быть несколько instance одной `Activity`.

`singleTop` - если `Activity` уже находится на вершине back stack, новый instance не создаётся, а существующий получает `onNewIntent()`. Если она не на вершине, создаётся новый instance.

`singleTask` - `Activity` существует как единственный instance в своём task. Если такой instance уже есть, система доставляет `Intent` в него через `onNewIntent()` и очищает `Activity` выше него.

`singleInstance` - более строгий вариант `singleTask`: `Activity` находится в отдельном task и другие `Activity` не добавляются в этот task. В modern Android встречается редко.

На практике launch modes используют осторожно: они сильно влияют на back stack, deep links, notifications и UX кнопки Back. Для большинства экранов подходит `standard`, а `singleTop` часто полезен для экранов, которые могут получить новый `Intent` сверху.

### Intent flags для запуска Activity

`FLAG_ACTIVITY_NEW_TASK`, `FLAG_ACTIVITY_SINGLE_TOP` и `FLAG_ACTIVITY_CLEAR_TOP` - intent flags, которые управляют запуском `Activity` и back stack на уровне конкретного `Intent`.

`FLAG_ACTIVITY_NEW_TASK` запускает `Activity` в новом task или переиспользует существующий task, если он подходит по affinity. Часто нужен при запуске `Activity` из non-Activity `Context`.

`FLAG_ACTIVITY_SINGLE_TOP` не создаёт новый instance, если нужная `Activity` уже находится на top текущего task. Вместо этого существующий instance получает новый `Intent` через `onNewIntent()`.

`FLAG_ACTIVITY_CLEAR_TOP` ищет существующий instance `Activity` в текущем task. Если он найден, все `Activity` выше него удаляются, а `Intent` доставляется найденной `Activity`. В зависимости от `launchMode` и flags существующий instance может получить `onNewIntent()` или быть пересоздан.

**Коротко:** `launchMode` задаёт default-поведение в manifest, а intent flags позволяют переопределить запуск для конкретного `Intent`.
