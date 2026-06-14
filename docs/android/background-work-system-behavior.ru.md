# Background Work & System Behavior

Android ограничивает фоновую работу, чтобы экономить батарею, защищать пользователя и сохранять предсказуемость системы.

## Background work

### Doze Mode

Doze Mode - режим энергосбережения Android, который ограничивает background activity, когда устройство долго не используется, лежит неподвижно и экран выключен.

В Doze система откладывает обычные background jobs, network access, sync и alarms. Периодически открываются maintenance windows, где приложения могут выполнить часть отложенной работы.

Для задач, которые должны выполниться надёжно, лучше использовать `WorkManager` / `JobScheduler`, а не raw background thread. Для точного времени существуют alarms, но с ограничениями и осторожным использованием.

**Коротко:** Doze protects battery by batching and delaying background work, so apps should use system-aware APIs instead of assuming background execution is always available.

### WorkManager

`WorkManager` - Jetpack API для deferrable background work, который должен выполниться гарантированно при соблюдении constraints.

Он подходит для задач вроде upload logs, sync data, cleanup, retryable network work. Можно задавать constraints: network, charging, battery not low, storage not low.

`WorkManager` поддерживает one-time и periodic work, chaining, retries, backoff policy и сохранение задач после перезапуска процесса или устройства.

**Важно:** `WorkManager` не предназначен для точных задач "выполнить ровно в 12:00" и не заменяет foreground service для немедленной user-visible работы.

**Коротко:** `WorkManager` is the recommended API for reliable deferrable background work with constraints and retry support.

### Foreground Service

Foreground Service - это `Service` для работы, о которой пользователь должен знать прямо сейчас. Он обязан показывать persistent notification.

Типичные сценарии: navigation, media playback, active location tracking, ongoing call, connected device operation, long-running user-initiated task.

Foreground Service не означает отдельный thread: тяжёлую работу всё равно нужно выполнять вне main thread.

В новых версиях Android есть дополнительные ограничения: нужно объявлять foreground service type, запрашивать соответствующие permissions и учитывать ограничения запуска foreground service из background.

**Коротко:** foreground service is for immediate user-visible ongoing work, while `WorkManager` is better for deferrable reliable background tasks.

### Background restrictions

Android постепенно усиливал background restrictions, чтобы экономить батарею и защищать пользователя от скрытой фоновой активности.

Ограничения касаются background services, implicit broadcasts, background location, exact alarms, foreground service launch, jobs, network access и battery optimizations.

Практический подход: выбирать API по типу задачи. Для отложенной гарантированной работы - `WorkManager`. Для точных alarms - `AlarmManager` с учётом permissions/ограничений. Для активной видимой пользователю работы - foreground service. Для push-triggered событий - FCM, но тоже с ограничениями.

Нельзя проектировать Android-приложение так, будто оно может бесконечно работать в фоне. Система может остановить процесс, отложить работу или ограничить доступ к ресурсам.
