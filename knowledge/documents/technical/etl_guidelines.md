---
type: document
title: "Data Pipeline Guidelines"
description: "Validation, checkpoints, retries, and reconciliation"
tags: ['ETL', 'pipeline', 'data ingestion']---

# Data Pipeline Guidelines

Data pipelines should validate input shape, record rejected rows, and preserve enough metadata to explain how a result was produced. Use checkpoints for large jobs and make retries safe. Reconcile input and output counts and investigate unexpected drops. Do not silently convert malformed values into valid-looking defaults.
