# Certificate Pinning

Certificate pinning narrows which server identities an application accepts beyond standard platform trust. It can reduce specific trust-chain risks, but it also creates deployment, recovery, testing, and certificate-rotation obligations, so it is not a mandatory default for every Android application.

## What problem pinning tries to solve

**TODO:** Define the additional threat pinning addresses after normal TLS validation succeeds.

## Certificate pinning vs public-key pinning

**TODO:** Compare pin targets and their effect on certificate renewal and operational flexibility.

## OkHttp `CertificatePinner`

**TODO:** Reserve a focused Android example and explain host-pattern behavior.

## Backup pins

**TODO:** Explain why independently controlled backup pins are part of a resilient rollout plan.

## Certificate rotation

**TODO:** Outline overlap windows, application release timing, and coordination with server changes.

## Expiration and recovery strategy

**TODO:** Plan for expired, compromised, or incorrectly deployed pins without requiring an impossible emergency client update.

## Operational risks

**TODO:** Cover outages, stale application versions, third-party endpoints, and ownership of pin updates.

## Impact on QA and debugging proxies

**TODO:** Explain how pinning affects traffic inspection and how debug-only behavior can remain controlled.

## Testing pinning

**TODO:** Define positive, negative, backup-pin, rotation, and release-configuration test cases.

## When pinning is justified

**TODO:** Identify high-risk environments and explicit security requirements that may justify the operational cost.

## When standard TLS is sufficient

**TODO:** Explain why correct platform TLS validation is the appropriate baseline for many applications.

## Related topics

- [HTTPS, TLS and Certificates](https-tls-certificates.md)
- [Android Security Basics](index.md)
- [Retrofit / OkHttp](../networking/retrofit-okhttp.md)
- [Network Inspection](../tools/network-inspection.md)
