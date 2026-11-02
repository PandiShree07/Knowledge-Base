---
type: document
title: "Background Job Guidelines"
description: "Retries, idempotency, timeouts, and queue visibility"
tags: ['background jobs', 'Celery', 'retry']---

# Background Job Guidelines

Background jobs should be idempotent where possible, have bounded retries, and use explicit timeouts. Retry transient failures with backoff and avoid retrying permanent validation errors indefinitely. Track job state and failure reasons so operators can distinguish a slow job from a failed one. Use unique task identifiers to avoid duplicate side effects.
