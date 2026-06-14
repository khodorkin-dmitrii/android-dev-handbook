# Android Components

Android-приложение строится вокруг компонентов, через которые система или пользователь могут войти в приложение.

## Основные компоненты

### Компоненты Android приложения

Четыре основных app components: `Activity`, `Service`, `BroadcastReceiver` и `ContentProvider`. Они объявляются в `AndroidManifest.xml` и имеют разные жизненные циклы.

`Activity` отвечает за экран и взаимодействие с пользователем. `Service` выполняет фоновые или bound-задачи без UI. `BroadcastReceiver` принимает события. `ContentProvider` управляет доступом к данным через общий контракт.

Эти компоненты могут быть entry points приложения: процесс не всегда создаётся из-за запуска `Activity`. Например, он может быть создан из-за `BroadcastReceiver`, `Service` или `ContentProvider`.

### Activity

`Activity` - компонент, представляющий экран с UI и основной entry point для взаимодействия пользователя с приложением.

Одна `Activity` обычно отвечает за один user-facing flow или служит host для нескольких экранов, fragments или Compose navigation. В современных приложениях часто встречается Single Activity approach, где одна `Activity` содержит `NavHost`, а конкретные экраны реализованы как fragments или composables.

`Activity` объявляется в `AndroidManifest.xml` и управляется системой через lifecycle callbacks.

### Service

`Service` - компонент без собственного UI, предназначенный для работы в фоне или предоставления API другим компонентам через binding.

**Важно:** `Service` не означает отдельный thread. Код service по умолчанию выполняется на main thread, поэтому тяжёлую работу нужно переносить в coroutine, worker или thread pool.

Основные варианты: started service запускается для выполнения задачи; bound service живёт, пока к нему привязан клиент; foreground service показывает persistent notification и используется для задач, о которых пользователь должен знать.

В современном Android для отложенной и гарантированной фоновой работы часто предпочтительнее `WorkManager`, а не ручной background `Service`.

### BroadcastReceiver

`BroadcastReceiver` получает broadcast events от системы или других приложений. Это entry point, через который приложение может отреагировать на событие вне обычного user flow.

`BroadcastReceiver` должен выполнять короткую работу. Для длительной операции лучше делегировать задачу в `WorkManager`, `JobScheduler` или foreground service, если сценарий действительно требует foreground execution.

Broadcast может быть system-wide или app-specific. При регистрации receiver важно учитывать security: exported/non-exported, permissions и ограничения implicit broadcasts в новых версиях Android.

### ContentProvider

`ContentProvider` управляет доступом к структурированным данным приложения и может предоставлять эти данные другим приложениям через URI-based API.

Типичные примеры: `ContactsProvider`, `MediaStore`, `FileProvider`. Provider может хранить данные в SQLite, файлах, сети или другом storage, но наружу отдаёт единый контракт через `ContentResolver`.

`ContentProvider` является одним из entry points приложения и может быть создан системой очень рано, иногда до `Application.onCreate()`. Поэтому в provider-коде нужно осторожно относиться к тяжёлой инициализации.

## Передача данных

### Intent: explicit vs implicit

Explicit Intent явно указывает компонент, который нужно запустить. Обычно используется для навигации внутри приложения.

```kotlin
val intent = Intent(this, DetailsActivity::class.java)
intent.putExtra("item_id", itemId)
startActivity(intent)
```

Implicit Intent описывает действие, а не конкретный компонент. Система выбирает подходящее приложение или компонент через intent filters.

```kotlin
val intent = Intent(Intent.ACTION_SEND)
intent.type = "text/plain"
intent.putExtra(Intent.EXTRA_TEXT, "Hello, world!")
startActivity(Intent.createChooser(intent, "Share"))
```

**Коротко:** explicit intent targets a specific component, implicit intent describes an action and lets Android resolve who can handle it.

### Bundle

`Bundle` - контейнер key-value данных, который часто используется для передачи параметров между Android-компонентами и сохранения небольшого состояния.

`Bundle` может хранить primitives, `String`, `Parcelable`, `Serializable` и некоторые массивы/коллекции поддерживаемых типов.

Типичные места использования: Intent extras, Fragment arguments, `onSaveInstanceState()`, `SavedStateHandle` interop.

**Важно:** `Bundle` не предназначен для больших данных. Для больших объектов лучше передавать id и загружать данные из repository, database или cache.

### Serializable vs Parcelable

`Serializable` - стандартный Java-механизм сериализации. Он простой в использовании, но часто медленнее и создаёт больше runtime overhead, потому что работает через reflection и промежуточные объекты.

`Parcelable` - Android-ориентированный механизм передачи объектов между компонентами, например через `Intent` или `Bundle`. Он обычно быстрее и лучше подходит для Android IPC/Bundle-сценариев, но требует явного описания того, как объект записывается и читается.

В Kotlin чаще используют `@Parcelize`, чтобы не писать boilerplate `Parcelable` вручную.

**Коротко:** `Serializable` проще, `Parcelable` быстрее и является предпочтительным вариантом для Android component communication.
