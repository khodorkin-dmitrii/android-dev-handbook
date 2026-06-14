# Storage

Storage in Android includes low-level SQLite, Room as a modern abstraction, DataStore for settings and legacy `SharedPreferences`.

## SQLite and Room

### SQLiteOpenHelper

![SQLite cheat sheet](../assets/images/android/sql_cheat_sheet.png)

`SQLiteOpenHelper` - a basic Android helper for manually creating, opening and migrating a SQLite database.

It is used when an app works directly with `SQLiteDatabase` and SQL queries: creates tables, runs query/insert/update/delete operations and manages schema versions.

A subclass usually defines the database name and version, and implements `onCreate()` and `onUpgrade()`.

**Important:** the helper object itself is created quickly, but the database is actually opened only when `getReadableDatabase()` or `getWritableDatabase()` is called.

In modern Android, Room is usually preferred because it provides compile-time SQL validation, DAO, migrations and less boilerplate.

**In short:** `SQLiteOpenHelper` is a low-level helper for managing SQLite database creation and migrations; Room is usually preferred for new production code.

### `onCreate()` / `onUpgrade()`

`onCreate()` is called when the database is created for the first time. This is usually where tables, indexes, triggers and, when needed, initial data are created.

`onUpgrade()` is called when the database version in code becomes higher than the version of the existing database on the device.

The main task of `onUpgrade()` is to carefully migrate the schema and preserve user data. A simple `DROP TABLE` + `CREATE TABLE` is acceptable only for cache/test data or when data loss is intentionally allowed.

Migrations must account for all old versions: a user may update from version 1 directly to version 5.

**Important:** after release, you cannot simply "rewrite" an already published migration step and expect it to run again on devices where it has already been applied.

**In short:** `onCreate()` creates the initial schema, `onUpgrade()` migrates an existing database between versions and must be written carefully to avoid data loss.

### `getReadableDatabase()` / `getWritableDatabase()`

`getReadableDatabase()` and `getWritableDatabase()` return `SQLiteDatabase`, but differ by opening intent.

`getWritableDatabase()` opens the database for reading and writing. On first open, it may call `onCreate()`, `onUpgrade()` and `onOpen()`.

`getReadableDatabase()` usually returns the same read/write database object when possible. But if there is a problem, for example full disk, it may return a read-only database.

Both methods may take a long time, especially when creating or migrating the database, so they should not be called on the main thread.

After successful opening, the database object is cached by the helper. Usually, you do not need to open/close the database for every small operation, but you should close the helper/database when they are no longer needed.

For several related operations, use a transaction to preserve consistency and improve performance.

**In short:** `getWritableDatabase()` opens a read/write database, `getReadableDatabase()` may return read-only in fallback cases, and both can block during open or migration.

### Room

Room - a Jetpack persistence library on top of SQLite that provides a more convenient and safer API for a local database.

Main parts of Room: `@Entity` describes a table, `@Dao` describes queries/insert/update/delete operations, and `@Database` connects entities and DAO in a database class.

Room validates SQL at compile time, reduces boilerplate and integrates well with Kotlin Coroutines and `Flow`.

Room fits structured relational data: cache, offline-first data, user-generated content, history and relational entities.

**Important:** Room still uses SQLite under the hood, so schema design, indexes, transactions and migrations still matter.

By default, Room does not allow database operations on the main thread, and that is good: queries should go through suspend functions, `Flow` or a background dispatcher.

**In short:** Room is the recommended higher-level abstraction over SQLite for structured local data, with DAO, entities, compile-time SQL checks and migration support.

## Preferences

### DataStore

DataStore - a Jetpack API for storing small persistent data asynchronously and more safely than `SharedPreferences`.

There are two main variants: Preferences DataStore for key-value data without a predefined schema, and Proto DataStore for typed objects through Protocol Buffers.

DataStore uses coroutines and `Flow`, so reads usually look like a `Flow` of settings, while writes are performed through suspend `updateData()` / `edit()`.

It works well for user settings, feature flags, onboarding flags, last selected option and other small preferences.

DataStore is not intended for large relational data, partial updates of complex structures or referential integrity. Room is better for that.

**Important:** for one DataStore file, there should be one instance in the process, usually through a delegate or DI singleton.

**In short:** DataStore is a modern asynchronous replacement for `SharedPreferences` for small key-value or typed settings, while Room is better for complex structured data.

### SharedPreferences

`SharedPreferences` - an old Android API for storing a small set of key-value data in an XML file.

It fits simple primitives and `String`: flags, small settings, selected mode and first launch marker.

For writing, there are `apply()` and `commit()`. `apply()` writes changes asynchronously and does not return a result; `commit()` writes synchronously and returns boolean success.

`commit()` can block the calling thread, so it should not be used on the main thread unless necessary.

`SharedPreferences` is not intended for large data, lists of complex objects, relational data or frequent concurrent writes.

`SharedPreferences` does not encrypt data by itself. Sensitive data needs a separate secure storage approach, not a regular preferences file.

In modern Android, DataStore is usually chosen for new settings, but `SharedPreferences` is still common in legacy code.

**In short:** `SharedPreferences` is a simple legacy key-value storage API; use it for small preferences, prefer DataStore for modern asynchronous settings storage.
