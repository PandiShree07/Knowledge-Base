---
type: document
title: "FAQ: Leave Balance"
description: "How to answer employee leave balance questions"
tags: ['FAQ', 'leave balance', 'SQL']---

# FAQ: Leave Balance

To answer an individual leave balance question, first clarify the applicable leave type and entitlement period if needed. Count only records whose status is approved. Pending requests are not approved usage. This demo schema contains leave records but does not store a full authoritative entitlement ledger, so do not calculate an official remaining balance unless an entitlement source is available.
