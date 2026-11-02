---
type: document
title: "Deployment Checklist"
description: "Configuration, migrations, health checks, and rollback"
tags: ['deployment', 'release', 'operations']---

# Deployment Checklist

Before release, verify configuration, dependency versions, tests, database migrations, secrets, health checks, and rollback steps. Prefer small, reversible changes. Do not run destructive seed or migration scripts against production without a reviewed plan and backup. After deployment, monitor errors and critical business workflows.
