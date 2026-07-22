# HTTPS, TLS and Certificates

HTTPS is the standard transport-security foundation for Android applications communicating with remote services. This article will explain the certificate and platform trust decisions an Android engineer needs, while leaving cryptographic internals outside its scope.

## What HTTPS protects

**TODO:** Describe confidentiality, integrity, and server authentication, together with the boundaries of those guarantees.

## TLS handshake at a high level

**TODO:** Outline negotiation, certificate validation, and session-key establishment without a cryptography deep dive.

## Server certificates

**TODO:** Explain certificate identity, validity periods, and the server's responsibility to present appropriate certificates.

## Certificate authorities

**TODO:** Describe how trusted certificate authorities participate in server authentication.

## Certificate chains

**TODO:** Show how leaf, intermediate, and root certificates form a validation path.

## Hostname verification

**TODO:** Explain why a valid chain must also match the requested host.

## Android trust store

**TODO:** Cover platform trust anchors, OS-version differences, and application-specific trust decisions.

## OkHttp and platform TLS

**TODO:** Clarify how OkHttp normally relies on the platform TLS stack and safe defaults.

## Network Security Configuration

**TODO:** Reserve guidance for declarative trust settings, cleartext policy, and debug-only overrides.

## Debug certificates and local proxy tools

**TODO:** Explain safe debug trust configuration for inspection proxies without weakening release builds.

## Common unsafe implementations

**TODO:** Show why permissive custom `TrustManager` and `HostnameVerifier` implementations disable essential TLS validation.

## Related topics

- [Android Security Basics](index.md)
- [Certificate Pinning](certificate-pinning.md)
- [Retrofit / OkHttp](../networking/retrofit-okhttp.md)
- [Network Inspection](../tools/network-inspection.md)
