# OAuth 2.0, PKCE and Token Management

Native Android applications need an authorization flow designed for public clients that cannot safely hold a client secret. This article will focus on Authorization Code Flow with PKCE and the Android session lifecycle without attempting to cover the entire OAuth or OpenID Connect specifications.

## OAuth 2.0 and OpenID Connect

**TODO:** Distinguish delegated authorization from authentication and identity information at an Android-relevant level.

## Native application authorization model

**TODO:** Explain public clients, redirect handling, external authorization services, and client-secret limitations.

## Authorization Code Flow with PKCE

**TODO:** Outline authorization code exchange, code verifier and challenge, state, nonce, and redirect validation.

## Browser-based authentication

**TODO:** Cover system-browser or Custom Tabs flows, shared authentication state, and secure return to the application.

## Why embedded WebView login is usually inappropriate

**TODO:** Reserve guidance on credential exposure, provider policy, session isolation, and missing browser security context.

## Access tokens

**TODO:** Define their purpose, audience, scope, and short lifetime from the mobile client's perspective.

## Refresh tokens

**TODO:** Cover their higher sensitivity, rotation, reuse detection, and server-policy dependencies.

## Token expiration

**TODO:** Explain proactive and reactive expiration handling, clock skew, and failure boundaries.

## Secure token storage

**TODO:** Connect token lifetime and sensitivity to Android Keystore-backed storage architecture.

## Adding authorization to requests

**TODO:** Reserve the request-header integration point without duplicating general interceptor design.

## Refreshing tokens

**TODO:** Outline refresh coordination, atomic session updates, retries, and terminal failure handling.

## Concurrent requests and single-flight refresh

**TODO:** Explain how one refresh operation can serve multiple failed requests without races or refresh storms.

## OkHttp interceptor vs authenticator

**TODO:** Compare responsibilities and reserve a future link to a dedicated Networking article about OkHttp interceptors.

## Handling `401 Unauthorized`

**TODO:** Distinguish expired credentials from revoked sessions, insufficient authorization, and non-retriable failures.

## Logout and token revocation

**TODO:** Cover local session clearing, server-side revocation when supported, and browser-session expectations.

## Process death and session restoration

**TODO:** Define the minimal persisted state and a safe restoration path after Android recreates the process.

## JWT limitations

**TODO:** Explain why token shape does not replace validation, revocation strategy, secure storage, or server-side authorization.

## Common implementation mistakes

**TODO:** Collect Android-specific mistakes involving embedded credentials, redirects, storage, refresh races, logging, and retry loops.

## Related topics

- [Android Keystore and Secure Storage](keystore-secure-storage.md)
- [Android Security Basics](index.md)
- [HTTPS, TLS and Certificates](https-tls-certificates.md)
- [Retrofit / OkHttp](../networking/retrofit-okhttp.md)

<!-- TODO: Link to the dedicated OkHttp Interceptors article when it exists in the Networking domain. -->
