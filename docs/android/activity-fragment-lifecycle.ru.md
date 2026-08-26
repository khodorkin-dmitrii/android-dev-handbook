# Activity, Fragment & Lifecycle

Lifecycle в Android описывает, как компоненты создаются, становятся видимыми, уходят в фон, уничтожаются и восстанавливают состояние. На практике важно не только помнить порядок callbacks, но и понимать, какому owner принадлежит state или ресурс.

## Activity и Fragment

### Activity lifecycle

![Activity lifecycle](../assets/images/android/activity-lifecycle.png)

`Activity` lifecycle описывает, как экран проходит состояния создания, видимости, взаимодействия с пользователем, ухода в фон и уничтожения.

Базовая последовательность callbacks:

```text
onCreate() -> onStart() -> onResume()
                       ...
onPause() -> onStop() -> onDestroy()
```

При возврате после `onStop()` перед `onStart()` может быть вызван `onRestart()`.

- `onCreate()` - инициализация экрана, восстановление небольшого saved state, подключение dependency entry points и получение `ViewModel`.
- `onStart()` - `Activity` становится видимой.
- `onResume()` - `Activity` находится на переднем плане и готова к interaction.
- `onPause()` - `Activity` теряет фокус, но может оставаться частично видимой.
- `onStop()` - `Activity` больше не видна.
- `onDestroy()` - текущий instance `Activity` уничтожается.

Не используйте `onDestroy()` как единственное место для сохранения важных данных. Процесс может быть завершён без финального cleanup callback.

При configuration change текущий instance `Activity` обычно уничтожается и создаётся новый. State стоит хранить по его lifetime:

- `ViewModel` - screen state, который должен пережить configuration change;
- `SavedStateHandle` / `onSaveInstanceState()` - небольшой restorable UI state;
- repository, database, DataStore, cache или backend - durable data.

### Fragment lifecycle

![Fragment lifecycle callbacks](../assets/images/android/fragment_lifecycle_1.png)

![Fragment and view lifecycle](../assets/images/android/fragment_lifecycle_2.png)

У `Fragment` есть два связанных lifecycle: lifecycle самого Fragment object и lifecycle его `View`. Fragment может оставаться жив после `onDestroyView()`.

Типичная последовательность callbacks:

```text
onAttach() -> onCreate() -> onCreateView() -> onViewCreated()
-> onStart() -> onResume()
-> onPause() -> onStop() -> onDestroyView() -> onDestroy() -> onDetach()
```

UI work, связанная с Fragment view, должна использовать `viewLifecycleOwner`, а не lifecycle самого Fragment. Это особенно важно для Flow collection, listeners, adapters и ссылок на views.

`onDestroyView()` - место, где нужно очищать `ViewBinding` и другие view references. `onDestroy()` относится к Fragment object и может произойти позже.

### Application lifecycle

`Application` создаётся один раз на процесс приложения и обычно используется для process-wide initialization: DI, logging, analytics и AndroidX Startup-related infrastructure.

Основные callbacks: `onCreate()`, `onConfigurationChanged()`, `onLowMemory()` и `onTrimMemory()`. `onTerminate()` не является обычным production callback завершения процесса и в основном относится к emulator или test environment.

Важный startup nuance: объект `Application` уже существует до `Application.onCreate()`, а manifest `ContentProvider` может быть инициализирован ещё до `Application.onCreate()`. Поэтому некоторые библиотеки исторически использовали provider-based auto initialization.

`onTrimMemory(level)` сообщает приложению, что системе нужно освободить память. Например, `TRIM_MEMORY_UI_HIDDEN` означает, что UI ушёл в фон и можно освободить UI-related resources.

### Что из `onStop()` или `onDestroy()` может не вызваться?

Если процесс приложения убит системой в фоне, `Activity` может не получить обычный полный набор финальных callbacks. В частности, `onDestroy()` не гарантирован как место для сохранения критически важных данных.

Надёжная логика сохранения должна происходить раньше: в lifecycle-aware state holder, repository, database/cache или через `onSaveInstanceState()` для небольшого transient UI state.

`onStop()` обычно вызывается, когда `Activity` полностью перестаёт быть видимой, но при жёстком завершении процесса нельзя строить архитектуру так, будто любой финальный callback обязательно успеет выполниться.

Главное различие:

- lifecycle callbacks координируют живой component;
- process death завершает весь процесс и требует восстановления из saved или durable state.

## Configuration changes

### Поворот экрана. Screen rotation

Screen rotation обычно приводит к configuration change: текущая `Activity` пересоздаётся, чтобы Android мог применить ресурсы для новой конфигурации.

Типичный transition включает pause/stop и уничтожение старой activity, после чего новая получает `onCreate()`, `onStart()` и `onResume()`. `onSaveInstanceState()` и `onRestoreInstanceState()` участвуют в сохранении небольшого UI state, но application logic не должна зависеть от одного жёстко заданного порядка всех callbacks.

`ViewModel` переживает обычный configuration change, потому что привязан к `ViewModelStoreOwner`, а не к конкретному instance `Activity`. Но `ViewModel` не переживает process death: для восстановления после убийства процесса нужны `SavedStateHandle`, saved instance state, database/cache или другой persistent source.

`onSaveInstanceState()` подходит для небольшого UI state: selected tab, scroll position, text input или ID, нужный для восстановления контента. Не стоит складывать туда большие объекты, bitmap или данные, которые можно заново загрузить.

`android:configChanges` может запретить пересоздание `Activity` для выбранных configuration changes, но тогда ответственность за ручную обработку изменений переходит на приложение. Это инструмент для специальных случаев, а не универсальный способ “починить” rotation.

### Как `ViewModel` переживает поворот экрана?

`ViewModel` переживает screen rotation, потому что хранится не внутри конкретного instance `Activity` / `Fragment`, а во `ViewModelStore`, связанном с `ViewModelStoreOwner`.

При rotation старая `Activity` уничтожается, создаётся новая, но если это обычный configuration change, Android сохраняет `ViewModelStore`, и новый owner получает тот же instance `ViewModel` через `ViewModelProvider`.

`ViewModel` подходит для screen state, загруженных данных и ongoing UI logic, которые не нужно терять при пересоздании UI. Но `ViewModel` не является persistent storage и не переживает process death.

Для восстановления после process death нужны `SavedStateHandle`, `onSaveInstanceState()`, database, DataStore, cache или повторная загрузка данных из repository.

## Activity launch

### Launch Modes for Activity

Launch mode определяет, как `Activity` создаётся или переиспользуется в task/back stack. Обычно он указывается в `AndroidManifest.xml` через `android:launchMode`.

- `standard` - default mode: каждый запуск создаёт новый instance `Activity` и кладёт его в back stack.
- `singleTop` - если `Activity` уже находится на вершине back stack, новый instance не создаётся, а существующий получает `onNewIntent()`. Если она не на вершине, создаётся новый instance.
- `singleTask` - `Activity` существует как единственный instance в своём task. Если такой instance уже есть, система доставляет `Intent` в него через `onNewIntent()` и очищает activities выше него.
- `singleInstance` - более строгий вариант `singleTask`: `Activity` находится в отдельном task и другие activities не добавляются в этот task. В modern Android встречается редко.

Launch modes влияют на back stack, deep links, notifications и UX кнопки Back, поэтому их нужно использовать осторожно. Для большинства экранов подходит `standard`, а `singleTop` полезен, когда activity на top должна получить новый `Intent`, а не создавать ещё один instance.

### Intent flags для запуска Activity

Intent flags управляют запуском `Activity` и back stack behavior для конкретного `Intent`.

- `FLAG_ACTIVITY_NEW_TASK` запускает `Activity` в новом task или переиспользует существующий task, если он подходит по affinity. Часто нужен при запуске `Activity` из non-Activity `Context`.
- `FLAG_ACTIVITY_SINGLE_TOP` не создаёт новый instance, если нужная `Activity` уже находится на top текущего task. Вместо этого существующий instance получает новый `Intent` через `onNewIntent()`.
- `FLAG_ACTIVITY_CLEAR_TOP` ищет существующий instance `Activity` в текущем task. Если он найден, все activities выше него удаляются, а `Intent` доставляется найденной `Activity`. В зависимости от `launchMode` и flags существующий instance может получить `onNewIntent()` или быть пересоздан.

`launchMode` задаёт default behavior в manifest, а intent flags настраивают launch behavior для конкретного `Intent`.

## Связанные темы

- [Android Components](components.md)
- [Основные системные службы Android](android-system-services.md)
- [Lifecycle-aware Collection](../coroutines-flow/lifecycle-aware-collection.md)
- [UI State Architecture](../architecture/ui-state.md)
- [Context & Resources](context-resources.md)
