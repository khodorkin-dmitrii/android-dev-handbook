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

`Service` - a component without its own UI, intended for background work or for exposing an API to other components through binding.

**Important:** `Service` does not mean a separate thread. Service code runs on the main thread by default, so heavy work must be moved to a coroutine, worker or thread pool.

Main variants: a started service is launched to perform a task; a bound service lives while a client is bound to it; a foreground service shows a persistent notification and is used for work the user should be aware of.

In modern Android, `WorkManager` is often preferable to a manual background `Service` for deferred and reliable background work.

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
