---
type: document
title: "Database Access Safety"
description: "Read-only query accounts, parameterization, and least privilege"
tags: ['database', 'SQL', 'read only']---

# Database Access Safety

Applications that only need to answer questions should use database accounts with SELECT privileges only. Never connect an AI-generated query to a production database using an administrator account. Validate generated SQL, restrict result sizes, set sensible timeouts, and log the question and query metadata without logging secrets. SQL text checks alone are not a security boundary; database permissions are essential.
