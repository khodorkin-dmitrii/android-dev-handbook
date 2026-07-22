# Android Keystore и безопасное хранение

Проектирование безопасного локального хранения начинается с решения о жизненном цикле данных, а не с выбора encryption API. Android Keystore усложняет извлечение криптографических ключей, но приложение по-прежнему отвечает за объем и срок хранения данных, корректное шифрование, сохранение ciphertext и metadata, а также восстановление при недоступности ключа или данных.

## Начните с решения о хранении

Перед сохранением чувствительных данных ответьте на вопросы:

- Нужно ли вообще хранить эти данные и как долго?
- Должны ли они переживать process death, logout, account switch или device migration?
- Нужно ли требовать device или biometric authentication для каждого использования?
- Можно ли снова получить данные после sign-in?
- Что должно произойти после key invalidation, backup restore или corruption?

> Самые безопасные чувствительные данные - те, которые приложение не хранит.

Для одноразовых серверных данных предпочтительны короткий срок хранения и повторная загрузка. Шифрование имеет смысл, когда persistence действительно нужна продукту, а не как оправдание бессрочного хранения каждого ответа.

## Android Keystore

Android Keystore хранит криптографические keys или non-exportable handles к ним. Код приложения запрашивает операции через стандартные Java Cryptography Architecture APIs, а key material остается вне процесса приложения и может быть привязан к secure hardware. Keystore не является общей encrypted database: данные приложения обычно хранятся отдельно как ciphertext.

Следующий helper для API 23+ создает или получает AES key, ограниченный операциями AES-GCM encryption и decryption:

```kotlin
private const val KEY_ALIAS = "local-data-v1"

private fun getOrCreateKey(): SecretKey {
    val keyStore = KeyStore.getInstance("AndroidKeyStore").apply {
        load(null)
    }

    (keyStore.getKey(KEY_ALIAS, null) as? SecretKey)?.let { return it }

    return KeyGenerator.getInstance(
        KeyProperties.KEY_ALGORITHM_AES,
        "AndroidKeyStore",
    ).run {
        init(
            KeyGenParameterSpec.Builder(
                KEY_ALIAS,
                KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT,
            )
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .setKeySize(256)
                .build(),
        )
        generateKey()
    }
}
```

Поддержка algorithms, key sizes, authentication options и hardware properties зависит от Android version и устройства. Проверяйте обязательные capabilities и определите fallback либо unsupported-device policy на уровне продукта.

## Ключевой материал и зашифрованные данные приложения

Обычная схема выглядит так:

1. Создать или получить Keystore-backed key.
2. Зашифровать сериализованные данные с помощью authenticated encryption.
3. Сохранить ciphertext и несекретные metadata, например IV и версию формата.
4. Получить handle ключа и расшифровать данные при необходимости.

Ciphertext и IV не обязаны быть секретными как ключ, но их нельзя случайно обрезать или перепутать между записями. В GCM значение IV не должно повторяться с одним ключом. Authentication tag, входящий в результат Java cipher, обнаруживает подмену; шифрования без контроля целостности для большинства данных недостаточно.

В этом компактном примере provider создает новый IV для каждой операции encryption:

```kotlin
data class EncryptedValue(
    val iv: ByteArray,
    val ciphertext: ByteArray,
)

fun encrypt(value: String): EncryptedValue {
    val cipher = Cipher.getInstance("AES/GCM/NoPadding")
    cipher.init(Cipher.ENCRYPT_MODE, getOrCreateKey())

    return EncryptedValue(
        iv = cipher.iv,
        ciphertext = cipher.doFinal(value.toByteArray(Charsets.UTF_8)),
    )
}

fun decrypt(value: EncryptedValue): String {
    val cipher = Cipher.getInstance("AES/GCM/NoPadding")
    cipher.init(
        Cipher.DECRYPT_MODE,
        getOrCreateKey(),
        GCMParameterSpec(128, value.iv),
    )

    return cipher.doFinal(value.ciphertext).toString(Charsets.UTF_8)
}
```

Production code также требует versioned serialization, при необходимости authenticated associated data, atomic writes, size limits, background execution, mapping ошибок corruption и authentication, recovery после key invalidation и tests. Нельзя повторно использовать фиксированный IV или продолжать работу после ошибки проверки authentication tag.

## Hardware-backed keys

На поддерживаемых устройствах key material и операции могут находиться в Trusted Execution Environment или Secure Element. Это снижает риск extraction, но не переносит приложение и plaintext в secure hardware. Данные для encryption и plaintext после decryption по-прежнему доступны процессу приложения.

Нельзя определять hardware backing по модели устройства или API level. Проверяйте `KeyInfo`; в современных Android значение `securityLevel` различает software, trusted environment и StrongBox security levels. Attestation может дать более сильные удаленно проверяемые гарантии для специализированных систем, но требует backend verification и отдельной threat model.

Скомпрометированный код с полномочиями приложения всё равно может использовать hardware-backed key. Non-exportability ограничивает извлечение key material, но не доказывает легитимность каждой запрошенной операции.

## StrongBox на высоком уровне

StrongBox использует отдельный secure hardware component на поддерживаемых устройствах и может обеспечить более сильную изоляцию, чем обычный TEE. Он доступен не везде и может иметь ограничения algorithms, performance, throughput и storage. Запрашивайте StrongBox только тогда, когда threat model оправдывает стоимость совместимости и UX.

`setIsStrongBoxBacked(true)` может завершиться `StrongBoxUnavailableException`. Продукту нужен явный вариант поведения: fallback на обычный Keystore key, отключение чувствительной функции или отказ в поддержке устройства согласно требованиям. Молчаливое предположение не является стратегией.

## Шифрование локальных данных

Подходящий storage envelope зависит от формы данных:

- Небольшие значения можно сериализовать в versioned encrypted record.
- Файлы можно шифровать authenticated chunks или целиком, если позволяет размер.
- Room columns могут хранить ciphertext для отдельных чувствительных полей.
- Full-database encryption - отдельное архитектурное решение со своей моделью key, migration, queries и performance.
- Кешированные responses иногда безопаснее удалить и загрузить заново, чем переносить между версиями keys.

Android Keystore защищает ключи. Приложение отвечает за serialization, хранение IV, привязку записи, schema versions, key rotation, обработку corruption, atomic persistence, deletion и backup policy. Не создавайте собственный cryptographic container, если требованиям соответствует проверенный формат или библиотека.

## Ключи с аутентификацией пользователя и биометрической защитой

Keystore key может требовать недавнюю device authentication или authentication для каждого использования в зависимости от API level и configuration ключа. `BiometricPrompt` способен разрешить `CryptoObject` для auth-per-use key. Биометрия управляет доступом к ключу, но не является алгоритмом шифрования.

Такая политика меняет UX и recovery. Authentication можно отменить, может сработать lockout, device credentials могут измениться, biometric enrollment способен инвалидировать key при соответствующей настройке, а пользователь может удалить secure lock screen. До создания ключа решите, нужна ли invalidation и должно ли приложение повторно аутентифицироваться через backend, удалить локальные данные или предложить другой recovery path.

Не используйте biometric-bound key только ради показа prompt. Он оправдан, когда каждая криптографическая операция действительно требует локального присутствия пользователя. Тестируйте device-credential fallback и прерывания lifecycle.

## Хранение токенов

Короткоживущие access tokens часто можно держать в памяти, если UX допускает повторную authentication после process death. Refresh tokens живут дольше и обычно требуют Keystore-backed encrypted persistence, когда продукт обещает background session или восстановление сессии.

Это защищает от простого извлечения файлов и просмотра backup, но не от кражи token после decryption в скомпрометированном процессе. Необходимы backend expiration, rotation, reuse detection, revocation, audience restrictions, anomaly detection и authoritative authorization. Никогда не логируйте tokens и атомарно удаляйте весь локальный token set при logout или удалении account.

## Жизненный цикл хранилища

Storage design требует состояний и переходов, а не только `encrypt()` и `decrypt()`:

- создать или найти versioned key;
- атомарно записать ciphertext и metadata;
- прочитать, аутентифицировать и десериализовать;
- различать unavailable key, invalidated key, corrupt data и временный I/O failure;
- ротировать keys и мигрировать records;
- удалять данные и ключи при logout, account switch или завершении retention period;
- безопасно восстанавливаться после частичной migration или process death.

Rotation часто требует прочитать данные старым ключом и повторно зашифровать новым. Оба aliases нужно сохранять до успешного commit migration. Для re-fetchable data удаление и загрузка после authentication могут быть безопаснее сложной migration.

Account-specific records нельзя расшифровывать или повторно использовать для другого account. Когда это защищает от подмены records, добавляйте account и format context как authenticated associated data.

## Переустановка приложения и очистка данных

Очистка данных удаляет app-private files и должна рассматриваться как потеря Keystore entries приложения. Uninstall также удаляет app-specific Keystore credentials. Поэтому после uninstall/reinstall или clear-data продукт должен считать app-local encrypted state потерянным и восстанавливать его из авторитетного сервиса либо требовать новый sign-in.

Backup или device transfer могут восстановить ciphertext без исходного key. Такие данные намеренно невозможно расшифровать, поэтому их нужно обнаружить и удалить либо заменить, а не повторять попытку до постоянного crash. Не обещайте сохранение app-local encrypted state после reinstall без явно спроектированной и проверенной recovery architecture с новыми credentials или отдельно восстанавливаемыми keys.

## Backups и перенос на другое устройство

У Android backup и device-to-device transfer есть правила, зависящие от версии. Начиная с Android 12, `dataExtractionRules` отдельно управляет cloud и device-transfer scopes. Для более старых версий нужен отдельный файл правил `fullBackupContent`.

Например, проект для Android 12+ может исключить файл с encrypted credentials из обоих путей:

```xml
<data-extraction-rules>
    <cloud-backup>
        <exclude domain="file" path="auth/session.bin" />
    </cloud-backup>
    <device-transfer>
        <exclude domain="file" path="auth/session.bin" />
    </device-transfer>
</data-extraction-rules>
```

Применяйте rules к фактическому storage location и дополнительно настройте legacy backup rules для поддерживаемых Android 11 и ниже. Одного `allowBackup="false"` недостаточно как полной cross-version policy для device transfer.

Одни данные нужно переносить, для других нужен end-to-end protected backup, а третьи следует загрузить заново после authentication. Restore на новое устройство, recovery при missing key и старые storage versions должны тестироваться как продуктовые сценарии.

## Распространенные небезопасные подходы

Не помещайте конфиденциальные значения в source code, Git history, resources, manifest metadata, `BuildConfig`, native libraries, plain `SharedPreferences`, unencrypted files, logs, analytics или crash reports. Атакующий может исследовать APK или запущенное приложение независимо от языка и расширения файла.

- R8 и obfuscation увеличивают трудоемкость reverse engineering, но не создают secret storage.
- Base64 - обратимое encoding, а не encryption.
- Native library скрывает строку от простого поиска, но всё равно доставляет ее атакующему.
- Hardcoded API key может быть публичным identifier, защищенным server-side ограничениями package, signing, quota или API. Его нельзя считать confidential credential.
- Постоянный OAuth client secret внутри native application не является конфиденциальным.

Настоящие service credentials должны храниться на backend, который также контролирует authorization. Мобильный клиент должен получать только необходимые scoped и revocable capabilities.

## Jetpack Security и convenience APIs

Начиная с AndroidX Security Crypto 1.1.0, его crypto convenience APIs, включая `EncryptedSharedPreferences`, `EncryptedFile` и `MasterKey`, deprecated в пользу существующих platform APIs и прямой работы с Android Keystore. Не следует вводить их как современную storage architecture по умолчанию.

Существующим приложениям не нужна незапланированная разрушительная переделка. Сначала оцените threat model, backup exclusions, стоимость migration и поддержку библиотеки, затем спроектируйте versioned transition. Замена `EncryptedSharedPreferences` на plain preferences не является security migration, если конфиденциальность всё еще нужна.

Любой convenience wrapper или сторонняя библиотека оставляет приложению ответственность за key availability, invalidation, backups, corruption, schema migration и recovery. Сначала определите требования lifecycle, а затем выберите минимальную поддерживаемую реализацию.

## Выбор стратегии хранения

| Данные | Типичный срок жизни | Рекомендуемый подход |
| --- | --- | --- |
| Короткоживущий access token | Session или короткий | Память, если позволяет UX продукта |
| Refresh token | Более долгий | Keystore-backed encrypted persistence, если требуется восстановление |
| Нечувствительная настройка | Долгий | DataStore или обычные preferences |
| Чувствительный cache | Временный | Не сохранять либо шифровать с простым discard lifecycle |
| Повторно загружаемые backend data | Временный | Предпочесть удаление и повторную загрузку сложному recovery |
| Локальный секрет с user authentication | Зависит от продукта | Authentication-bound Keystore key с явным recovery path |

Это ориентиры, а не универсальная политика. Итоговое решение зависит от чувствительности данных, offline requirements, account model, поддерживаемых Android versions и ожиданий от recovery.

## Связанные темы

- [Основы безопасности Android](index.md)
- [OAuth 2.0, PKCE и управление токенами](oauth-pkce-token-management.md)
- [Хранение данных в Android](../android/storage.md)
