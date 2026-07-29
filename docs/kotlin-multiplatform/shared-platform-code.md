# Shared vs Platform-Specific Code

This article will examine which responsibilities are usually valuable to share and which commonly remain platform-specific in a Kotlin Multiplatform system. It will emphasize deliberate platform boundaries, integration abstractions, and the costs of trying to share every implementation detail.

> **Draft:** This article is a structured placeholder and will be expanded in a follow-up task.

## Topics to cover

- Code that is safe and valuable to share
- Responsibilities that commonly remain platform-specific
- Explicit platform boundaries
- `expect` and `actual`
- Interfaces, adapters, and dependency injection
- Avoiding the "share everything" trap
