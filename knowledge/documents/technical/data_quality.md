---
type: document
title: "Data Quality Standard"
description: "Completeness, consistency, freshness, and reconciliation"
tags: ['data quality', 'validation', 'reconciliation']---

# Data Quality Standard

Data quality checks should cover required fields, valid value ranges, duplicate identifiers, referential integrity, freshness, and unexpected count changes. Define the expected grain of each table and avoid comparing counts that measure different things. Investigate anomalies before deleting or rewriting records. Keep a clear audit trail for corrections.
