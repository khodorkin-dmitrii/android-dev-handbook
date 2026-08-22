# Android Components

An Android app is built around components through which the system or the user can enter the app.

## Core components

### Android app components

The four core app components are `Activity`, `Service`, `BroadcastReceiver` and `ContentProvider`. They are declared in `AndroidManifest.xml` and have different lifecycles.

`Activity` represents a screen and user interaction. `Service` performs background or bound work without UI. `BroadcastReceiver` receives events. `ContentProvider` manages access to data through a shared contract.

These components can be app entry points: a process is not always created because an `Activity` was launched. For example, it can be created because of a `BroadcastReceiver`, `Service` or `ContentProvider`.

### Activity

`Activity` - a component that represents a screen with UI and the main entry point for user interaction with the app.

One `Activity` usually owns one user-facing flow or acts as a host for several screens, fragments or Compose navigation. Modern apps often use the Single Activity approach, where one `Activity` contains a `NavHost`, and individual screens are implemented as fragments or composables.

`Activity` is declared in `AndroidManifest.xml` and managed by the system through lifecycle callbacks.

### Service

`Service` - a component without its own UI, intended for work that must be owned independently of a screen or for exposing an API to other components through binding.

**Important:** `Service` does not mean a separate thread. Service callbacks run on the main thread by default, so blocking or CPU-intensive work must be moved to a coroutine, worker or thread pool.

Started and bound describe how a service is controlled and how long it lives. Foreground describes a user-visible execution mode with a persistent notification. These concepts are not mutually exclusive: one service can be started, bound and foreground at the same time.

#### Started Service

A started service is launched with `startService()` or, when foreground execution is required, `startForegroundService()`. The system calls `onStartCommand()`, and the service can continue after the component that started it is destroyed.

A started service must stop itself with `stopSelf()` or be stopped with `stopService()`. It should not be used as a generic way to keep an app alive in the background. Modern Android restricts background service starts, and deferred reliable work is usually better handled by `WorkManager`.

See [Background Work & System Behavior](background-work-system-behavior.md) for `WorkManager`, foreground services, Doze and background execution limits.

#### Bound Service

A bound service provides a client-server interface. A component calls `bindService()` with a `ServiceConnection`; the service receives `onBind()` and returns an `IBinder` through which the client can call operations or exchange data.

A purely bound service normally exists while at least one client is bound. Multiple clients can bind at the same time. After the last client calls `unbindService()`, the system can destroy the service. Bind and unbind calls should be paired with an appropriate client lifecycle, commonly `onStart()` / `onStop()` when the connection is needed only while an `Activity` is visible.

For a service and client in the same process, a custom `Binder` can expose the service API directly:

```kotlin
class PlaybackService : Service() {
    inner class LocalBinder : Binder() {
        fun getService(): PlaybackService = this@PlaybackService
    }

    private val binder = LocalBinder()

    override fun onBind(intent: Intent): IBinder = binder

    fun play() {
        // Start playback on an appropriate execution context.
    }
}
```

The client receives the binder in `ServiceConnection.onServiceConnected()` and uses it until the connection is released. `Context.BIND_AUTO_CREATE` creates the service when the first client binds if it is not already running.

For communication across processes, use a `Messenger` for serialized message-based IPC or AIDL when a typed concurrent IPC contract is genuinely required. These approaches are more complex than a local binder and require careful error handling, lifecycle management and thread safety.

A service can also be both started and bound. In that case, unbinding the last client does not stop it: the started lifetime must still end through `stopSelf()` or `stopService()`, and the service is destroyed only after it is no longer started and has no bound clients.

Use an explicit `Intent` when binding. If the service is private to the application, declare it with `android:exported="false"` so other apps cannot bind to it.

### BroadcastReceiver

`BroadcastReceiver` receives broadcast events from the system or other apps. It is an entry point through which an app can react to an event outside the normal user flow.

`BroadcastReceiver` should do short work. For a long-running operation, delegate the task to `WorkManager`, `JobScheduler` or a foreground service if the scenario truly requires foreground execution.

A broadcast can be system-wide or app-specific. When registering a receiver, security matters: exported/non-exported state, permissions and implicit broadcast restrictions in newer Android versions.

### ContentProvider

`ContentProvider` manages access to structured app data and can expose that data to other apps through a URI-based API.

Typical examples are `ContactsProvider`, `MediaStore` and `FileProvider`. A provider may store data in SQLite, files, the network or another storage layer, but externally it exposes a unified contract through `ContentResolver`.

`ContentProvider` is one of the app entry points and can be created by the system very early, sometimes before `Application.onCreate()`. For that reason, provider code should be careful with heavy initialization.

## Passing data

### Intent: explicit vs implicit

An explicit `Intent` directly specifies the component to launch. It is usually used for navigation inside the app.

```kotlin
val intent = Intent(this, DetailsActivity::class.java)
intent.putExtra("item_id", itemId)
startActivity(intent)
```

An implicit `Intent` describes an action, not a specific component. The system chooses a suitable app or component through intent filters.

```kotlin
val intent = Intent(Intent.ACTION_SEND)
intent.type = "text/plain"
intent.putExtra(Intent.EXTRA_TEXT, "Hello, world!")
startActivity(Intent.createChooser(intent, "Share"))
```

**In short:** explicit intent targets a specific component; implicit intent describes an action and lets Android resolve who can handle it.

### Bundle

`Bundle` - a key-value data container often used to pass parameters between Android components and save small pieces of state.

`Bundle` can store primitives, `String`, `Parcelable`, `Serializable` and some arrays/collections of supported types.

Common usage points are Intent extras, Fragment arguments, `onSaveInstanceState()` and `SavedStateHandle` interop.

**Important:** `Bundle` is not designed for large data. For large objects, pass an id and load the data from a repository, database or cache.

### Serializable vs Parcelable

`Serializable` - the standard Java serialization mechanism. It is simple to use, but often slower and creates more runtime overhead because it works through reflection and intermediate objects.

`Parcelable` - an Android-oriented mechanism for passing objects between components, for example through `Intent` or `Bundle`. It is usually faster and better suited for Android IPC/Bundle scenarios, but requires explicitly describing how the object is written and read.

In Kotlin, `@Parcelize` is commonly used to avoid writing `Parcelable` boilerplate by hand.

**In short:** `Serializable` is simpler, while `Parcelable` is faster and is the preferred option for Android component communication.
