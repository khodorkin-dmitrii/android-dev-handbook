# Storage

Choose storage by the shape and ownership of the data: Room for relational records, DataStore for small settings, app-specific files for data used only by the app, and shared storage for user-visible media or documents. Persistence across app restarts is different from temporary UI state.

## SQLite and Room

### SQLiteOpenHelper

![SQLite cheat sheet](../assets/images/android/sql_cheat_sheet.png)

`SQLiteOpenHelper` manages creation, opening, and version upgrades when an app works directly with `SQLiteDatabase`. A subclass specifies a database name and version and implements `onCreate()` and `onUpgrade()`. Constructing the helper does not open the database; the first `getReadableDatabase()` or `getWritableDatabase()` call does.

Use Room for most new relational databases. It still uses SQLite, but validates supported SQL queries at compile time and provides DAOs and migration support. Direct SQLite remains relevant in existing code and when lower-level control is needed.

### `onCreate()` / `onUpgrade()`

`onCreate()` initializes a new database, typically creating tables and indexes. `onUpgrade()` runs when an existing database has an older version than the version requested by the helper. The default downgrade behavior throws unless `onDowngrade()` is implemented.

Plan a migration path from every supported old version: a user may skip several app releases. Preserve data unless it is explicitly disposable; dropping and recreating user tables loses it. Test upgrades using real schemas from previous releases. Changing the code for a migration that has already run will not rerun it on upgraded devices. Room has its own explicit and automatic migration mechanisms; do not confuse them with `SQLiteOpenHelper.onUpgrade()`.

### `getReadableDatabase()` / `getWritableDatabase()`

`getWritableDatabase()` opens a read/write database or throws if this is impossible. `getReadableDatabase()` generally returns the same read/write database but can fall back to read-only, for example when the disk is full. Do not assume its result is writable.

Opening may create or upgrade a database and block, so call these methods off the main thread. Reuse an appropriately scoped helper instead of opening and closing it for every query; close it when its owner is finished. Group related writes in a transaction to preserve consistency.

### Room

Room models tables with `@Entity`, database operations with `@Dao`, and the database entry point with `@Database`. It suits offline records, caches, history, and other structured data with queries and relationships. It does not remove the need to design indexes and migrations.

Room disallows main-thread database access by default. Use `suspend` DAO functions for one-shot operations and `Flow` for observable queries; Room executes these asynchronous queries off the main thread. For multiple related writes, use a transaction. Never use destructive migration for data users expect to keep.

## Preferences

### DataStore

DataStore stores small persistent values with coroutines and `Flow`. Preferences DataStore uses keys without a fixed schema; Proto DataStore stores typed messages defined with Protocol Buffers. Reads expose a `Flow`; Preferences DataStore uses `edit()` and Proto DataStore uses `updateData()` for transactional updates.

Use it for settings and small pieces of app state, such as a theme or onboarding flag. Use Room for relational data, large datasets, or queries over individual records. Keep one DataStore instance per file within a process; if multiple processes must access the same file, use the multiprocess variant consistently. DataStore itself is not an encryption mechanism.

### SharedPreferences

`SharedPreferences` stores a small set of key-value settings and is common in older Android code. `apply()` updates the in-memory state immediately and schedules disk persistence without reporting failure. `commit()` writes synchronously and returns a success flag. Avoid `commit()` on the main thread; pending `apply()` disk writes can also stall lifecycle transitions and contribute to ANRs.

For new settings, prefer DataStore. When migrating an existing preferences file, use DataStore migration support and verify defaults and key mapping. Neither plain `SharedPreferences` nor DataStore makes secrets secure by itself; choose a suitable protected storage design for sensitive data.

## Files and shared storage

Store files needed only by your app in app-specific storage. Use `filesDir` for persistent private files and `cacheDir` for disposable cache; the system may remove cache files, and app-specific files are generally removed on uninstall. App-specific external storage is also available for large app-owned files, but its volume may be unavailable.

To publish photos and videos outside your app, use `MediaStore`; to let users select existing photos or videos, use the system photo picker. For documents chosen or created by the user, use the Storage Access Framework. Treat returned `content://` URIs as handles to content rather than assuming a filesystem path. Access rules and permissions depend on the operation and Android version.

See the [Android storage overview](https://developer.android.com/training/data-storage) for API selection and the [Android Keystore guidance](https://developer.android.com/privacy-and-security/keystore) for cryptographic keys.
