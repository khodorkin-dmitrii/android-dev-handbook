# Android Components

Компоненты Android-приложения - это точки входа, через которые система или другое приложение могут создать приложение либо обратиться к нему. Процесс может быть запущен ради `Activity`, `Service`, `BroadcastReceiver` или `ContentProvider`, поэтому инициализация не должна исходить из того, что пользователь сначала открыл экран.

## Основные компоненты

### Компоненты Android-приложения

Четыре основных компонента - `Activity`, `Service`, `BroadcastReceiver` и `ContentProvider`. У каждого своя задача и жизненный цикл. Activity, service и provider объявляются в `AndroidManifest.xml`; receiver можно объявить в манифесте или зарегистрировать во время выполнения.

Доступность компонента для других приложений зависит от intent filters, permissions и настройки `android:exported`. Внутренние компоненты следует оставлять неэкспортируемыми, а все данные, поступающие в экспортируемые компоненты, - проверять.

### Activity

`Activity` - основная точка входа для взаимодействия с пользователем. Она владеет окном, в котором приложение показывает UI, но не обязана соответствовать ровно одному экрану.

В современных приложениях одна `Activity` часто служит контейнером для навигации на Fragment или Compose. Система управляет ею через lifecycle callbacks и может уничтожить и пересоздать после изменения конфигурации или завершения процесса. Поэтому UI-состояние должно храниться у подходящего state holder и при необходимости восстанавливаться.

Состояния жизненного цикла и границы восстановления разобраны в статье [Activity, Fragment & Lifecycle](activity-fragment-lifecycle.md).

### Service

`Service` - компонент без собственного UI. Он подходит для работы, которая должна существовать независимо от экрана, или для предоставления API другим компонентам через binding.

**Важно:** service не является фоновым потоком. Его lifecycle callbacks по умолчанию выполняются в main thread, поэтому блокирующую или CPU-intensive работу нужно переносить на подходящий coroutine dispatcher, worker или executor.

Started и bound описывают способ управления service и продолжительность его жизни. Foreground означает видимый пользователю режим выполнения с уведомлением. Эти понятия не исключают друг друга: один service может одновременно быть started, bound и foreground.

#### Started service

Started service запускается через `startService()` или, когда foreground execution разрешён и необходим, через `startForegroundService()`. Система вызывает `onStartCommand()`, после чего service может продолжать работу даже после уничтожения запустившего его компонента.

Он должен остановить себя через `stopSelf()` либо быть остановлен через `stopService()`. Не следует использовать service как универсальный способ удерживать приложение в фоне. Современный Android ограничивает фоновое выполнение; для отложенной гарантированной работы обычно лучше подходит `WorkManager`.

Подробнее о `WorkManager`, foreground services, Doze и ограничениях фонового выполнения см. в статье [Background Work & System Behavior](background-work-system-behavior.md).

#### Bound service

Bound service предоставляет client-server interface. Компонент вызывает `bindService()` с `ServiceConnection`; service получает `onBind()` и возвращает `IBinder`, через который клиент с ним взаимодействует.

Purely bound service обычно существует, пока к нему привязан хотя бы один клиент. Вызовы bind и unbind нужно связывать с жизненным циклом клиента - часто с `onStart()` / `onStop()`, если соединение требуется только пока `Activity` видима.

Если service и клиент находятся в одном процессе, custom `Binder` может напрямую предоставлять API сервиса:

```kotlin
class PlaybackService : Service() {
    inner class LocalBinder : Binder() {
        fun getService(): PlaybackService = this@PlaybackService
    }

    private val binder = LocalBinder()

    override fun onBind(intent: Intent): IBinder = binder

    fun play() {
        // Запустить воспроизведение в подходящем execution context.
    }
}
```

Флаг `Context.BIND_AUTO_CREATE` создаёт service при подключении первого клиента, если тот ещё не запущен. Для взаимодействия между процессами используют `Messenger` для последовательных сообщений или AIDL, когда действительно нужен типизированный конкурентный IPC-контракт. Оба варианта усложняют работу с lifecycle, ошибками и thread safety.

Service может быть одновременно started и bound. Тогда отключение последнего клиента его не остановит: started lifetime также нужно завершить через `stopSelf()` или `stopService()`.

Для binding используй explicit `Intent`. Если service доступен только внутри приложения, укажи `android:exported="false"`.

### BroadcastReceiver

`BroadcastReceiver` позволяет приложению реагировать на broadcasts от системы или других приложений. Это короткоживущая точка входа, а не место для длительной работы.

`onReceive()` выполняется в main thread и должен быстро завершаться. `goAsync()` позволяет закончить короткую асинхронную работу после возврата из `onReceive()`, но не снимает ограничение по времени. Более длительную или отложенную работу следует передавать в `WorkManager`; foreground service подходит только для видимой пользователю задачи, когда платформа разрешает его запуск.

Receiver можно зарегистрировать в манифесте или во время выполнения. Нужно учитывать ограничения implicit broadcasts, permissions и exported/non-exported flags. Если Intent может прийти от другого приложения, его данные следует считать недоверенными.

### ContentProvider

`ContentProvider` предоставляет структурированные данные через URI-based API. Клиенты обращаются к нему через `ContentResolver`, независимо от того, хранятся ли данные в базе, файлах или другом источнике.

Типичные примеры - `ContactsProvider`, `MediaStore` и `FileProvider`. Provider может быть точкой входа и инициализироваться до `Application.onCreate()`, поэтому в нём следует избегать тяжёлой работы при старте. Если provider экспортирован, чувствительные операции нужно защищать узкими URI permissions или явными permissions.

## Передача данных

### Intent: explicit vs implicit

Explicit `Intent` называет целевой компонент и обычно используется для внутренней навигации или взаимодействия с service.

```kotlin
val intent = Intent(this, DetailsActivity::class.java)
    .putExtra("item_id", itemId)
startActivity(intent)
```

Implicit `Intent` описывает действие. Android находит подходящий компонент по intent filters. Используй chooser, когда получателя должен выбрать пользователь, и проверяй возможность обработки Intent, если подходящего компонента может не оказаться.

```kotlin
val intent = Intent(Intent.ACTION_SEND).apply {
    type = "text/plain"
    putExtra(Intent.EXTRA_TEXT, "Hello, world!")
}
startActivity(Intent.createChooser(intent, "Share"))
```

### Bundle

`Bundle` - key-value контейнер для Intent extras, Fragment arguments, `onSaveInstanceState()` и интеграции с `SavedStateHandle`. Он поддерживает primitives, `String`, `Parcelable`, `Serializable`, а также некоторые массивы и коллекции.

Bundle передаётся через Binder и не рассчитан на большие графы объектов. Объёмные данные могут привести к `TransactionTooLargeException`. Вместо них лучше передать стабильный идентификатор и загрузить данные из repository, database или cache.

### Serializable vs Parcelable

`Serializable` - универсальный Java-механизм сериализации. Он удобен в простых случаях, но обычно требует больше работы во время выполнения и создаёт больше объектов.

`Parcelable` - Android-формат для IPC и значений внутри `Intent` или `Bundle`. Kotlin-плагин `@Parcelize` генерирует реализацию и избавляет от большей части boilerplate.

Если объект действительно нужно передать между Android-компонентами, обычно стоит выбрать `Parcelable`, но payload должен оставаться небольшим. Стабильный идентификатор чаще оказывается более надёжным контрактом, чем передача целого domain object.

## Связанные темы

- [Activity, Fragment & Lifecycle](activity-fragment-lifecycle.md)
- [Background Work & System Behavior](background-work-system-behavior.md)
- [Context & Resources](context-resources.md)
- [Storage](storage.md)
