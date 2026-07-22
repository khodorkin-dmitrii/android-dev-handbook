# HTTPS, TLS and Certificates

HTTPS is the standard transport-security foundation for Android applications communicating with remote services. Android and OkHttp already provide safe TLS defaults for normal public HTTPS endpoints. Application code should usually configure policy around those defaults, not replace certificate validation with custom networking code.

## What HTTPS protects

Correctly validated HTTPS provides three central properties:

- **Confidentiality:** intermediaries cannot normally read application payloads.
- **Integrity:** modification of protected traffic is detected.
- **Server authentication:** the client verifies that the certificate chain is trusted and valid for the requested hostname.

HTTPS does not prove that the backend behaves correctly, authorize a user for an operation, or protect a response after the application stores or logs it. Malware or instrumentation inside a compromised device may observe plaintext in the process. TLS also does not hide all metadata: observers can still learn facts such as destination IP addresses, timing, and traffic volume, and hostname visibility depends on the negotiated protocol and infrastructure.

## TLS handshake at a high level

A simplified connection looks like this:

1. The client connects to the server.
2. Client and server negotiate supported TLS parameters.
3. The server presents its certificate chain.
4. The client validates the chain, certificate properties, and hostname.
5. Both sides establish session keys.
6. Encrypted application traffic begins.

Modern TLS configurations normally use ephemeral key agreement and provide forward secrecy, so later compromise of a long-term server key does not automatically decrypt previously recorded sessions. The practical Android concern is to keep the platform TLS stack updated and correctly configured, not to implement handshake cryptography.

## Server certificates

An X.509 server certificate binds a public key to identities and includes an issuer, validity period, extensions, and a CA signature. DNS identities are carried in the Subject Alternative Name extension. The requested host must appear there according to hostname-matching rules; the legacy subject common name is not a substitute for a correct SAN configuration.

A certificate being within its validity period is not enough. Its signature and usage must be valid, its chain must reach an accepted trust anchor, it must match the hostname, and relevant revocation or platform policy checks must succeed. The server also needs to present the leaf certificate and required intermediate certificates in the correct order.

## Certificate authorities

A certificate authority signs certificates under a public-key infrastructure. Android's accepted root CA certificates are **trust anchors**. Trusting a root means accepting valid chains issued beneath it within platform and certificate constraints, not trusting every server operated by that organization.

Publicly trusted CAs support ordinary Internet endpoints. Private enterprise or development CAs may be appropriate for controlled environments, but adding one expands the set of identities that can authenticate servers to the application and therefore expands the trust boundary.

## Certificate chains

Servers usually present a leaf certificate plus one or more intermediates:

```text
Trusted root CA
    -> Intermediate CA
        -> api.example.com
```

The root is normally already in the client trust store and is not sent by the server. The client builds and validates a path from the leaf to an accepted root. A missing intermediate can break Android clients even when a desktop browser appears to work because browsers may have cached or fetched the missing certificate. Server-chain deployment must therefore be tested independently.

## Hostname verification

Chain validation and hostname verification answer different questions:

- Is this certificate chain anchored in a trusted CA and otherwise valid?
- Is the leaf certificate valid for the exact server the client requested?

A certificate valid only for `files.example.net` must be rejected when connecting to `api.example.com`, even if both use the same trusted CA. Disabling hostname verification allows any otherwise trusted certificate to impersonate the requested endpoint.

## Android trust store

By default, Android networking stacks use platform trust anchors. Available roots and TLS capabilities can vary by Android version, security update, and device, so server compatibility should be tested across the supported matrix.

Application trust can be customized declaratively with Network Security Configuration. Whether user-installed CAs are accepted depends on the application's target behavior and configuration, so do not assume one rule for every OS version. Explicitly adding system, user, or bundled CAs changes the trust boundary. Prefer the system store for public production services and add private trust anchors only for a documented requirement.

## OkHttp and platform TLS

A normal OkHttp client needs no custom TLS objects:

```kotlin
val client = OkHttpClient.Builder()
    .build()
```

OkHttp delegates certificate-chain and hostname validation to the platform integration and applies its safe defaults. Developers should generally not implement or replace `X509TrustManager`, `SSLSocketFactory`, or `HostnameVerifier`. Specialized private PKI requirements should first use Network Security Configuration where possible and receive expert review.

## Network Security Configuration

Reference the configuration from the manifest:

```xml
<application
    android:networkSecurityConfig="@xml/network_security_config"
    android:usesCleartextTraffic="false"
    ... />
```

The following production baseline disables cleartext. The debug override adds user-installed CAs only while `android:debuggable` is true, which supports a deliberately configured inspection proxy without changing release trust:

```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <base-config cleartextTrafficPermitted="false" />

    <debug-overrides>
        <trust-anchors>
            <certificates src="user" />
        </trust-anchors>
    </debug-overrides>
</network-security-config>
```

`android:usesCleartextTraffic="false"` expresses the application-wide policy, while `cleartextTrafficPermitted` can define declarative base or domain-specific rules for networking stacks that honor the configuration. If a legacy host truly requires HTTP, scope the exception to that domain and plan its removal. Never put a local proxy CA into production trust anchors.

## Debug certificates and local proxy tools

Charles, Proxyman, mitmproxy, and similar tools terminate the device's TLS connection and present a certificate issued by a locally installed proxy CA. Inspection works only when the debug application trusts that CA. Release builds should keep normal production trust and should be tested separately.

Certificate pinning adds another check and may still reject a proxy connection. If a project needs inspection of pinned endpoints, use explicit build-variant separation controlled by the team. Do not add a runtime switch or global bypass that can reach production.

## Common unsafe implementations

**Intentionally unsafe - never use this in an application:**

```kotlin
val unsafeHostnameVerifier = HostnameVerifier { _, _ -> true }
```

This accepts a trusted certificate for the wrong hostname. A custom trust manager whose checks return successfully for every chain is equally dangerous. Either change removes the server-authentication property of TLS and permits a man-in-the-middle with an arbitrary or unrelated certificate to impersonate the service.

Suppressing TLS errors is not a temporary fix. Correct the server chain, hostname, device clock, trust configuration, or controlled development CA instead. Do not publish a reusable accept-all trust manager, even in sample or test utility code that may be copied into release sources.

## Practical review guidance

- Use HTTPS for every sensitive endpoint and disable cleartext by default.
- Keep platform certificate and hostname validation unchanged.
- Prefer declarative trust configuration to custom TLS code.
- Isolate proxy CAs and other test trust to debuggable builds.
- Test supported Android versions, hostnames, redirect paths, and server-chain deployment.
- Monitor certificate renewal and intermediate-chain changes before production rollout.

**Key idea:** TLS is the normal secure transport boundary. Custom validation expands or removes that boundary and therefore needs a concrete requirement, careful testing, and explicit ownership.

## Related topics

- [Android Security Basics](index.md)
- [Certificate Pinning](certificate-pinning.md)
- [Retrofit / OkHttp](../networking/retrofit-okhttp.md)
- [Network Inspection](../tools/network-inspection.md)
