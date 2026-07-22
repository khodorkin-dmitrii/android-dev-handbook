# Android Keystore and Secure Storage

Secure local storage begins with deciding what data must persist and which keys should protect it. This article will center on Android Keystore and the underlying storage architecture rather than tying the design to a single convenience API that may evolve over time.

## Android Keystore

**TODO:** Explain non-exportable key storage, supported key operations, and relevant platform constraints.

## Key material vs encrypted application data

**TODO:** Separate protection of cryptographic keys from encryption and persistence of application data.

## Hardware-backed keys

**TODO:** Describe hardware-backed isolation, capability checks, and realistic guarantees across devices.

## StrongBox at a high level

**TODO:** Explain when StrongBox may add isolation and what availability and performance trade-offs it introduces.

## Encrypting local data

**TODO:** Outline authenticated encryption, key selection, metadata, and storage responsibilities.

## User-authenticated and biometric-protected keys

**TODO:** Cover authentication-bound key use, invalidation, UX, and recovery implications.

## Token storage

**TODO:** Connect token sensitivity and lifetime to an appropriate storage strategy.

## Storage lifecycle

**TODO:** Define creation, access, rotation, invalidation, and deletion of keys and encrypted data.

## App reinstall and data clearing

**TODO:** Explain the loss of application data and keys and its effect on recoverability.

## Backup and device migration considerations

**TODO:** Address backups, restore onto another device, key availability, and exclusion policy.

## Common insecure approaches

**TODO:** Explain why secrets do not belong in source code, resources, `BuildConfig`, plain `SharedPreferences`, or logs.

## Choosing a storage strategy

**TODO:** Provide a decision framework based on data sensitivity, lifetime, offline needs, user authentication, and recovery.

## Related topics

- [Android Security Basics](index.md)
- [OAuth 2.0, PKCE and Token Management](oauth-pkce-token-management.md)
- [Android Storage](../android/storage.md)
