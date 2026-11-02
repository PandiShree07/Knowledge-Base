---
type: document
title: "Access Control Standard"
description: "Least privilege, access reviews, and credential handling"
tags: ['access control', 'least privilege', 'IAM']---

# Access Control Standard

Grant access according to the least-privilege principle: each account receives only the permissions needed for its approved tasks. Use individual accounts, multi-factor authentication where available, and approved secrets management. Shared accounts should be avoided. Access should be reviewed periodically and removed promptly when roles change or access is no longer needed. Database applications should use a dedicated account with narrowly scoped privileges.
