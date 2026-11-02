---
type: document
title: "Backup and Recovery Standard"
description: "Backup frequency, restore tests, and recovery ownership"
tags: ['backup', 'recovery', 'disaster recovery']---

# Backup and Recovery Standard

Critical data should be backed up according to its recovery requirements and stored separately from the primary failure domain. Backup jobs must be monitored, and restore tests should verify that data can actually be recovered. Document recovery time and recovery point objectives for each important service. Encrypt backups containing sensitive information and restrict access to restore operations.
