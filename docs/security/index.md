# Android Security Basics

Android application security is the practice of protecting user data, sessions, and privileged operations while accepting that the client runs on a device outside the application's control. The goal is not to make reverse engineering impossible. It is to define realistic trust boundaries, reduce exposure, raise attacker cost, and keep authoritative decisions in systems that can enforce them.

## Security model and threat boundaries

An **asset** is anything whose disclosure, modification, or unavailability would cause harm. In an Android application, typical assets include user sessions, personal or financial data, local files, business records, API operations, and the integrity of transactions initiated from the device.

The important trust boundaries are between:

- the application process and other applications;
- the application and the Android operating system;
- the device and the network;
- the mobile client and backend services;
- first-party code and third-party SDKs or services.

Threats have different capabilities. Accidental logging is not the same problem as a malicious application abusing an exported component. A compromised Wi-Fi network can inspect or alter unprotected traffic, while a rooted device, debugger, hook, emulator, or runtime instrumentation can observe behavior inside the application. A modified APK may remove client-side checks entirely.

The required defenses depend on data sensitivity, business impact, regulatory obligations, attacker motivation, supported devices, and acceptable operational cost. A public content reader and a banking application do not need identical controls. A useful threat model names the assets and credible attackers before selecting mechanisms.

## Sensitive data

Sensitive data includes more than passwords. Common examples are:

- access and refresh tokens, session cookies, and authorization codes;
- personal, health, location, and financial data;
- encryption and signing keys;
- cached backend responses and local documents;
- internal identifiers, feature flags, and diagnostic data;
- logs, analytics events, screenshots, and crash reports containing user context.

Not every identifier is a secret. A public client ID or record identifier may be visible by design, but it can still be private, enable correlation, or help an attacker enumerate resources. Classify data by the consequence of disclosure or modification rather than by its name.

Retain only what the product actually needs, for only as long as it needs it. Data that is never collected or persisted cannot leak from local storage or backup.

## Data in transit vs data at rest

**Data in transit** moves between the client and a remote service. HTTPS with correct TLS validation protects the confidentiality and integrity of requests and responses on the network and authenticates the server.

**Data at rest** is persisted in files, databases, preferences, caches, and backups. It needs a separate storage and lifecycle policy. TLS stops protecting a response as soon as the application receives it and decides to store, log, display, or share it.

**Data in use** exists in process memory while code works with it. Even encrypted local data must become plaintext somewhere to be useful. On a compromised runtime, instrumentation may observe plaintext or invoke operations that use a non-exportable key. Local encryption still raises the cost of offline extraction, but it is not isolation from a process-level attacker.

## The Android client is not a trusted environment

An APK can be downloaded and inspected. Resources, manifest metadata, native libraries, constants, URLs, and `BuildConfig` values can be extracted. Obfuscation can slow analysis and reduce useful names, but it is not encryption and does not turn an embedded value into a secret.

Android sandboxing, app signing, permissions, verified boot, and hardware-backed keys provide meaningful protection. They isolate ordinary applications and make many attacks harder. They do not make the client equivalent to a trusted backend: on a compromised device, runtime memory and behavior may be observed or changed, and a repackaged client may omit local validation.

> The application may enforce UX rules locally, but the backend must enforce security-sensitive authorization and business rules.

For example, hiding an admin button is useful UI behavior, not an authorization boundary. Every protected API operation must verify the authenticated subject, permission, resource ownership, and business constraints on the server.

## Common Android security risks

- **Hardcoded secrets:** credentials in source code, resources, `BuildConfig`, manifest metadata, or native code remain extractable from the distributed application.
- **Sensitive logs:** request headers, tokens, personal data, and decrypted payloads may reach Logcat, analytics, or crash reporting systems.
- **Insecure persistence and backups:** plain preferences, files, database rows, or backup rules may expose long-lived credentials and cached data.
- **Exported components and unsafe intents:** an activity, service, receiver, or provider with an overly broad intent filter, permission, or validation policy may be invoked by another application.
- **WebView misuse:** loading untrusted content with powerful settings or exposing a JavaScript bridge without a narrow trust model can cross application and web trust boundaries.
- **Cleartext or broken TLS:** HTTP, an accept-all `TrustManager`, or a permissive `HostnameVerifier` removes transport protection or server authentication.
- **Dependency risk:** outdated libraries and unnecessary SDKs increase attack surface and may collect or expose more data than expected.
- **Excessive retention:** old caches, abandoned account data, clipboard contents, and screenshots may outlive their legitimate purpose.

Sensitive screens may justify controls such as `FLAG_SECURE`, but it affects usability and does not prevent every capture method. Clipboard use should be minimized for credentials because other surfaces and user workflows can expose copied values.

## Defense in depth

Defense in depth combines independent layers so that one failure does not become total compromise:

- backend authorization remains authoritative;
- TLS provides the normal secure transport baseline;
- platform configuration limits exported surfaces, cleartext traffic, and permissions;
- Android Keystore-backed encryption protects selected local data from simple offline extraction;
- short-lived credentials, rotation, and revocation reduce exposure time;
- least privilege limits component, account, SDK, and backend access;
- dependency maintenance reduces known vulnerabilities;
- observability supports detection without recording sensitive payloads;
- release signing and variant separation keep debug behavior out of production;
- tests, threat reviews, and incident runbooks validate both code and recovery paths.

No item makes the application secure by itself. The layers must match a concrete threat model and have owners who can maintain them.

## Security review checklist

Use this list during design or pull-request review. It helps find common gaps but does not replace a professional security assessment for high-risk systems.

**Data**

- Which assets and personal data are processed, and how long are they retained?
- Can collection, persistence, screenshots, clipboard use, or backup be avoided?

**Network and storage**

- Is HTTPS required, cleartext disabled, and platform certificate validation unchanged?
- Are sensitive persisted values encrypted with a defined key, backup, migration, and recovery lifecycle?

**Authentication and authorization**

- Does the backend authorize every protected operation and resource?
- Are tokens short-lived where possible, stored deliberately, refreshed once, revoked when supported, and removed on logout?

**Android surfaces**

- Are exported components, permissions, deep links, pending intents, and incoming extras explicitly constrained and validated?
- Does WebView load only intended content with the minimum required capabilities and no unjustified JavaScript bridge?

**Diagnostics and release**

- Are logs, analytics, crash reports, and network inspectors redacting credentials and personal data?
- Are debug CAs, test endpoints, debuggable flags, and diagnostic menus absent or controlled in release builds?

**Maintenance and recovery**

- Are dependencies current, necessary, and reviewed for data collection and exposed components?
- What happens after key invalidation, corrupt storage, token refresh denial, certificate rotation, app reinstall, or account switch?

## Related topics

- [HTTPS, TLS and Certificates](https-tls-certificates.md)
- [Certificate Pinning](certificate-pinning.md)
- [Android Keystore and Secure Storage](keystore-secure-storage.md)
- [OAuth 2.0, PKCE and Token Management](oauth-pkce-token-management.md)
- [Networking](../networking/index.md)
- [Logging and Diagnostic Data](../tools/logging-diagnostics.md)
