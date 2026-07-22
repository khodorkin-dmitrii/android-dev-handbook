# Android Keystore and Secure Storage

Secure local storage starts with a data-lifecycle decision, not an encryption API. Android Keystore can make cryptographic keys difficult to extract, while the application remains responsible for deciding what to retain, encrypting it correctly, storing ciphertext and metadata, and recovering when keys or data are unavailable.

## Start with a storage decision

Before persisting sensitive data, answer:

- Must it be stored at all, and for how long?
- Must it survive process death, logout, account switch, or device migration?
- Should every use require recent device or biometric authentication?
- Can the data be fetched again after sign-in?
- What should happen after key invalidation, backup restore, or corruption?

> The safest sensitive data is data the application does not retain.

Prefer short retention and re-fetching for disposable server data. Encryption is appropriate when persistence has real product value, not as a reason to keep every response indefinitely.

## Android Keystore

Android Keystore stores cryptographic keys or non-exportable handles to them. Application code requests cryptographic operations through standard Java Cryptography Architecture APIs, while key material remains outside the application process and may be bound to secure hardware. Keystore is not a general encrypted database: application data is normally stored separately as ciphertext.

The following API 23+ helper creates or retrieves an AES key restricted to AES-GCM encryption and decryption:

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

Algorithms, key sizes, authentication options, and hardware properties vary by Android version and device. Check required capabilities and keep a product-level fallback or unsupported-device policy.

## Key material vs encrypted application data

The common envelope is:

1. Create or retrieve a Keystore-backed key.
2. Encrypt serialized application data with authenticated encryption.
3. Persist ciphertext plus non-secret metadata such as IV and format version.
4. Retrieve the key handle and decrypt when the data is needed.

Ciphertext and IV do not need to be secret like the key, but they must be stored without accidental truncation or mixing between records. For GCM, an IV must never repeat with the same key. The authentication tag, included in the Java cipher output, detects modification; encryption without integrity is not sufficient for most application data.

This compact example lets the provider generate a fresh IV for every encryption:

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

Production code still needs versioned serialization, optional authenticated associated data, atomic writes, size limits, background execution, corruption and authentication-error mapping, key invalidation recovery, and tests. Never reuse a fixed IV or continue after authentication-tag verification fails.

## Hardware-backed keys

On supported devices, key material and key operations can reside in a Trusted Execution Environment or Secure Element. This reduces extraction risk, but does not move the application or its plaintext into secure hardware. Data supplied for encryption and plaintext returned after decryption are still available to the application process.

Do not infer hardware backing from device model or API level. Inspect `KeyInfo`; on modern Android, `securityLevel` distinguishes software, trusted environment, and StrongBox security levels. Attestation may provide stronger remotely verifiable claims for specialized systems, but it requires backend verification and a separate threat model.

Hardware-backed keys can still be used by compromised code running with the application's authority. Non-exportability limits where the key material can go; it does not prove that every requested operation is legitimate.

## StrongBox at a high level

StrongBox uses a dedicated secure hardware component on supported devices and can offer stronger isolation than a general TEE. It is not universal and may have algorithm, performance, throughput, or storage limitations. Request it only when the threat model justifies the compatibility and UX cost.

`setIsStrongBoxBacked(true)` may fail with `StrongBoxUnavailableException`. A product needs an explicit response: fall back to a normal Keystore key, disable the sensitive capability, or reject the device according to requirements. Silent assumptions are not a strategy.

## Encrypting local data

The appropriate storage envelope depends on data shape:

- Small values can be serialized into a versioned encrypted record.
- Files can be encrypted as authenticated chunks or as a whole when size permits.
- Room columns can hold ciphertext when only selected fields are sensitive.
- Full-database encryption is a separate architectural choice with its own key, migration, query, and performance model.
- Cached responses may be safer to delete and re-fetch than to migrate across key versions.

Android Keystore protects keys. The application owns serialization, IV storage, record association, schema versions, key rotation, corruption behavior, atomic persistence, deletion, and backup policy. Do not design a custom cryptographic container when a reviewed format or library already fits the requirement.

## User-authenticated and biometric-protected keys

A Keystore key can require recent device authentication or authentication for every use, depending on API level and key configuration. `BiometricPrompt` can authorize a `CryptoObject` for an auth-per-use key. Biometrics are a gate to using the key, not the encryption algorithm itself.

This policy changes UX and recovery. Authentication can be canceled or locked out; device credentials can change; biometric enrollment may invalidate a key when configured that way; and the user may remove the secure lock screen. Decide before key creation whether invalidation is desired and whether the application should re-authenticate with the backend, discard local data, or provide another recovery route.

Do not use a biometric-bound key merely to show a prompt. Use it when each cryptographic operation genuinely needs local user presence, and test device-credential fallback and lifecycle interruption.

## Token storage

Short-lived access tokens can often remain in memory if the desired session UX permits re-authentication after process death. Refresh tokens live longer and usually justify Keystore-backed encrypted persistence when background or restored sessions are required.

This protects against simple file extraction and backup inspection. It does not protect a token after decryption in a compromised process. Backend expiration, rotation, reuse detection, revocation, audience restrictions, anomaly detection, and authoritative authorization remain necessary. Never log tokens, and delete the complete local token set atomically on logout or account removal.

## Storage lifecycle

A storage design needs states and transitions, not just `encrypt()` and `decrypt()`:

- create or look up a versioned key;
- write ciphertext and metadata atomically;
- read, authenticate, and deserialize;
- distinguish unavailable keys, invalidated keys, corrupt data, and temporary I/O failures;
- rotate keys and migrate records;
- delete data and keys on logout, account switch, or retention expiry;
- recover safely after partial migration or process death.

Rotation often means reading with the old key and re-encrypting with the new key. Keep both aliases until migration commits successfully. For re-fetchable data, deletion and download after authentication may be safer than complex migration.

Account-specific records must not be decrypted or reused for another account. Include account and format context as authenticated associated data when it materially prevents record substitution.

## App reinstall and data clearing

Clearing application data removes app-private files and should be treated as loss of the application's Keystore entries. Uninstalling also removes app-specific Keystore credentials. Product logic should therefore treat uninstall/reinstall or clear-data as loss of app-local encrypted state and require restoration from an authoritative service or a new sign-in.

Backup or device transfer can restore ciphertext without the original key. Such data is intentionally undecryptable and must be detected and discarded or replaced, not retried until the application crashes. Do not promise that app-local encrypted state survives reinstall unless an explicit, tested recovery architecture provides new credentials or separately recoverable keys.

## Backup and device migration considerations

Android backup and device-to-device transfer have version-dependent rules. For Android 12 and later, `dataExtractionRules` controls cloud and device-transfer scopes separately. Earlier versions require a separate `fullBackupContent` rules file.

For example, an Android 12+ project can exclude a file containing encrypted credentials from both paths:

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

Apply rules to the actual storage location and also configure legacy backup rules for supported Android 11 and lower devices. `allowBackup="false"` alone is not a complete cross-version device-transfer policy.

Some data should migrate, some should require end-to-end protected backup, and some should be re-fetched after authentication. Test restore onto a new device, missing-key recovery, and old storage versions as product flows.

## Common insecure approaches

Do not place confidential values in source code, Git history, resources, manifest metadata, `BuildConfig`, native libraries, plain `SharedPreferences`, unencrypted files, logs, analytics, or crash reports. An attacker can inspect the APK or the running application regardless of language or file extension.

- R8 and obfuscation increase reverse-engineering effort but do not create secret storage.
- Base64 is reversible encoding, not encryption.
- A native library hides a string from casual search but still ships it to the attacker.
- A hardcoded API key may be a public identifier protected by server-side package, signing, quota, or API restrictions. It must not be treated as a confidential credential.
- A permanent OAuth client secret embedded in a native application is not confidential.

Use the backend to hold true service credentials and enforce authorization. Give the mobile client only the scoped, revocable capabilities it needs.

## Jetpack Security and convenience APIs

As of AndroidX Security Crypto 1.1.0, its crypto convenience APIs, including `EncryptedSharedPreferences`, `EncryptedFile`, and `MasterKey`, are deprecated in favor of existing platform APIs and direct Android Keystore use. Do not introduce them as the default modern storage architecture.

Existing applications do not need an unplanned destructive rewrite. Assess their threat model, backup exclusions, migration cost, and library support, then design a versioned transition if needed. Replacing `EncryptedSharedPreferences` with plain preferences is not a security migration when confidentiality is still required.

Any convenience wrapper or third-party library still leaves the application responsible for key availability, invalidation, backups, corruption, schema migration, and recovery. Start with these lifecycle requirements, then select the smallest maintained implementation that meets them.

## Choosing a storage strategy

| Data | Typical lifetime | Suggested approach |
| --- | --- | --- |
| Short-lived access token | Session or short | Memory where product UX permits |
| Refresh token | Longer-lived | Keystore-backed encrypted persistence when restoration is required |
| Non-sensitive preference | Long | DataStore or ordinary preferences |
| Sensitive cache | Temporary | Avoid persistence or encrypt with a discardable lifecycle |
| Re-fetchable backend data | Temporary | Prefer deletion and re-fetch over complex recovery |
| User-authenticated local secret | Product-specific | Authentication-bound Keystore key with an explicit recovery path |

This is guidance, not a universal policy. Data sensitivity, offline requirements, account model, supported Android versions, and recovery expectations determine the final design.

## Related topics

- [Android Security Basics](index.md)
- [OAuth 2.0, PKCE and Token Management](oauth-pkce-token-management.md)
- [Android Storage](../android/storage.md)
