---
type: document
title: "FAQ: Password and Secret Handling"
description: "How to protect credentials and API keys"
tags: ['FAQ', 'password', 'secrets']---

# FAQ: Password and Secret Handling

Never commit API keys, passwords, private keys, or access tokens to source control. Use environment variables for local development and an approved secrets manager in shared environments. Rotate exposed credentials promptly and check logs or repository history for accidental disclosure. A .env file should remain untracked.
