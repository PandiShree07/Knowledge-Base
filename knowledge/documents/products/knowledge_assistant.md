---
type: document
title: "Unified Knowledge Assistant Overview"
description: "How the assistant combines document evidence and database results"
tags: ['assistant', 'LangGraph', 'RAG', 'MySQL']---

# Unified Knowledge Assistant Overview

The Unified Knowledge Assistant routes a question to document retrieval, SQL retrieval, or both. Document answers are grounded in the bundled Markdown knowledge base. Structured counts and record questions should use the MySQL demo database. When a question requires both a rule and a record, the graph gathers both types of evidence before drafting the answer. If evidence is missing, the assistant should say so.
