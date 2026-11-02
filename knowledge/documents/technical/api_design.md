---
type: document
title: "API Design Guidelines"
description: "REST resources, validation, errors, and pagination"
tags: ['API', 'REST', 'backend']---

# API Design Guidelines

APIs should use predictable resource names, explicit request validation, consistent response structures, and appropriate HTTP status codes. List endpoints should support pagination and bounded result sizes. Errors should be useful to callers without exposing secrets, internal stack traces, or sensitive database details. Authentication and authorization must be enforced server-side.
